API_URL = "http://supervisor/core/api"
OPTIONS_PATH = "/data/options.json"

# Preset → insiemi di domini
PRESET_DOMAINS = {
    "sensors": {"sensor", "binary_sensor"},
    "actuators": {"light", "switch", "cover", "climate", "fan", "lock", "siren", "valve", "water_heater"},
    "presence": {"device_tracker", "person"},
    "media": {"media_player"},
    "automations": {"automation", "script", "scene"},
}

# Attributi essenziali (profilo 'essentials')
ESSENTIAL_ATTRS = {"friendly_name", "unit_of_measurement", "device_class", "state_class"}

# Correzioni comuni di plurali/typo
DOMAIN_CORRECTIONS = {
    "sensors": "sensor",
    "binary_sensors": "binary_sensor",
    "lights": "light",
    "switches": "switch",
    "binanry_sensor": "binary_sensor",
    "binanry_sensors": "binary_sensor",
}
