import json
from .constants import OPTIONS_PATH

def load_options():
    """
    Carica le opzioni dal file /data/options.json con default sensati.
    """
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "max_entities": 0,
        "update_interval": 60,
        "include_domains": [],  # lista di domini, vuota = usa DEFAULT_INCLUDED_DOMAINS
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key in list(opts.keys()):
            if key in data:
                opts[key] = data[key]
    except Exception:
        # fallback ai default se qualcosa va storto
        pass
    return opts
