import asyncio
from functools import wraps
import logging

_LOGGER = logging.getLogger(__name__)


def decoratorexceptionDebug(f):
    @wraps(f)
    async def async_wrapper(*args, **kwargs):
        try:
            _LOGGER.debug(f"Start async function {f.__name__}")
            result = await f(*args, **kwargs)
            _LOGGER.debug(f"End async function {f.__name__}")
            return result
        except Exception as e:
            _LOGGER.error(f"Error in async function {f.__name__}: {e}", exc_info=True)
            raise

    @wraps(f)
    def sync_wrapper(*args, **kwargs):
        try:
            _LOGGER.debug(f"Start function {f.__name__}")
            result = f(*args, **kwargs)
            _LOGGER.debug(f"End function {f.__name__}")
            return result
        except Exception as e:
            _LOGGER.error(f"Error in function {f.__name__}: {e}", exc_info=True)
            raise

    if asyncio.iscoroutinefunction(f):
        return async_wrapper
    else:
        return sync_wrapper
