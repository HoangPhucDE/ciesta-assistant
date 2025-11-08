# ⚡ Copy-Paste Nhanh cho Colab

## 🚀 Setup và Train (Copy toàn bộ vào 1 cell)

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
- **GPU**: Bật GPU để train nhanh hơn (Runtime → Change runtime type → GPU)
- **Thời gian**: Training mất 30 phút - 2 giờ tùy vào GPU

## 🔧 Troubleshooting

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

