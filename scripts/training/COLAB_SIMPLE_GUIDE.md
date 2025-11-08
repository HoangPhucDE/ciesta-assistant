# 🚀 Hướng Dẫn Train Đơn Giản Trên Colab

## ⚠️ Vấn Đề Hiện Tại

1. **Python 3.12** không tương thích với **Rasa 3.6.20** (cần Python 3.8-3.10)
2. **Nested directory** khi clone nhiều lần
3. Script phức tạp, khó debug

## ✅ Giải Pháp Đơn Giản

### Cách 1: Sử dụng Python 3.10 (Khuyến nghị)

```python
# ============================================
# SETUP VÀ TRAIN - COPY TOÀN BỘ
# ============================================

# Bước 1: Clone repo (CHỈ CHẠY 1 LẦN)
import os
from pathlib import Path

# Xóa nếu đã clone trước đó
if Path("ciesta-assistant").exists():
    !rm -rf ciesta-assistant

# Clone
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git

# Chuyển vào thư mục
%cd ciesta-assistant
print(f"✅ Thư mục: {os.getcwd()}")

# Bước 2: Cài đặt Python 3.10
!apt-get update -qq
!apt-get install -y -qq python3.10 python3.10-venv python3.10-dev

# Bước 3: Tạo virtual environment Python 3.10
!python3.10 -m venv venv_py310

# Bước 4: Activate virtual environment
import sys
sys.path.insert(0, 'venv_py310/lib/python3.10/site-packages')

# Bước 5: Cài đặt dependencies
!venv_py310/bin/pip install --upgrade pip
!venv_py310/bin/pip install -r requirements.txt

# Bước 6: Cập nhật config để dùng model online
import re
with open("config.yml", "r") as f:
    config = f.read()

# Thay đổi để dùng model online
config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

with open("config.yml", "w") as f:
    f.write(config)

print("✅ Đã cập nhật config để dùng model online")

# Bước 7: Train NLU
!venv_py310/bin/python -m rasa train nlu

# Bước 8: Download model
from google.colab import files
from pathlib import Path

models = list(Path("models").glob("*.tar.gz"))
if models:
    latest = max(models, key=lambda x: x.stat().st_mtime)
    files.download(str(latest))
    print(f"✅ Đã tải model: {latest.name}")
```

### Cách 2: Dùng Script Đơn Giản

```python
# Clone repo
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# Chạy script đơn giản
!python scripts/training/colab_train_simple.py
```

## 📋 Checklist

- [ ] Đã clone repo (CHỈ 1 LẦN)
- [ ] Đã chuyển vào thư mục `ciesta-assistant`
- [ ] Đã cài đặt Python 3.10
- [ ] Đã tạo virtual environment
- [ ] Đã cài đặt dependencies
- [ ] Đã cập nhật config để dùng model online
- [ ] Đã train NLU
- [ ] Đã download model

## 🔧 Troubleshooting

### Lỗi: Nested directory

```python
# Xóa và clone lại
!rm -rf ciesta-assistant
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
```

### Lỗi: Python 3.12 không tương thích

```python
# Cài đặt Python 3.10
!apt-get update -qq
!apt-get install -y -qq python3.10 python3.10-venv

# Tạo venv
!python3.10 -m venv venv_py310

# Sử dụng venv
!venv_py310/bin/pip install -r requirements.txt
!venv_py310/bin/python -m rasa train nlu
```

### Lỗi: Rasa không cài được

```python
# Kiểm tra Python version
import sys
print(sys.version)

# Phải là Python 3.10 hoặc thấp hơn
# Nếu là 3.12, cần dùng Python 3.10 như trên
```

## 💡 Tips

1. **Chỉ clone 1 lần**: Kiểm tra xem đã có thư mục chưa trước khi clone
2. **Dùng model online**: Không cần download model trước, Rasa sẽ tự động tải
3. **Python 3.10**: Bắt buộc phải dùng Python 3.10 để train Rasa 3.6.20
4. **GPU**: Bật GPU để train nhanh hơn (Runtime → Change runtime type → GPU)

## 🚀 Quick Start (Copy toàn bộ)

```python
# Setup và train trong 1 cell
import os
from pathlib import Path

# Cleanup
if Path("ciesta-assistant").exists():
    !rm -rf ciesta-assistant

# Clone
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# Setup Python 3.10
!apt-get update -qq && apt-get install -y -qq python3.10 python3.10-venv python3.10-dev
!python3.10 -m venv venv_py310
!venv_py310/bin/pip install --upgrade pip
!venv_py310/bin/pip install -r requirements.txt

# Update config for online model
import re
with open("config.yml", "r") as f:
    config = f.read()
config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)
with open("config.yml", "w") as f:
    f.write(config)

# Train
!venv_py310/bin/python -m rasa train nlu

# Download
from google.colab import files
from pathlib import Path
models = list(Path("models").glob("*.tar.gz"))
if models:
    files.download(str(max(models, key=lambda x: x.stat().st_mtime)))
```

