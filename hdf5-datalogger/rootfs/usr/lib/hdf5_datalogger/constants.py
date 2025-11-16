API_URL = "http://supervisor/core/api"
OPTIONS_PATH = "/data/options.json"

# Domini inclusi di default se include_domains è vuoto
DEFAULT_INCLUDED_DOMAINS = {
    "sensor",
    "binary_sensor",
    "button",
    "climate",
    "light",
}

# Percorso per lo stato degli ultimi valori (per il log "solo se cambia")
LAST_VALUES_PATH = "/data/hdf5_last_values.json"
