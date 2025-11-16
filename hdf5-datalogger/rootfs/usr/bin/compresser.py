#!/usr/bin/env python3
"""
HDF5 Compresser - v0.3.0

- Ogni giorno, all'ora compress_time (HH:MM, ora locale container),
  comprime il file HDF5 del giorno precedente:
  <output_path_prefix>HDF5_datalogger_<YYYY-MM-DD>.h5

- Flusso:
  * crea backup .bak
  * crea file .tmp.h5 compresso (gzip livello 4)
  * sostituisce l'originale
  * rimuove il backup se tutto ok
"""

import os
import sys
import time
from datetime import datetime, timedelta

if "/usr/lib" not in sys.path:
    sys.path.insert(0, "/usr/lib")

import h5py

from hdf5_datalogger.config_loader import load_options

def _build_hdf5_path(prefix: str, date_str: str) -> str:
    filename = f"HDF5_datalogger_{date_str}.h5"
    if prefix.endswith("/") or prefix.endswith("\\"):
        return prefix + filename
    return os.path.join(prefix, filename)

def _copy_with_compression(src_path: str, tmp_path: str) -> None:
    with h5py.File(src_path, "r") as fin, h5py.File(tmp_path, "w") as fout:
        def _recurse_copy(g_in, g_out):
            # copia attributi del gruppo
            for aname, aval in g_in.attrs.items():
                g_out.attrs[aname] = aval
            for name, item in g_in.items():
                if isinstance(item, h5py.Dataset):
                    data = item[()]
                    # crea dataset compresso (gzip livello 4)
                    dset = g_out.create_dataset(
                        name,
                        data=data,
                        compression="gzip",
                        compression_opts=4,
                    )
                    for aname, aval in item.attrs.items():
                        dset.attrs[aname] = aval
                elif isinstance(item, h5py.Group):
                    sub = g_out.create_group(name)
                    _recurse_copy(item, sub)
        _recurse_copy(fin, fout)

def main():
    last_compressed_for = None

    while True:
        try:
            opts = load_options()
            prefix = opts.get("output_path_prefix") or "/share/hdf5/"
            compress_time = (opts.get("compress_time") or "02:00").strip()
        except Exception:
            prefix = "/share/hdf5/"
            compress_time = "02:00"

        now = datetime.now()
        current_hm = now.strftime("%H:%M")

        if current_hm == compress_time:
            # comprimi il giorno precedente
            target_date = (now.date() - timedelta(days=1)).isoformat()

            if last_compressed_for == target_date:
                # già compresso per questa data in questo giro
                time.sleep(60)
                continue

            src = _build_hdf5_path(prefix, target_date)
            if not os.path.exists(src):
                print(f"[WARNING] Nessun file HDF5 da comprimere per la data {target_date}: {src}")
                last_compressed_for = target_date
                time.sleep(60)
                continue

            backup = src + ".bak"
            tmp = src + ".tmp"

            print("[INFO] ===== HDF5 Compresser =====")
            print(f"[INFO] Ora locale: {now.isoformat()}")
            print(f"[INFO] File da comprimere: {src}")
            print(f"[INFO] Backup: {backup}")
            print(f"[INFO] File temporaneo: {tmp}")

            # crea backup
            try:
                import shutil
                shutil.copy2(src, backup)
            except Exception as e:
                print(f"[ERROR] Impossibile creare backup {backup}: {e}")
                last_compressed_for = target_date
                time.sleep(60)
                continue

            # comprimi in tmp
            try:
                print("[INFO] Inizio compressione (gzip livello 4)...")
                t0 = time.time()
                _copy_with_compression(src, tmp)
                t1 = time.time()
                size_orig = os.path.getsize(src)
                size_tmp = os.path.getsize(tmp)
                print(f"[INFO] Compressione completata in {t1 - t0:.1f}s")
                print(f"[INFO] Dimensione originale: {size_orig / (1024*1024):.2f} MB")
                print(f"[INFO] Dimensione compressa: {size_tmp / (1024*1024):.2f} MB")
                if size_orig > 0:
                    reduction = 100.0 * (1.0 - (size_tmp / size_orig))
                    print(f"[INFO] Riduzione: {reduction:.1f}%")
            except Exception as e:
                print(f"[ERROR] Errore durante la compressione di {src}: {e}")
                try:
                    if os.path.exists(tmp):
                        os.remove(tmp)
                except Exception:
                    pass
                print(f"[WARNING] File originale e backup mantenuti: {src}, {backup}")
                last_compressed_for = target_date
                time.sleep(60)
                continue

            # sostituisci il file originale con il compresso
            try:
                os.replace(tmp, src)
                print("[INFO] File originale sostituito con la versione compressa.")
            except Exception as e:
                print(f"[ERROR] Impossibile sostituire il file originale {src} con {tmp}: {e}")
                print(f"[WARNING] Backup non rimosso: {backup}")
                last_compressed_for = target_date
                time.sleep(60)
                continue

            # rimuovi backup
            try:
                os.remove(backup)
                print(f"[INFO] Backup rimosso: {backup}")
            except Exception as e:
                print(f"[WARNING] Impossibile rimuovere il backup {backup}: {e}")

            print("[INFO] ===== HDF5 Compresser terminato =====")
            last_compressed_for = target_date
            time.sleep(60)
        else:
            time.sleep(20)

if __name__ == "__main__":
    main()
