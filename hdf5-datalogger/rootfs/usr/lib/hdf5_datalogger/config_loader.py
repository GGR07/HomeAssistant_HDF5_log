import json
from .constants import OPTIONS_PATH

def load_options():
    # default coerenti con config.yaml v0.3.0
    opts = {
        "output_path": "/share/example_addon_output.txt",
        "max_entities": 0,

        # domini
        "domain_mode": "presets",
        "domain_presets": ["sensors"],
        "domains_include": [],
        "domains_exclude": [],
        "strict_domains": True,

        # attributi
        "attributes_mode": "all",
        "attributes_include": [],
        "attributes_exclude": [
            "icon",
            "entity_picture",
            "attribution",
            "editable",
            "restored",
            "supported_features",
            "supported_color_modes",
        ],
    }
    try:
        with open(OPTIONS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k in list(opts.keys()):
            if k in data:
                opts[k] = data[k]
    except Exception:
        pass
    return opts
