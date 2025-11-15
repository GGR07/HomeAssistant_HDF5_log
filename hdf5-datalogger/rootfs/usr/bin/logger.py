#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime

OUTPUT_FILE = "/share/example_addon_output.txt"
API_URL = "http://supervisor/core/api"
TOKEN = os.getenv("SUPERVISOR_TOKEN")

if not TOKEN:
    raise SystemExit("ERROR: SUPERVISOR_TOKEN is missing. Check 'homeassistant_api: true' in config.yaml.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}

def ha_api(endpoint):
    """Call Home Assistant Supervisor API."""
    url = f"{API_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def write_line(text):
    """Write a line to the output file."""
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def start_new_file():
    """Reset the file and write header."""
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("===== HOME ASSISTANT STRUCTURE REPORT =====\n")
        f.write(f"Generated at: {datetime.now()}\n\n")

def main():
    start_new_file()

    # 1. AREE
    write_line("===== AREE =====")
    try:
        areas = ha_api("/config/area_registry/list")
        for area in areas:
            name = area.get("name")
            area_id = area.get("area_id")
            write_line(f"- {name} (area_id: {area_id})")
    except Exception as err:
        write_line(f"ERROR retrieving areas: {err}")
    write_line("")

    # 2. DISPOSITIVI
    write_line("===== DISPOSITIVI =====")
    try:
        devices = ha_api("/config/device_registry/list")
        for dev in devices:
            name = dev.get("name_by_user") or dev.get("name")
            device_id = dev.get("id")
            area_id = dev.get("area_id")
            write_line(f"- {name} (device_id: {device_id}, area: {area_id})")
    except Exception as err:
        write_line(f"ERROR retrieving devices: {err}")
    write_line("")

    # 3. ENTITÀ
    write_line("===== ENTITÀ =====")
    try:
        entities = ha_api("/config/entity_registry/list")
        for ent in entities:
            entity_id = ent.get("entity_id")
            device_id = ent.get("device_id")
            area_id = ent.get("area_id")
            write_line(f"- {entity_id} (device_id: {device_id}, area_id: {area_id})")
    except Exception as err:
        write_line(f"ERROR retrieving entities: {err}")
    write_line("")

    # 4. STATI
    write_line("===== STATI =====")
    try:
        states = ha_api("/states")
        for s in states:
            entity_id = s.get("entity_id")
            state = s.get("state")
            write_line(f"- {entity_id}: {state}")
    except Exception as err:
        write_line(f"ERROR retrieving states: {err}")

    write_line("\n===== END =====")

if __name__ == "__main__":
    main()
