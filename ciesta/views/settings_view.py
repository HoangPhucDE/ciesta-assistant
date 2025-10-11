from PySide6.QtWidgets import (QWidget, QFormLayout, QHBoxLayout, QLabel, QComboBox, QRadioButton, QPushButton, QLineEdit)
from utils import load_config, save_config

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(15)

        self.title = QLabel("⚙️ Settings")
        self.title.setStyleSheet("font-size: 20px; color: #00d4ff;")
        self.layout.addRow(self.title)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["Tiếng Việt", "English"])
        self.layout.addRow("Language:", self.language_combo)

        self.light_radio = QRadioButton("Light")
        self.dark_radio = QRadioButton("Dark")
        self.light_radio.toggled.connect(lambda: self.dark_radio.setChecked(not self.light_radio.isChecked()))
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(self.light_radio)
        theme_layout.addWidget(self.dark_radio)
        self.layout.addRow("Theme:", theme_layout)

        self.server_input = QLineEdit("localhost:5005")
        self.layout.addRow("Server:", self.server_input)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.back_button = QPushButton("Back to Chat")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.back_button)
        self.layout.addRow(buttons_layout)

        self.setLayout(self.layout)

    def load_config(self):
        config = load_config()
        self.language_combo.setCurrentText(config.get('language', 'Tiếng Việt'))
        self.light_radio.setChecked(config.get('theme', 'Tối') == 'Sáng')
        self.server_input.setText(config.get('server_url', 'localhost:5005'))

    def save_config(self):
        config = {
            'language': self.language_combo.currentText(),
            'theme': 'Sáng' if self.light_radio.isChecked() else 'Tối',
            'server_url': self.server_input.text()
        }
        save_config(config)