import sys  # Xử lý exit và args
from PySide6.QtWidgets import QApplication, QMainWindow  # App và window chính
from PySide6.QtCore import QTimer  # Delay cho loading
from utils import load_stylesheet, load_config  # Load theme/config
from views.login_view import LoginView  # Import views
from views.chat_view import ChatView
from views.settings_view import SettingsView
from backend.api_client import APIClient


class MainApp(QMainWindow):  # Window chính
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Chatbot Frontend")  # Tiêu đề
        self.setGeometry(100, 100, 700, 900)  # Kích thước

        config = load_config()  # Load config
        self.setStyleSheet(load_stylesheet(config.get('theme', 'Tối')))  # Áp theme
        self.api = APIClient('http://localhost:5005')  # Khởi tạo API

        # Views
        self.login_view = LoginView()
        self.chat_view = ChatView()
        self.settings_view = SettingsView()

        self.setCentralWidget(self.login_view)  # Bắt đầu login

        # Connect events
        self.login_view.login_button.clicked.connect(self.handle_login)
        self.login_view.register_button.clicked.connect(self.handle_register)
        self.chat_view.send_button.clicked.connect(self.handle_send_message)
        self.chat_view.message_input.returnPressed.connect(self.handle_send_message)
        self.chat_view.settings_button.clicked.connect(self.show_settings)
        self.settings_view.save_button.clicked.connect(self.handle_save_settings)
        self.settings_view.back_button.clicked.connect(self.show_chat)

    def handle_login(self):  # Xử lý login (mock)
        username = self.login_view.username_input.text()
        password = self.login_view.password_input.text()
        if username == 'admin' and password == '123':  # Mock success
            self.setCentralWidget(self.chat_view)
            self.chat_view.add_bot_message("Chào mừng! Tôi sẵn sàng chat.")
        else:
            self.login_view.error_label.setText("Sai! Dùng admin/123")

    def handle_register(self):
        pass  # Placeholder

    def handle_send_message(self):
        text = self.chat_view.message_input.text().strip()
        if text:
            self.chat_view.add_user_message(text)
            self.chat_view.message_input.clear()
            self.chat_view.show_loading()
            QTimer.singleShot(500, lambda: self._process_bot_response(text))

    def _process_bot_response(self, message):
        bot_response = self.api.send_message(message)
        self.chat_view.add_bot_message(bot_response)
        self.chat_view.hide_loading()

    def show_settings(self):
        self.settings_view.load_config()
        self.setCentralWidget(self.settings_view)

    def handle_save_settings(self):
        self.settings_view.save_config()
        config = load_config()
        self.setStyleSheet(load_stylesheet(config['theme']))  # Reload theme
        self.api.update_server_url(config['server_url'])
        self.show_chat()

    def show_chat(self):
        self.setCentralWidget(self.chat_view)


# ⚙️ Phần này PHẢI đặt ngoài class MainApp
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()   # Khởi tạo cửa sổ chính
    window.show()        # Hiển thị giao diện
    sys.exit(app.exec()) # Vòng lặp chính
