#!/usr/bin/env python3
"""
HDF5 DataLogger - v0.2.0
- REST only: /api/states
- Domain filtering via boolean flags + include_domains_extra
- Text report, grouped by domain
- Logs ALL attributes for each entity
"""
import os
import json
from datetime import datetime, timezone
from collections import defaultdict

import requests

API_URL = "http://supervisor/core/api"
TOKEN = os.getenv("SUPERVISOR_TOKEN")
OPTIONS_PATH = "/data/options.json"

if not TOKEN:
    raise SystemExit(
        "ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true in config.yaml."
    )

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

# Mapping "flag option" -> domain
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

def load_options():
    # Defaults aligned with config.yaml
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "max_entities": 0,
        "include_domains_extra": [],
        # flags default values are handled by HA UI, but keep safe fallbacks here:
        **{k: False for k in DOMAIN_FLAGS.keys()},
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # copy known keys if present
        for k in opts.keys():
            if k in data:
                opts[k] = data[k]
    except Exception:
        pass
    return opts

def normalize_domain(d: str) -> str:
    """Basic normalization for extra domains input."""
    if not d:
        return ""
    d = d.strip().lower()
    # common plural -> singular corrections / typos
    corrections = {
        "sensors": "sensor",
        "binary_sensors": "binary_sensor",
        "lights": "light",
        "switches": "switch",
        "binanry_sensor": "binary_sensor",
        "binanry_sensors": "binary_sensor",
    }
    return corrections.get(d, d)

def build_included_domains(opts: dict, available_domains: set) -> set:
    """Build the final set of domains to include from flags + extras."""
    selected = set()

    # from boolean flags
    for flag, domain in DOMAIN_FLAGS.items():
        if opts.get(flag, False):
            selected.add(domain)

    # from extra list
    extras = opts.get("include_domains_extra", []) or []
    for d in extras:
        nd = normalize_domain(str(d))
        if nd:
            selected.add(nd)

    # If nothing selected, fallback to "include all"
    if not selected:
        return set()  # empty = include all

    # Keep only those that actually appear (helps avoid empty reports due to typos)
    if available_domains:
        return {d for d in selected if d in available_domains}
    return selected

def get_states():
    url = f"{API_URL}/states"
    r = requests.get(ur
