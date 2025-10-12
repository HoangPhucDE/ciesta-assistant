import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "theme": "Tối",
        "language": "Tiếng Việt",
        "server_url": "http://localhost:5005"
    }

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

def load_stylesheet(theme_name):
    """Load QSS file tương ứng."""
    path = "styles/dark.qss" if theme_name == "Tối" else "styles/light.qss"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""
