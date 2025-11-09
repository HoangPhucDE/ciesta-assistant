# ============================================
# SETUP VÀ TRAIN - COLAB
# ============================================

import os
import shutil
import re
from pathlib import Path

# Bước 1: Cleanup và Clone
print("🧹 Dọn dẹp thư mục cũ...")
# Xóa tất cả nested directories
base_path = Path("/content")
for path in base_path.glob("ciesta-assistant*"):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
        print(f"   ✅ Đã xóa {path}")

# Đảm bảo đang ở /content
os.chdir("/content")
print(f"   Thư mục hiện tại: {os.getcwd()}")

!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
current_dir = Path.cwd()
print(f"✅ Thư mục: {current_dir}")

# Đảm bảo đang ở đúng thư mục root (không phải nested)
while (current_dir / "ciesta-assistant").exists() and current_dir.name == "ciesta-assistant":
    parent = current_dir.parent
    if (parent / "ciesta-assistant").exists() and parent.name != "ciesta-assistant":
        # Đang ở trong nested directory, cần lên 1 level
        %cd ..
        current_dir = Path.cwd()
        print(f"   ⚠️ Phát hiện nested directory, đã chuyển lên: {current_dir}")
    else:
        break

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

# Đảm bảo đang ở đúng thư mục root của project
current_dir = Path.cwd()
print(f"   Thư mục hiện tại: {current_dir}")

# Tìm file config (có thể ở root hoặc trong config/rasa/)
config_paths = [
    current_dir / "config.yml",
    current_dir / "config/rasa/config.yml",
]

config_file = None
config_path_used = None

for path in config_paths:
    if path.exists():
        config_file = str(path)
        config_path_used = path
        print(f"   ✅ Tìm thấy config tại: {path}")
        break

if not config_file:
    print("❌ Không tìm thấy config.yml")
    print("   Đang tìm trong:")
    for path in config_paths:
        exists = path.exists()
        print(f"   - {path} ({'tồn tại' if exists else 'không tồn tại'})")
        if exists:
            print(f"     Absolute: {path.resolve()}")
    raise FileNotFoundError("Không tìm thấy config.yml")

# Nếu config ở trong config/rasa/, tạo symlink ở root để Rasa tìm thấy
root_config = current_dir / "config.yml"
rasa_config = current_dir / "config/rasa/config.yml"

if config_path_used == rasa_config:
    print(f"   Tạo symlink/copy từ {rasa_config} -> {root_config}")
    
    # Xóa file cũ nếu tồn tại (symlink hoặc file thường)
    if root_config.exists():
        try:
            root_config.unlink()  # Xóa file hoặc symlink
            print("   ✅ Đã xóa file/symlink cũ")
        except Exception as e:
            print(f"   ⚠️ Không thể xóa file cũ: {e}")
    
    # Thử tạo symlink trước
    try:
        os.symlink("config/rasa/config.yml", "config.yml")
        config_file = "config.yml"
        print("   ✅ Đã tạo symlink config.yml")
    except (FileExistsError, OSError) as e:
        print(f"   ⚠️ Không thể tạo symlink (có thể do Colab filesystem): {e}")
        # Nếu không tạo được symlink, copy file (đảm bảo hoạt động)
        try:
            shutil.copy(rasa_config, root_config)
            config_file = "config.yml"
            print("   ✅ Đã copy config.yml")
        except Exception as e2:
            print(f"   ❌ Không thể copy file: {e2}")
            # Fallback: dùng file gốc
            config_file = str(rasa_config)
            print(f"   ⚠️ Sẽ dùng file gốc: {config_file}")

# Tạo symlink hoặc copy cho các file config khác nếu cần
rasa_config_files = ["domain.yml", "endpoints.yml", "credentials.yml"]
for filename in rasa_config_files:
    rasa_path = current_dir / "config/rasa" / filename
    root_path = current_dir / filename
    
    if rasa_path.exists():
        # Xóa file cũ nếu tồn tại
        if root_path.exists():
            try:
                root_path.unlink()  # Xóa file hoặc symlink
            except Exception:
                pass
        
        if not root_path.exists():
            print(f"   Tạo symlink từ config/rasa/{filename} -> {filename}")
            try:
                os.symlink(f"config/rasa/{filename}", filename)
                print(f"   ✅ Đã tạo symlink {filename}")
            except (FileExistsError, OSError) as e:
                # Nếu không tạo được symlink, copy file (đảm bảo hoạt động)
                try:
                    shutil.copy(rasa_path, root_path)
                    print(f"   ✅ Đã copy {filename}")
                except Exception as e2:
                    print(f"   ⚠️ Không thể tạo {filename}: {e2}")

# Đọc và cập nhật config (đảm bảo dùng file ở root)
config_to_update = current_dir / "config.yml"
if not config_to_update.exists():
    # Nếu không có ở root, dùng file gốc
    config_to_update = config_path_used
    print(f"   ⚠️ Không tìm thấy config.yml ở root, dùng: {config_to_update}")

print(f"   Đang cập nhật: {config_to_update}")

# Đọc config
with open(config_to_update, "r", encoding="utf-8") as f:
    config = f.read()

# Cập nhật config
config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

# Ghi lại config
with open(config_to_update, "w", encoding="utf-8") as f:
    f.write(config)

# Nếu đã copy/symlink từ config/rasa/, cũng cập nhật file gốc
if config_path_used == rasa_config and config_to_update == root_config:
    # Cũng cập nhật file gốc trong config/rasa/
    with open(rasa_config, "w", encoding="utf-8") as f:
        f.write(config)
    print("   ✅ Đã cập nhật cả file gốc trong config/rasa/")

print("✅ Đã cập nhật config để dùng model online")

# Bước 6: Train NLU
print("\n🚀 Bắt đầu training...")
print("💡 Quá trình này có thể mất 30 phút - 2 giờ")
!venv_py310/bin/python -m rasa train nlu

# Bước 7: Download model
print("\n📥 Tải model về máy...")
from google.colab import files

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

