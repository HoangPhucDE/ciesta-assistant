from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt

class LoginView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(20)

        self.title = QLabel("🤖 AI Chatbot")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; color: #00d4ff;")
        self.layout.addWidget(self.title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username (admin)")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Password (123)")
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.layout.addWidget(self.login_button)

        self.register_button = QPushButton("Register")
        self.layout.addWidget(self.register_button)

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        self.layout.addWidget(self.error_label)

        self.setLayout(self.layout)