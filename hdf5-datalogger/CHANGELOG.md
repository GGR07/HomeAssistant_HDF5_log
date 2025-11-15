# Changelog
Tutte le modifiche rilevanti a **HDF5 DataLogger** verranno documentate in questo file.

Il formato segue [Keep a Changelog](https://keepachangelog.com/it-IT/1.0.0/),
e la versione segue [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2025-11-15
### Added
- **Logger REST stabile** basato su `/api/states`:
  - Generazione report testuale leggibile raggruppato per **dominio**.
  - Supporto filtri in UI: `include_domains`, `include_attributes`, `max_entities`.
  - **Percorso file configurabile**: `output_path` (default `/share/example_addon_output.txt`).
  - **Intervallo configurabile**: `update_interval` (il servizio rilegge l’opzione a ogni ciclo).
- **Passaggio a Python**: introdotto `rootfs/usr/bin/logger.py`.
- **Run loop** che invoca il logger e attende l’intervallo configurato.

### Changed
- `config.yaml`: `homeassistant_api: true`, nuove sezioni `options`/`schema`.
- Dockerfile: base `ghcr.io/hassio-addons/base-python:17.0.0` + `pip install requests`.

---

## [0.1.8] - 2025-11-15
### Fixed
- Tentativo di installare dipendenze Python tramite `pip` (introduzione `requests`).
### Note
- Build fallita se `requirements.txt` non presente nel contesto (poi rimosso in favore di `pip install` inline).

## [0.1.7] - 2025-11-15
### Changed
- Transizione da script bash a **logger Python**.
### Fixed
- Sistemato percorso e permessi dei servizi S6.
### Known Issues
- Build fallita con `base-python:12.2.0` inesistente per multi-arch.

## [0.1.6] - 2025-11-15
### Fixed
- **Rimossa l’immagine remota** dal `config.yaml` per usare build locale sul device.
- Allineata struttura `rootfs/etc/services.d/` con slug `hdf5_datalogger`.
- Aggiunti permessi eseguibili dove necessario.

## [0.1.4] - 2025-11-15
### Changed
- Tentativo di utilizzo immagine pubblicata (GHCR) per installazione più rapida.
### Known Issues
- Errore **403 Forbidden** su immagini `ghcr.io/home-assistant/...` non accessibili: ripristinata strategia di build locale.

## [0.1.1] - 2025-11-15
### Fixed
- Pulizia `config.yaml` (rimozione escape, BOM) e aggiunta `map: ["share:rw"]`.
- Aggiunto `init: false` per compatibilità con s6 overlay v3.

## [0.1.0] - 2025-11-15
### Added
- **Prima versione funzionante** “Hello world” con servizi S6 e scrittura file su `/share`.

---

## Note di rilascio
- Per modifiche a `rootfs/` o al Dockerfile è **necessario**: Add-on Store → Aggiorna repository → **Disinstalla** → **Reinstalla**.
- L’uso delle API REST richiede `homeassistant_api: true`.
- I log del container si “resettano” fermando/avviando l’add-on o usando “Clear logs” dopo lo **Stop**.

