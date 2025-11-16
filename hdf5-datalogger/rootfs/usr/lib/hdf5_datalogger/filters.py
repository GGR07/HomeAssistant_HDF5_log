from .domains import domain_of

def filter_states(states: list):
    """
    Applica il filtro "fisico":

    - sensor: incluso solo se ha attributes.unit_of_measurement non vuoto
    - binary_sensor: sempre incluso
    - button: sempre incluso
    - climate: sempre incluso
    - light: sempre incluso
    - altri domini: nessun filtro specifico (verranno filtrati per dominio dopo)

    Ritorna:
      (lista_filtrata, stats_dict)
    """
    filtered = []
    stats = {
        "total_entities": len(states),
        "sensor_included": 0,
        "sensor_excluded_no_uom": 0,
        "binary_sensor_included": 0,
        "button_included": 0,
        "climate_included": 0,
        "light_included": 0,
        "other_included": 0,
    }

    for st in states:
        eid = st.get("entity_id", "") or ""
        dom = domain_of(eid)
        attrs = st.get("attributes", {}) or {}

        if dom == "sensor":
            uom = attrs.get("unit_of_measurement")
            if not uom:
                stats["sensor_excluded_no_uom"] += 1
                continue
            stats["sensor_included"] += 1
            filtered.append(st)
            continue

        if dom == "binary_sensor":
            stats["binary_sensor_included"] += 1
            filtered.append(st)
            continue

        if dom == "button":
            stats["button_included"] += 1
            filtered.append(st)
            continue

        if dom == "climate":
            stats["climate_included"] += 1
            filtered.append(st)
            continue

        if dom == "light":
            stats["light_included"] += 1
            filtered.append(st)
            continue

        # altri domini: li lasciamo passare
        stats["other_included"] += 1
        filtered.append(st)

    stats["included_after_filter"] = len(filtered)
    return filtered, stats
