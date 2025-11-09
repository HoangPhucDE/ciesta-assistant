# 🔧 Fix Lỗi Cài Đặt Dependencies trên Colab

## ⚠️ Vấn Đề

Lỗi khi cài đặt dependencies trên Colab:
- Python 3.12 không tương thích với một số packages
- Nested directory `/content/ciesta-assistant/ciesta-assistant`
- Pip install fail với exit code 1

## ✅ Giải Pháp

### Cách 1: Sử dụng requirements-colab.txt (Khuyến nghị)

Script đã được cập nhật để tự động sử dụng `requirements-colab.txt` trên Colab (tương thích Python 3.12).

```python
# Clone repo
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# Chạy script (sẽ tự động dùng requirements-colab.txt)
!python scripts/training/train_on_colab.py
```

### Cách 2: Cài đặt thủ công từ requirements-colab.txt

```python
# Clone và chuyển vào thư mục
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# Cài đặt dependencies từ requirements-colab.txt
%pip install -r requirements-colab.txt
```

### Cách 3: Tránh nested directory

```python
# Kiểm tra thư mục hiện tại
import os
print(f"Thư mục hiện tại: {os.getcwd()}")

# Nếu đang ở trong nested directory, chuyển ra ngoài
if os.getcwd().endswith("/ciesta-assistant/ciesta-assistant"):
    %cd ..
    print(f"Đã chuyển ra: {os.getcwd()}")

# Hoặc xóa và clone lại
!rm -rf ciesta-assistant
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
```

### Cách 4: Cài đặt từng package quan trọng

```python
# Cài đặt các package cốt lõi trước
%pip install rasa==3.6.20 rasa-sdk==3.6.2
%pip install transformers==4.35.2 torch==2.1.2
%pip install numpy faiss-cpu
%pip install huggingface_hub

# Cài đặt các package còn lại
%pip install -r requirements-colab.txt
```

## 🔍 Kiểm Tra

```python
import sys
print(f"Python version: {sys.version}")

# Kiểm tra các package đã cài
import subprocess
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
print(result.stdout)
```

## 📝 requirements-colab.txt

File `requirements-colab.txt` đã được tạo với:
- Loại bỏ các package không cần thiết cho Colab (PySide6, GUI, dev tools)
- Tương thích với Python 3.12
- Chỉ bao gồm các package cần thiết cho training

## 🚀 Quick Fix

```python
# Setup đầy đủ
import os
from pathlib import Path

# Xóa nested directory nếu có
if Path("ciesta-assistant/ciesta-assistant").exists():
    !rm -rf ciesta-assistant/ciesta-assistant

# Clone nếu chưa có
if not Path("ciesta-assistant").exists():
    !git clone https://github.com/HoangPhucDE/ciesta-assistant.git

# Chuyển vào thư mục
%cd ciesta-assistant

# Cài đặt từ requirements-colab.txt
%pip install -r requirements-colab.txt

# Chạy training
!python scripts/training/train_on_colab.py
```

## ⚠️ Lưu Ý

1. **Python 3.12**: Colab mặc định dùng Python 3.12, một số packages có thể không tương thích
2. **Nested directory**: Tránh clone 2 lần vào cùng một thư mục
3. **Memory**: Một số packages lớn có thể cần nhiều RAM
4. **Timeout**: Cài đặt có thể mất vài phút, đừng ngắt kết nối

## 🔗 Xem thêm

- [FIX_COLAB.md](FIX_COLAB.md) - Fix lỗi khác
- [QUICK_START_COLAB.md](QUICK_START_COLAB.md) - Hướng dẫn nhanh

