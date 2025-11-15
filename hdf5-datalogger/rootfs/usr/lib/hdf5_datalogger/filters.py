from .domains import domain_of

def filter_states(states: list) -> tuple[list, dict]:
  """
  Applica il filtro "fisico":

  - sensor: incluso solo se ha attributes.unit_of_measurement non vuoto
  - binary_sensor: sempre incluso
  - climate: sempre incluso
  - altri domini: nessun filtro specifico (verranno filtrati per dominio dopo)

  Ritorna:
    (lista_filtrata, stats_dict)
  """
  filtered = []
  stats = {
    "excluded_sensors_no_unit_of_measurement": 0,
  }

  for st in states:
    eid = st.get("entity_id", "") or ""
    dom = domain_of(eid)
    attrs = st.get("attributes", {}) or {}

    if dom == "sensor":
      uom = attrs.get("unit_of_measurement")
      if not uom:
        stats["excluded_sensors_no_unit_of_measurement"] += 1
        continue
      # sensor con unit_of_measurement -> incluso
      filtered.append(st)
      continue

    if dom in ("binary_sensor", "climate"):
      # sempre inclusi (salvo filtro domini dopo)
      filtered.append(st)
      continue

    # altri domini: li lasciamo passare
    filtered.append(st)

  return filtered, stats
