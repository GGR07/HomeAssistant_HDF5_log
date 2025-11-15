API_URL = "http://supervisor/core/api"
OPTIONS_PATH = "/data/options.json"

# mapping flag -> domain (coerente con config.yaml attuale)
DOMAIN_FLAGS = {
    "include_sensor": "sensor",
    "include_binary_sensor": "binary_sensor",
    "include_light": "light",
    "include_switch": "switch",
    "include_climate": "climate",
    "include_cover": "cover",
    "include_fan": "fan",
    "include_media_player": "media_player",
    "include_lock": "lock",
    "include_device_tracker": "device_tracker",
    "include_person": "person",
    "include_camera": "camera",
    "include_alarm_control_panel": "alarm_control_panel",
    "include_scene": "scene",
    "include_script": "script",
    "include_automation": "automation",
    "include_button": "button",
    "include_number": "number",
    "include_select": "select",
    "include_input_boolean": "input_boolean",
    "include_input_number": "input_number",
    "include_input_select": "input_select",
    "include_input_text": "input_text",
    "include_vacuum": "vacuum",
    "include_weather": "weather",
    "include_water_heater": "water_heater",
    "include_valve": "valve",
    "include_siren": "siren",
}
