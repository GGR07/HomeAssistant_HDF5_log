#!/usr/bin/env python3
"""
HDF5 DataLogger - v0.4.0
- REST /api/states
- Filtro "fisico":
  * sensor: incluso solo se ha unit_of_measurement
  * binary_sensor: sempre incluso
  * climate: sempre incluso
- Filtro dominio semplice via include_domains (lista)
- Log di tutti gli attributi
"""

import os
import sys

# fallback nel caso il run non setti PYTHONPATH
if "/usr/lib" not in sys.path:
  sys.path.insert(0, "/usr/lib")

from hdf5_datalogger.config_loader import load_options
from hdf5_datalogger.ha_client import get_states
from hdf5_datalogger.domains import (
  discover_available_domains,
  build_included_domains,
  group_states_by_domain,
)
from hdf5_datalogger.filters import filter_states
from hdf5_datalogger.report import write_report
from hdf5_datalogger.timeutils import utc_now_z

TOKEN = os.getenv("SUPERVISOR_TOKEN")
if not TOKEN:
  raise SystemExit("ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true in config.yaml.")

def main():
  opts = load_options()
  output_path = opts["output_path"]
  max_entities = int(opts.get("max_entities", 0) or 0)
  include_domains_raw = opts.get("include_domains") or []

  try:
    all_states = get_states(TOKEN)
  except Exception as e:
    ts = utc_now_z()
    with open(output_path, "w", encoding="utf-8") as f:
      f.write("===== HOME ASSISTANT STATES REPORT =====\n")
      f.write(f"Generated at: {ts}\n\n")
      f.write(f"ERROR fetching /states: {e}\n")
      f.write("===== END =====\n")
    return

  # 1) Filtro fisico (sensor con unit_of_measurement, binary_sensor e climate sempre inclusi)
  filtered_states, filter_stats = filter_states(all_states)

  # 2) Domini disponibili dopo il filtro
  available_domains = discover_available_domains(filtered_states)

  # 3) Applica include_domains (se valorizzato)
  selected_domains, domain_warnings = build_included_domains(include_domains_raw, available_domains)

  # 4) Raggruppa per dominio con il filtro domini
  grouped = group_states_by_domain(filtered_states, selected_domains)

  # 5) Scrivi report
  write_report(
    output_path=output_path,
    grouped=grouped,
    max_entities=max_entities,
    available_domains=available_domains,
    included_domains_effective=selected_domains,
    include_domains_raw=include_domains_raw,
    filter_stats=filter_stats,
    domain_warnings=domain_warnings,
  )

if __name__ == "__main__":
  main()
