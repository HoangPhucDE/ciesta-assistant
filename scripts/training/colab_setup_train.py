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

# Tìm file config (có thể ở root hoặc trong config/rasa/)
config_paths = ["config.yml", "config/rasa/config.yml"]
config_file = None

for path in config_paths:
    if Path(path).exists():
        config_file = path
        break

if not config_file:
    print("❌ Không tìm thấy config.yml")
    print("   Đang tìm trong:")
    for path in config_paths:
        print(f"   - {path} ({'tồn tại' if Path(path).exists() else 'không tồn tại'})")
    raise FileNotFoundError("Không tìm thấy config.yml")

# Nếu config ở trong config/rasa/, tạo symlink ở root để Rasa tìm thấy
if config_file == "config/rasa/config.yml" and not Path("config.yml").exists():
    print("   Tạo symlink từ config/rasa/config.yml -> config.yml")
    try:
        os.symlink("config/rasa/config.yml", "config.yml")
    except FileExistsError:
        pass  # File đã tồn tại
    config_file = "config.yml"

# Tạo symlink cho các file config khác nếu cần
rasa_config_files = ["domain.yml", "endpoints.yml", "credentials.yml"]
for filename in rasa_config_files:
    rasa_path = f"config/rasa/{filename}"
    if Path(rasa_path).exists() and not Path(filename).exists():
        print(f"   Tạo symlink từ {rasa_path} -> {filename}")
        try:
            os.symlink(rasa_path, filename)
        except FileExistsError:
            pass

# Đọc và cập nhật config
with open(config_file, "r") as f:
    config = f.read()

config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

with open(config_file, "w") as f:
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

