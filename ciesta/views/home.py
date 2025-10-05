import sys
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton

class RasaChat(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ciesta Assistant")
        self.resize(400, 500)

        self.layout = QVBoxLayout()
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)

        self.user_input = QLineEdit()
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)

        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.user_input)
        self.layout.addWidget(self.send_btn)
        self.setLayout(self.layout)

        # URL Rasa REST API
        self.rasa_url = "http://localhost:5005/webhooks/rest/webhook"

    def send_message(self):
        message = self.user_input.text().strip()
        if not message:
            return
        self.chat_history.append(f"You: {message}")

        try:
            response = requests.post(
                self.rasa_url,
                json={"sender": "user", "message": message},
                timeout=30
            )
            data = response.json()
            for r in data:
                self.chat_history.append(f"Bot: {r.get('text', '')}")
        except Exception as e:
            self.chat_history.append(f"Error: {e}")

        self.user_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RasaChat()
    window.show()
    sys.exit(app.exec())
