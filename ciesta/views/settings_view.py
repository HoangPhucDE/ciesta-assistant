from PySide6.QtWidgets import (QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, 
                               QLabel, QComboBox, QRadioButton, QPushButton, QLineEdit)
from PySide6.QtCore import Qt
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

        # Connection Type Selection
        self.connection_type_combo = QComboBox()
        self.connection_type_combo.addItems(["Local", "LAN", "Ngrok"])
        self.connection_type_combo.currentTextChanged.connect(self._on_connection_type_changed)
        self.layout.addRow("Connection Type:", self.connection_type_combo)

        # Server URL Input với placeholder động
        server_layout = QVBoxLayout()
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("http://localhost:5005")
        self.server_help_label = QLabel()
        self.server_help_label.setStyleSheet("color: #888; font-size: 11px;")
        self.server_help_label.setWordWrap(True)
        server_layout.addWidget(self.server_input)
        server_layout.addWidget(self.server_help_label)
        self.layout.addRow("Server URL:", server_layout)

        # Auto-detect Ngrok và Test Connection Buttons
        button_layout = QHBoxLayout()
        
        self.auto_detect_button = QPushButton("🔍 Auto-detect Ngrok")
        self.auto_detect_button.clicked.connect(self._auto_detect_ngrok)
        button_layout.addWidget(self.auto_detect_button)
        
        self.test_button = QPushButton("✅ Test Connection")
        self.test_button.clicked.connect(self._test_connection)
        button_layout.addWidget(self.test_button)
        
        self.status_label = QLabel()
        self.status_label.setStyleSheet("font-size: 11px;")
        self.status_label.setWordWrap(True)
        
        self.layout.addRow("", button_layout)
        self.layout.addRow("", self.status_label)

        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.back_button = QPushButton("Back to Chat")
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.back_button)
        self.layout.addRow(buttons_layout)

        self.setLayout(self.layout)
        self._update_help_text()
        # Ẩn nút auto-detect ban đầu (chỉ hiện khi chọn Ngrok)
        self.auto_detect_button.setVisible(False)

    def _on_connection_type_changed(self):
        """Cập nhật placeholder và help text khi đổi connection type"""
        self._update_help_text()
        # Hiện/ẩn nút auto-detect dựa trên connection type
        connection_type = self.connection_type_combo.currentText()
        self.auto_detect_button.setVisible(connection_type == "Ngrok")
        
        # Tự động điền URL mẫu nếu input trống
        if not self.server_input.text():
            if connection_type == "Local":
                self.server_input.setText("http://localhost:5005")
            elif connection_type == "LAN":
                self.server_input.setText("http://192.168.1.100:5005")
            elif connection_type == "Ngrok":
                self.server_input.setText("https://xxxx-xx-xx-xx-xx.ngrok-free.app")

    def _update_help_text(self):
        """Cập nhật help text dựa trên connection type"""
        connection_type = self.connection_type_combo.currentText()
        if connection_type == "Local":
            self.server_help_label.setText("📍 Chạy trên cùng máy (localhost)")
            self.server_input.setPlaceholderText("http://localhost:5005")
        elif connection_type == "LAN":
            self.server_help_label.setText("🌐 Kết nối qua mạng nội bộ (IP:port)")
            self.server_input.setPlaceholderText("http://192.168.1.100:5005")
        elif connection_type == "Ngrok":
            self.server_help_label.setText(
                "🔗 URL từ ngrok tunnel (https://xxx.ngrok-free.app)\n"
                "💡 Tip: Click 'Auto-detect Ngrok' để tự động lấy URL từ ngrok API"
            )
            self.server_input.setPlaceholderText("https://xxxx-xx-xx-xx-xx.ngrok-free.app")

    def _auto_detect_ngrok(self):
        """Tự động lấy URL từ ngrok API"""
        from controllers.api_client import APIClient
        
        self.auto_detect_button.setEnabled(False)
        self.auto_detect_button.setText("🔄 Đang tìm...")
        self.status_label.setText("Đang kết nối đến ngrok API...")
        self.status_label.setStyleSheet("color: orange; font-size: 11px;")
        
        try:
            ngrok_url, error_msg = APIClient.get_ngrok_url()
            
            if ngrok_url:
                self.server_input.setText(ngrok_url)
                self.status_label.setText(f"✅ Đã tìm thấy: {ngrok_url}")
                self.status_label.setStyleSheet("color: green; font-size: 11px;")
            else:
                self.status_label.setText(f"❌ {error_msg}")
                self.status_label.setStyleSheet("color: red; font-size: 11px;")
        except Exception as e:
            self.status_label.setText(f"❌ Lỗi: {str(e)[:100]}")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
        finally:
            self.auto_detect_button.setEnabled(True)
            self.auto_detect_button.setText("🔍 Auto-detect Ngrok")

    def _test_connection(self):
        """Test kết nối đến server"""
        from controllers.api_client import APIClient
        url = self.server_input.text().strip()
        if not url:
            self.status_label.setText("❌ Vui lòng nhập URL")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
            return
        
        self.test_button.setEnabled(False)
        self.test_button.setText("🔄 Testing...")
        self.status_label.setText("Đang kiểm tra kết nối...")
        self.status_label.setStyleSheet("color: orange; font-size: 11px;")
        
        try:
            client = APIClient(url)
            # Test với message đơn giản
            result = client.health_check()
            if result:
                self.status_label.setText("✅ Kết nối thành công!")
                self.status_label.setStyleSheet("color: green; font-size: 11px;")
            else:
                self.status_label.setText("⚠️ Server không phản hồi")
                self.status_label.setStyleSheet("color: orange; font-size: 11px;")
        except Exception as e:
            self.status_label.setText(f"❌ Lỗi: {str(e)[:100]}")
            self.status_label.setStyleSheet("color: red; font-size: 11px;")
        finally:
            self.test_button.setEnabled(True)
            self.test_button.setText("✅ Test Connection")

    def load_config(self):
        config = load_config()
        self.language_combo.setCurrentText(config.get('language', 'Tiếng Việt'))
        self.light_radio.setChecked(config.get('theme', 'Tối') == 'Sáng')
        
        # Load connection type và URL
        connection_type = config.get('connection_type', 'Local')
        if connection_type in ['Local', 'LAN', 'Ngrok']:
            self.connection_type_combo.setCurrentText(connection_type)
        else:
            # Auto-detect từ URL
            server_url = config.get('server_url', 'http://localhost:5005')
            if 'ngrok' in server_url.lower() or 'ngrok-free.app' in server_url:
                self.connection_type_combo.setCurrentText('Ngrok')
            elif 'localhost' in server_url or '127.0.0.1' in server_url:
                self.connection_type_combo.setCurrentText('Local')
            else:
                self.connection_type_combo.setCurrentText('LAN')
        
        self.server_input.setText(config.get('server_url', 'http://localhost:5005'))
        self._update_help_text()

    def save_config(self):
        config = {
            'language': self.language_combo.currentText(),
            'theme': 'Sáng' if self.light_radio.isChecked() else 'Tối',
            'connection_type': self.connection_type_combo.currentText(),
            'server_url': self.server_input.text().strip()
        }
        save_config(config)