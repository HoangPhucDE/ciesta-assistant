# 🌙 **Ciesta Assistant**

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20Windows%20|%20macOS-lightgrey)
![Status](https://img.shields.io/badge/status-active-brightgreen)

> **Ciesta Assistant** là một **trợ lý AI mã nguồn mở** dành cho **Linux** và **đa nền tảng**, được phát triển với mục tiêu trở thành **nền tảng chatbot thông minh, thân thiện và dễ mở rộng** cho người dùng và nhà phát triển.

---

## 🧠 **Tổng quan**

**Ciesta Assistant** là chatbot hoạt động **cục bộ (local)**, sử dụng **PyQt5** cho giao diện người dùng và **Rasa** cho xử lý ngôn ngữ tự nhiên (NLP).  
Dự án hướng đến mô hình **Hybrid AI** – kết hợp giữa **AI cục bộ** và **dịch vụ AI đám mây** (OpenAI, Gemini, Ollama, v.v.) để tối ưu hóa khả năng phản hồi và khả năng tùy biến.

---

## ⚙️ **Kiến trúc hệ thống**

Dự án được thiết kế theo mô hình **MVC (Model – View – Controller)**, giúp tách biệt rõ ràng các tầng chức năng và dễ dàng mở rộng trong tương lai.

- **Model:** Quản lý dữ liệu, NLP (Rasa), database, cấu hình hệ thống.  
- **View:** Giao diện đồ họa được phát triển bằng **PyQt5 / PySide6**.  
- **Controller:** Xử lý logic, sự kiện người dùng và giao tiếp giữa View ↔ Backend.

---

## 🧩 **Thành phần chính**

| Thành phần           | Công nghệ               | Mô tả |
| -------------------- | ----------------------- | ------ |
| **Frontend**         | PyQt5 / PySide6         | Giao diện người dùng đa nền tảng |
| **Backend**          | Python 3.x              | Xử lý luồng hội thoại, tương tác dữ liệu |
| **NLP Engine**       | Rasa                    | Phân tích và hiểu ngôn ngữ tự nhiên |
| **Database**         | SQLite / SQLAlchemy     | Lưu trữ hội thoại, cấu hình người dùng |
| **Speech (TTS/STT)** | gTTS, SpeechRecognition | Chuyển đổi giọng nói đầu vào / đầu ra |
| **Build**            | Flatpak / PyInstaller   | Đóng gói và triển khai đa nền tảng |

---

# 🧠 Ciesta Assistant — Project Structure (MVC + DevContainer)

ciesta-assistant/
├── .devcontainer/                 # 🐳 Cấu hình cho VS Code DevContainer
│   ├── devcontainer.json
│   └── Dockerfile
│
├── ciesta/                        # 🌐 Core source code (MVC structure)
│   ├── model/                     # 📘 M - Data, NLP, AI models
│   │   ├── __init__.py
│   │   ├── nlp_model.py           # Xử lý NLP bằng Rasa / spaCy / Transformers
│   │   ├── user_data.py           # Lưu và truy xuất dữ liệu người dùng
│   │   └── settings_model.py      # Model cho cấu hình hệ thống
│   │
│   ├── view/                      # 🪟 V - Giao diện người dùng (PyQt / QML)
│   │   ├── __init__.py
│   │   ├── main_window.py         # Giao diện chính chatbot
│   │   ├── chat_view.py           # Khung hội thoại
│   │   ├── settings_view.py       # Giao diện cấu hình
│   │   └── assets/                # Icon, hình ảnh, CSS/QSS
│   │       ├── icons/
│   │       └── styles/
│   │
│   ├── controller/                # 🧩 C - Xử lý logic giữa View và Model
│   │   ├── __init__.py
│   │   ├── chat_controller.py     # Kết nối NLP model và view chat
│   │   ├── settings_controller.py # Điều khiển phần cài đặt
│   │   └── system_controller.py   # Điều khiển API, IO, đa nền tảng
│   │
│   ├── core/                      # ⚙️ Chức năng lõi của ứng dụng
│   │   ├── __init__.py
│   │   ├── config.py              # Cấu hình toàn hệ thống
│   │   ├── logger.py              # Ghi log
│   │   ├── utils.py               # Tiện ích chung
│   │   └── platform_integration.py# Xử lý đa hệ điều hành (Linux/macOS/Windows)
│   │
│   └── main.py                    # Điểm khởi chạy ứng dụng
│
├── rasa/                          # 💬 NLP Backend (Rasa project folder)
│   ├── domain.yml
│   ├── config.yml
│   ├── data/
│   │   ├── nlu.yml
│   │   └── stories.yml
│   └── actions/
│       └── actions.py
│
├── tests/                         # 🧪 Unit tests & integration tests
│   ├── test_chat_controller.py
│   ├── test_nlp_model.py
│   └── test_ui_launch.py
│
├── requirements.txt               # 📦 Python dependencies
├── README.md                      # 📖 Giới thiệu dự án
├── LICENSE                        # ⚖️ Giấy phép
└── .gitignore


## 🚀 **Cài đặt**

### 1️⃣ Clone dự án
```bash
git clone https://github.com/<your-username>/ciesta-assistant.git
cd ciesta-assistant

2️⃣ Tạo môi trường và cài đặt dependencies
python3 -m venv venv
source venv/bin/activate   # Trên Linux/macOS
venv\Scripts\activate      # Trên Windows

pip install -r requirements.txt

3️⃣ Khởi chạy Rasa server

cd ciesta/rasa
rasa train
rasa run --enable-api

4️⃣ Chạy ứng dụng chính

python run.py

💬 Tính năng nổi bật

💡 Gửi và nhận tin nhắn theo thời gian thực

🌗 Giao diện chế độ tối / sáng linh hoạt

🗣️ Hỗ trợ giọng nói (TTS/STT – đang phát triển)

🧠 NLP nội bộ bằng Rasa + mở rộng với AI đám mây

⚙️ Tùy chỉnh và lưu hội thoại / cấu hình cá nhân

🧱 Hướng phát triển tương lai

Tích hợp Rust Core Engine – tăng hiệu năng xử lý

Xây dựng plugin system – mở rộng tính năng dễ dàng

Hỗ trợ Flatpak chính thức trên Linux

Phát triển API mở cho developer bên thứ ba

Tích hợp điều khiển bằng giọng nói toàn diện

🛠️ Công cụ cho lập trình viên

| Script                     | Mô tả                               |
| -------------------------- | ----------------------------------- |
| `scripts/run_rasa.sh`      | Chạy server NLP Rasa                |
| `scripts/build_flatpak.sh` | Đóng gói ứng dụng dạng Flatpak      |
| `scripts/dev_setup.sh`     | Cài đặt môi trường phát triển nhanh |

🧑‍💻 Đóng góp

Mọi đóng góp đều được hoan nghênh 💜
Hãy fork dự án, tạo branch mới, và gửi Pull Request về repository chính:

git checkout -b feature/my-improvement
git commit -m "Add: new feature"
git push origin feature/my-improvement

📄 Giấy phép

Phát hành theo MIT License –
Bạn được phép sử dụng, chỉnh sửa và phân phối lại tự do,
miễn là ghi nguồn gốc dự án Ciesta Assistant.

🪶 Tác giả

Nguyễn Hoàng Phúc
📧 Liên hệ qua GitHub Issues

