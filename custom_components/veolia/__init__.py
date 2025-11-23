"""
Custom integration to integrate Veolia with Home Assistant.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import logging

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
    statistics_during_period,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.core_config import Config
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .VeoliaClient import VeoliaClient
from .const import CONF_ABO_ID, CONF_PASSWORD, CONF_USERNAME, DAILY, DOMAIN, HISTORY, PLATFORMS
from .debug import decoratorexceptionDebug

SCAN_INTERVAL = timedelta(hours=10)

_LOGGER = logging.getLogger(__name__)

STATISTIC_ID = f"{DOMAIN}:water_consumption"


@decoratorexceptionDebug
async def async_setup(hass: HomeAssistant, config: Config):
    """Set up this integration using YAML is not supported."""
    return True


@decoratorexceptionDebug
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})

    username = entry.data.get(CONF_USERNAME)
    password = entry.data.get(CONF_PASSWORD)
    abo_id = entry.data.get(CONF_ABO_ID)
    # _LOGGER.debug(f"abo_id={abo_id}")
    session = async_get_clientsession(hass)
    client = VeoliaClient(username, password, session, abo_id)
    coordinator = VeoliaDataUpdateCoordinator(hass, client=client, entry=entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


class VeoliaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass: HomeAssistant, client: VeoliaClient, entry: ConfigEntry) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []
        self.entry = entry

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            consumption = await self.hass.async_add_executor_job(self.api.update_all)
            _LOGGER.debug(f"consumption = {consumption}")

            # Inject historical statistics for the energy dashboard
            await self._async_insert_statistics(consumption)

            return consumption

        except Exception as exception:
            raise UpdateFailed() from exception

    async def _async_insert_statistics(self, consumption: dict):
        """Insert historical statistics for the energy dashboard."""
        if DAILY not in consumption or HISTORY not in consumption[DAILY]:
            _LOGGER.warning("No daily consumption data to insert into statistics")
            return

        history = consumption[DAILY][HISTORY]
        if not history:
            return

        # Get existing statistics to calculate cumulative sum
        statistic_id = f"{DOMAIN}:water_consumption_{self.entry.entry_id}"

        # Metadata for the statistic
        # mean_type: 0=no mean, 1=arithmetic mean, 2=circular mean
        metadata = StatisticMetaData(
            mean_type=0,
            has_sum=True,
            name="Veolia Water Consumption",
            source=DOMAIN,
            statistic_id=statistic_id,
            unit_of_measurement=UnitOfVolume.LITERS,
        )

        # Sort history by date ascending for cumulative calculation
        sorted_history = sorted(history, key=lambda x: x[0])

        # Get the last recorded statistic to continue the cumulative sum
        last_stats = await get_instance(self.hass).async_add_executor_job(
            get_last_statistics, self.hass, 1, statistic_id, True, {"sum"}
        )

        if last_stats and statistic_id in last_stats:
            last_sum = last_stats[statistic_id][0].get("sum", 0) or 0
            last_date = datetime.fromtimestamp(
                last_stats[statistic_id][0]["start"], tz=timezone.utc
            ).date()
        else:
            last_sum = 0
            last_date = None

        # Build statistics data
        statistics_data = []
        cumulative_sum = last_sum

        for date_val, liters in sorted_history:
            # Skip dates we already have
            if last_date and date_val <= last_date:
                continue

            cumulative_sum += liters

            # Create timestamp at start of day in UTC
            start_time = datetime.combine(date_val, datetime.min.time(), tzinfo=timezone.utc)

            statistics_data.append(
                StatisticData(
                    start=start_time,
                    sum=cumulative_sum,
                    state=liters,
                )
            )

        if statistics_data:
            _LOGGER.debug(f"Inserting {len(statistics_data)} statistics for {statistic_id}")
            async_add_external_statistics(self.hass, metadata, statistics_data)
        else:
            _LOGGER.debug("No new statistics to insert")


@decoratorexceptionDebug
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


@decoratorexceptionDebug
async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
