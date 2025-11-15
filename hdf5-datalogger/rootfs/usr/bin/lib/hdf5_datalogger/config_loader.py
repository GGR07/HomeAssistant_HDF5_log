import json
from .constants import OPTIONS_PATH, DOMAIN_FLAGS

def load_options():
    # Default coerenti con config.yaml
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "max_entities": 0,
        "include_domains_extra": [],
        **{k: False for k in DOMAIN_FLAGS.keys()},
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in opts.keys():
            if k in data:
                opts[k] = data[k]
    except Exception:
        pass
    return opts
