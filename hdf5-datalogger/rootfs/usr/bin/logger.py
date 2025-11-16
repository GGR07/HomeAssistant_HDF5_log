#!/usr/bin/env python3
"""
HDF5 DataLogger - v0.3.0

- REST /api/states
- Filtro “fisico”:
  * sensor: incluso solo se ha unit_of_measurement
  * binary_sensor: sempre incluso
  * button: sempre incluso
  * climate: sempre incluso
  * light: sempre incluso
- Filtro domini via include_domains (lista) + domini di default
- Report testuale + HDF5 giornaliero (solo su cambio di valore)
"""

import os
import sys

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
from hdf5_datalogger.constants import DEFAULT_INCLUDED_DOMAINS
from hdf5_datalogger.hdf5_writer import append_states_to_hdf5

TOKEN = os.getenv("SUPERVISOR_TOKEN")
if not TOKEN:
    raise SystemExit("ERROR: SUPERVISOR_TOKEN missing. Ensure homeassistant_api: true in config.yaml.")

def main():
    opts = load_options()
    output_path = opts["output_path"]
    max_entities = int(opts.get("max_entities", 0) or 0)
    update_interval = int(opts.get("update_interval", 60) or 60)
    include_domains_raw = opts.get("include_domains") or []
    output_path_prefix = opts.get("output_path_prefix") or "/share/hdf5/"

    ts_run = utc_now_z()

    try:
        all_states = get_states(TOKEN)
    except Exception as e:
        print("[ERROR] Error fetching /states:", repr(e))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("===== HOME ASSISTANT STATES REPORT =====\n")
            f.write(f"Generated at: {ts_run}\n\n")
            f.write(f"ERROR fetching /states: {e}\n")
            f.write("===== END =====\n")
        return

    # 1) Filtro fisico
    filtered_states, filter_stats = filter_states(all_states)

    # 2) Domini disponibili
    available_domains = discover_available_domains(filtered_states)

    # 3) include_domains + default
    selected_domains, domain_warnings = build_included_domains(
        include_domains_raw,
        available_domains,
        DEFAULT_INCLUDED_DOMAINS,
    )

    # 4) Raggruppa per dominio
    grouped = group_states_by_domain(filtered_states, selected_domains)

    # Flatten per HDF5: solo gli stati nei domini effettivamente inclusi
    states_for_hdf5 = []
    for _, entities in grouped.items():
        states_for_hdf5.extend(entities)

    # 5) Scrittura HDF5
    hdf5_stats = append_states_to_hdf5(states_for_hdf5, output_path_prefix)

    # 6) Log esteso nel log dell'add-on
    total_entities = filter_stats.get("total_entities", len(all_states))
    included_after_filter = filter_stats.get("included_after_filter", len(filtered_states))

    print("[INFO] ===============================")
    print("[INFO] HDF5 DataLogger run")
    print(f"[INFO] Timestamp run (UTC): {ts_run}")
    print(f"[INFO] Output report (testo): {output_path}")
    print(f"[INFO] HDF5 file corrente: {hdf5_stats.get('file_path', '')}")
    print(f"[INFO] Update interval: {update_interval} secondi")
    print(f"[INFO] Max entities per dominio: {max_entities} (0 = nessun limite)")
    print(f"[INFO] Entità totali lette da Home Assistant: {total_entities}")
    print(f"[INFO] Entità dopo filtro fisico: {included_after_filter}")
    print(f"[INFO] HDF5 points appended: {hdf5_stats.get('appended_points', 0)}")
    print(f"[INFO] HDF5 points skipped (unchanged): {hdf5_stats.get('skipped_points', 0)}")

    for key, label in [
        ("sensor_included", "Sensors inclusi (con unit_of_measurement)"),
        ("sensor_excluded_no_uom", "Sensors esclusi (senza unit_of_measurement)"),
        ("binary_sensor_included", "Binary sensors inclusi"),
        ("button_included", "Buttons inclusi"),
        ("climate_included", "Climate inclusi"),
        ("light_included", "Light inclusi"),
        ("other_included", "Altri domini inclusi"),
    ]:
        if key in filter_stats:
            print(f"[INFO]   {label}: {filter_stats[key]}")

    if include_domains_raw:
        normalized_cfg = sorted({str(d).strip().lower() for d in include_domains_raw if str(d).strip()})
        print("[INFO] include_domains (config): " + ", ".join(normalized_cfg))
    else:
        print("[INFO] include_domains (config): (vuoto => domini di default)")

    if DEFAULT_INCLUDED_DOMAINS:
        print("[INFO] Default included domains: " + ", ".join(sorted(DEFAULT_INCLUDED_DOMAINS)))

    if available_domains:
        print("[INFO] Domini disponibili (dopo filtro fisico): " + ", ".join(sorted(available_domains)))
    else:
        print("[INFO] Domini disponibili: (nessuno)")

    if selected_domains:
        print("[INFO] Domini inclusi effettivi: " + ", ".join(sorted(selected_domains)))
    else:
        print("[INFO] Domini inclusi effettivi: (tutti i domini disponibili)")

    if domain_warnings:
        for w in domain_warnings:
            print("[WARNING]", w)

    print(f"[INFO] Scrittura report in: {output_path}")

    # 7) Scrivi il report testuale
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

    print(f"[INFO] Report scritto in: {output_path}")
    print("[INFO] ===============================")

if __name__ == "__main__":
    main()
