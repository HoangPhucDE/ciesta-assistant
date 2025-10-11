from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QListWidget, 
                             QListWidgetItem, QLineEdit, QPushButton)
from PySide6.QtCore import Qt, QTimer

class ChatView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        self.title = QLabel("🤖 Chat")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.settings_button = QPushButton("⚙️")
        self.settings_button.setFixedSize(40, 40)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_button)
        self.layout.addLayout(header_layout)

        # Chat area
        self.chat_area = QScrollArea()
        self.chat_list = QListWidget()
        self.chat_list.setWordWrap(True)
        self.chat_list.setSpacing(15)
        self.chat_area.setWidget(self.chat_list)
        self.chat_area.setWidgetResizable(True)
        self.layout.addWidget(self.chat_area, 1)

        # Input
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type message...")
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(60, 40)
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        self.layout.addLayout(input_layout)

        # Loading
        self.loading_label = QLabel("🤖 Thinking...")
        self.loading_label.hide()
        self.layout.addWidget(self.loading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self.layout)

    def add_user_message(self, text):
        bubble = QLabel(text)
        bubble.setStyleSheet("background: #00d4ff; border-radius: 10px; padding: 10px; color: white; margin-left: 30%;")
        item = QListWidgetItem()
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.scroll_to_bottom()

    def add_bot_message(self, text):
        bubble = QLabel(text)
        bubble.setStyleSheet("background: #2a2a2a; border-radius: 10px; padding: 10px; color: white;")
        item = QListWidgetItem()
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.scroll_to_bottom()

    def show_loading(self):
        self.loading_label.show()
        self.scroll_to_bottom()

    def hide_loading(self):
        self.loading_label.hide()

    def scroll_to_bottom(self):
        QTimer.singleShot(0, lambda: self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum()))