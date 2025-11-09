# ⚡ Copy-Paste Nhanh cho Colab

## 🚀 Cách 1: Copy từ file Python (KHUYẾN NGHỊ - TRÁNH LỖI)
1. Mở file `colab_setup_train.py` trong thư mục này
2. Copy toàn bộ nội dung (Ctrl+A, Ctrl+C)
3. Paste vào 1 cell Python trên Colab
4. Chạy cell

**Ưu điểm**: Không có markdown syntax, không có ký tự đặc biệt, copy trực tiếp không lỗi!

## 🚀 Cách 2: Copy từ block code bên dưới
**⚠️ QUAN TRỌNG: Chỉ copy code trong block Python bên dưới, KHÔNG copy dấu ``` (backticks) và phần Markdown!**

```python
# ============================================
# SETUP VÀ TRAIN - COLAB
# ============================================

import os
from pathlib import Path
import re

# Bước 1: Cleanup và Clone
if Path("ciesta-assistant").exists():
    !rm -rf ciesta-assistant

!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
print(f"✅ Thư mục: {os.getcwd()}")

# Bước 2: Cài đặt Python 3.10 (QUAN TRỌNG!)
print("\n🐍 Cài đặt Python 3.10...")
!apt-get update -qq
!apt-get install -y -qq python3.10 python3.10-venv python3.10-dev

# Bước 3: Tạo virtual environment
print("\n📦 Tạo virtual environment...")
!python3.10 -m venv venv_py310

# Bước 4: Cài đặt dependencies
print("\n📦 Cài đặt dependencies...")
!venv_py310/bin/pip install --upgrade pip
!venv_py310/bin/pip install -r requirements.txt

# Bước 5: Cập nhật config để dùng model online
print("\n⚙️ Cập nhật config...")
with open("config.yml", "r") as f:
    config = f.read()

config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

with open("config.yml", "w") as f:
    f.write(config)
print("✅ Đã cập nhật config để dùng model online")

# Bước 6: Train NLU
print("\n🚀 Bắt đầu training...")
print("💡 Quá trình này có thể mất 30 phút - 2 giờ")
!venv_py310/bin/python -m rasa train nlu

# Bước 7: Download model
print("\n📥 Tải model về máy...")
from google.colab import files
from pathlib import Path

models = list(Path("models").glob("*.tar.gz"))
if models:
    latest = max(models, key=lambda x: x.stat().st_mtime)
    size_mb = latest.stat().st_size / (1024*1024)
    print(f"📦 Model: {latest.name} ({size_mb:.2f} MB)")
    files.download(str(latest))
    print("✅ Đã bắt đầu tải model về máy")
else:
    print("❌ Không tìm thấy model")

print("\n🎉 Hoàn tất!")
```

## 📝 Giải Thích

1. **Cleanup**: Xóa thư mục cũ nếu có (tránh nested directory)
2. **Clone**: Clone repository từ GitHub
3. **Python 3.10**: Cài đặt Python 3.10 (Rasa 3.6.20 cần Python 3.8-3.10)
4. **Virtual Environment**: Tạo venv với Python 3.10
5. **Dependencies**: Cài đặt tất cả packages
6. **Config**: Cập nhật để dùng model online (không cần download trước)
7. **Train**: Train NLU model
8. **Download**: Tải model đã train về máy

## ⚠️ Lưu Ý

- **Python 3.10**: Bắt buộc phải dùng Python 3.10
- **Model online**: Config đã được cập nhật để dùng model từ HuggingFace
- **GPU**: Bật GPU để train nhanh hơn (Runtime -> Change runtime type -> GPU)
- **Thời gian**: Training mất 30 phút - 2 giờ tùy vào GPU

## 🔧 Troubleshooting

### Lỗi: SyntaxError: invalid character hoặc invalid syntax
**Nguyên nhân**: Đã copy cả markdown syntax (```) hoặc ký tự đặc biệt vào cell Python.

**Giải pháp**: 
- **Sử dụng file `colab_setup_train.py`** (Cách 1) - đảm bảo không có lỗi
- Hoặc chỉ copy phần code giữa 2 dấu ```, KHÔNG copy dấu ``` vào cell Python

### Lỗi: ERROR: Cannot install regex - conflicting dependencies
**Nguyên nhân**: `regex==2024.5.15` không tương thích với `rasa 3.6.20` (rasa yêu cầu `regex<2022.11`).

**Giải pháp**: 
- File `requirements.txt` đã được cập nhật với `regex==2022.9.13` (tương thích với rasa 3.6.20)
- Pull code mới nhất từ repo hoặc cập nhật requirements.txt thủ công:
  ```bash
  regex==2022.9.13
  ```

### Lỗi: FileNotFoundError: config.yml
**Nguyên nhân**: File config không ở root, mà nằm trong `config/rasa/config.yml`.

**Giải pháp**: 
- Script đã được cập nhật để tự động tìm và tạo symlink từ `config/rasa/config.yml` -> `config.yml`
- Đảm bảo bạn đang dùng phiên bản mới nhất của script

### Lỗi: Nested directory
```python
# Xóa và clone lại
!rm -rf ciesta-assistant
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
```

### Lỗi: Python version
```python
# Kiểm tra Python version
import sys
print(sys.version)

# Phải là Python 3.10 trong venv
!venv_py310/bin/python --version
```

### Lỗi: Rasa không cài được
```python
# Cài đặt lại trong venv
!venv_py310/bin/pip install rasa==3.6.20 rasa-sdk==3.6.2
```

