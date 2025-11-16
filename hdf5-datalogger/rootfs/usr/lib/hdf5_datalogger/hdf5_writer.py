import os
import json
from typing import Dict, Tuple, List, Any
import h5py

from .domains import domain_of
from .timeutils import utc_now_z, today_str_local
from .constants import LAST_VALUES_PATH


def _load_last_values(path: str = LAST_VALUES_PATH) -> Dict[str, str]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return {str(k): str(v) for k, v in data.items()}
    except Exception:
        pass
    return {}


def _save_last_values(last_values: Dict[str, str], path: str = LAST_VALUES_PATH) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    except Exception:
        pass
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(last_values, f)
        os.replace(tmp, path)
    except Exception:
        # non bloccare il logger se fallisce il salvataggio
        pass


def _ensure_group(f: h5py.File, domain: str, entity_id: str, attrs: dict) -> h5py.Group:
    group_path = f"/{domain}/{entity_id}"
    grp = f.require_group(group_path)
    # aggiorna attributi statici utili
    for key in ("friendly_name", "unit_of_measurement", "device_class", "state_class", "area_id", "device_id"):
        if key in attrs:
            try:
                grp.attrs[key] = attrs[key]
            except Exception:
                grp.attrs[key] = str(attrs[key])
    grp.attrs["domain"] = domain
    grp.attrs["entity_id"] = entity_id
    return grp


def _ensure_datasets(grp: h5py.Group, first_value_is_numeric: bool) -> Tuple[h5py.Dataset, h5py.Dataset]:
    # dataset timestamp: stringhe ISO-8601
    if "timestamp" not in grp:
        ts_ds = grp.create_dataset(
            "timestamp",
            shape=(0,),
            maxshape=(None,),
            dtype="S32",
        )
    else:
        ts_ds = grp["timestamp"]

    # dataset value: float64 o stringa a seconda del primo valore
    if "value" not in grp:
        if first_value_is_numeric:
            val_ds = grp.create_dataset(
                "value",
                shape=(0,),
                maxshape=(None,),
                dtype="f8",
            )
        else:
            val_ds = grp.create_dataset(
                "value",
                shape=(0,),
                maxshape=(None,),
                dtype="S256",
            )
    else:
        val_ds = grp["value"]

    return val_ds, ts_ds


def _parse_value(raw: str, prefer_numeric: bool) -> Tuple[Any, bool]:
    if not prefer_numeric:
        return raw, False
    try:
        return float(raw), True
    except Exception:
        return raw, False


def append_states_to_hdf5(
    states: List[dict],
    output_path_prefix: str,
) -> Dict[str, Any]:
    """
    Scrive i dati nel file HDF5 del giorno corrente in modalità append,
    solo se il valore è cambiato rispetto all'ultimo loggato.

    Ritorna un dict con statistiche: appended_points, skipped_points, file_path
    """
    stats: Dict[str, Any] = {
        "appended_points": 0,
        "skipped_points": 0,
        "file_path": "",
    }

    if not states:
        return stats

    today_str = today_str_local()
    filename = f"HDF5_datalogger_{today_str}.h5"

    # gestisci eventuale slash finale nel prefisso
    if output_path_prefix.endswith("/") or output_path_prefix.endswith("\\"):
        filepath = output_path_prefix + filename
    else:
        filepath = os.path.join(output_path_prefix, filename)

    stats["file_path"] = filepath

    # assicura cartella
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    except Exception:
        pass

    last_values = _load_last_values()
    ts_now = utc_now_z().encode("utf-8")

    with h5py.File(filepath, "a") as f:
        for st in states:
            entity_id = st.get("entity_id", "")
            if not entity_id:
                continue

            domain = domain_of(entity_id)
            new_state_raw = str(st.get("state", ""))

            old_state_raw = last_values.get(entity_id)
            if old_state_raw is not None and old_state_raw == new_state_raw:
                stats["skipped_points"] += 1
                continue

            attrs = st.get("attributes", {}) or {}
            grp = _ensure_group(f, domain, entity_id, attrs)

            # decidiamo il tipo al primo valore
            _, is_numeric = _parse_value(new_state_raw, prefer_numeric=True)
            val_ds, ts_ds = _ensure_datasets(grp, first_value_is_numeric=is_numeric)

            # ridimensiona e scrivi
            new_len = val_ds.shape[0] + 1
            val_ds.resize((new_len,))
            ts_ds.resize((new_len,))

            # scrivi valore
            if val_ds.dtype.kind in ("f", "i"):
                from math import nan
                try:
                    val_ds[-1] = float(new_state_raw)
                except Exception:
                    val_ds[-1] = nan
            else:
                val_ds[-1] = str(new_state_raw).encode("utf-8")

            # scrivi timestamp
            ts_ds[-1] = ts_now

            last_values[entity_id] = new_state_raw
            stats["appended_points"] += 1

    _save_last_values(last_values)
    return stats
