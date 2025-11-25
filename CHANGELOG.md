# Changelog

All notable changes to this project will be documented in this file.

## v1.4.0

### Fixed

- Dans le dashboard énergie, les données sont remontées à la bonne date.
- Correction de l'import déprécié `Config` depuis `homeassistant.core_config`
- Correction du décorateur `decoratorexceptionDebug` pour gérer correctement les fonctions asynchrones avec `await`
- Correction de l'appel aux statistiques du recorder : utilisation de `self.hass.async_add_executor_job` au lieu de `get_instance().async_add_executor_job`
- Correction du format `statistic_id` pour respecter les exigences de Home Assistant (caractères alphanumériques uniquement)
- Ajout du paramètre `unit_class` dans `StatisticMetaData` pour la compatibilité avec Home Assistant 2026.11
- Amélioration des logs pour faciliter le débogage

### Changed

- Nettoyage des imports inutilisés (`get_instance`, `statistics_during_period`)
- Sanitisation robuste du `statistic_id` basé sur l'ABO_ID

## v1.3.1

### Changed

- Mise à jour des dépendances
- Mise à jour fonctions dépréciées par home assistant
  
## v1.3.0

### Changed

- Mise à jour des dépendances
- Ajout info tableau de bord energie dans Readme
  

## v1.2.0

### Breaking change
  
---
  **La configuration perd le mot de pase en passant à cette version.**

  **Il faut supprimer l'intégration PUIS la recréer, mais les historiques de données seront repris.**

---

### Changed

- Passage de la doc en Français, l'usage étant réservé à la France.
- Ajout de la gestion multi compteur. 
    Dans la configuration, vous pourrez préciser la référence d'abonnement (voir Readme)
    Vous devez pour cela supprimer l'intégration actuelle pour la recréer.
  

## v1.1.2

### Changed

- Améliorer le retour si erreur 500 : possibilité de récupérer le message du serveur

## v1.1.1

### Changed

- Ajout d'un controle si l'historique des consos ne ramène qu'un résultat

## v1.1.0

### Breaking change

- le format d'historique a été modifié pour être plus facilement intégrable dans apexcharts-card

### Changed

- Ajout d'un exemple d'utilisation d'apexcharts-card pour l'historique
 
## v1.0.3

### Changed

- Ajout de traces
  
## v1.0.2

### Changed

- Gestion de l'abonnement si plusieurs abonnements
  
## v1.0.1

### Changed

- Amélioration des traces

## v1.0.0

### Changed

- reformatage du code
- `veolia_last_index` peut être utilisé dans le tableau de bord `Energie`

## v0.0.4

### Changed

- Correction bug sur last_index

## v0.0.3

### Changed

- Added sensor last_index compatible with energy dashboard

## v0.0.2

### Changed

- Added sensor monthly_consumption

## v0.0.1

- First Beta unreleased
