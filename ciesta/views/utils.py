import json  # Đọc/ghi JSON

def load_stylesheet(theme='Tối'):
    base_style = ""  # Base QSS
    try:
        with open('styles/style.qss', 'r') as f:
            base_style = f.read()
    except FileNotFoundError:
        pass
    if theme == 'Sáng':  # Override light
        base_style += "\nQWidget { background: #f0f0f0; color: #000; }\nQLineEdit { background: #fff; color: #000; }\n"
    return base_style

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'theme': 'Tối', 'language': 'Tiếng Việt', 'server_url': 'localhost:5005'}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)