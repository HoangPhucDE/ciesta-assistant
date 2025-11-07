import json
import os

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Backward compatibility: nếu không có connection_type, tự detect
            if 'connection_type' not in config:
                server_url = config.get('server_url', 'http://localhost:5005')
                if 'ngrok' in server_url.lower():
                    config['connection_type'] = 'Ngrok'
                elif 'localhost' in server_url or '127.0.0.1' in server_url:
                    config['connection_type'] = 'Local'
                else:
                    config['connection_type'] = 'LAN'
            return config
    return {
        "theme": "Tối",
        "language": "Tiếng Việt",
        "connection_type": "Local",
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
