# config_db.py
import json
import os

CONFIG_FILE = "config_db.json"

def cargar_config_db():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    else:
        return None

def guardar_config_db(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
