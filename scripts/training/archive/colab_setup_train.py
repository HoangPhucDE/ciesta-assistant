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
print("⚠️ QUAN TRỌNG: Quá trình này có thể mất 10-20 phút, KHÔNG interrupt!")
print("   Để cài đặt chạy đến khi hoàn tất...")

# Upgrade pip
print("\n🔄 Upgrade pip...")
!venv_py310/bin/pip install --upgrade pip --quiet

# Cài đặt dependencies với error handling
print("\n📥 Cài đặt packages từ requirements.txt...")
print("   (Quá trình này có thể mất 10-20 phút, vui lòng đợi...)")

# Import subprocess (nếu chưa import)
import subprocess
import os

pip_process = subprocess.run(
    ["venv_py310/bin/pip", "install", "-r", "requirements.txt"],
    cwd=str(current_dir),
    capture_output=False,  # Hiển thị output real-time
    text=True
)

if pip_process.returncode != 0:
    print("\n❌ Lỗi khi cài đặt dependencies!")
    print("   Vui lòng chạy lại script từ đầu")
    print("   Hoặc cài đặt thủ công: !venv_py310/bin/pip install -r requirements.txt")
    raise RuntimeError("Failed to install dependencies")

print("\n✅ Đã cài đặt dependencies thành công!")

# Kiểm tra các packages quan trọng đã được cài đặt
print("\n🔍 Kiểm tra packages quan trọng...")
check_packages = """
import sys
sys.path.insert(0, 'venv_py310/lib/python3.10/site-packages')
packages = ['rasa', 'torch', 'transformers']
missing = []
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
    except ImportError:
        print(f"❌ {pkg} - CHƯA CÀI ĐẶT")
        missing.append(pkg)

if missing:
    sys.exit(1)
"""
with open("/tmp/check_packages.py", "w") as f:
    f.write(check_packages)

result = subprocess.run(
    ["venv_py310/bin/python", "/tmp/check_packages.py"],
    cwd=str(current_dir),
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(result.stdout)
    print("\n❌ Một số packages quan trọng chưa được cài đặt!")
    print("   ⚠️ Vui lòng chạy lại script từ đầu và đợi cài đặt hoàn tất")
    print("   ⚠️ KHÔNG interrupt quá trình cài đặt (có thể mất 10-20 phút)")
    raise RuntimeError("Critical packages not installed")
else:
    print(result.stdout)
    print("✅ Tất cả packages quan trọng đã được cài đặt")

# Bước 4.5: Kiểm tra GPU (sau khi đã cài đặt PyTorch)
print("\n🎮 Kiểm tra GPU...")
print("=" * 60)

# Kiểm tra GPU bằng nvidia-smi
nvidia_result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
if nvidia_result.returncode == 0:
    print("✅ GPU được phát hiện:")
    print(nvidia_result.stdout)
else:
    print("❌ Không tìm thấy GPU!")
    print("\n⚠️ QUAN TRỌNG: Để sử dụng GPU trên Colab:")
    print("   1. Vào menu: Runtime → Change runtime type")
    print("   2. Chọn 'Hardware accelerator': GPU")
    print("   3. Chọn GPU type: T4 (miễn phí) hoặc A100/V100 (trả phí)")
    print("   4. Click 'Save'")
    print("   5. Chạy lại script từ đầu")
    print("\n💡 Training sẽ chạy trên CPU (chậm hơn) nếu không có GPU")

# Kiểm tra PyTorch có detect GPU không (sau khi đã cài đặt)
print("\n🔍 Kiểm tra PyTorch GPU support...")
check_gpu_script = """
import sys
import os
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, venv_path)

try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ PyTorch phát hiện GPU: {torch.cuda.get_device_name(0)}")
        print(f"   GPU Count: {torch.cuda.device_count()}")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        print("❌ PyTorch KHÔNG phát hiện GPU")
        print("   Có thể do:")
        print("   1. Chưa bật GPU runtime trên Colab")
        print("   2. Hoặc Colab free tier không có GPU available")
except ImportError as e:
    print(f"⚠️ PyTorch chưa được cài đặt: {e}")
    print("   Script sẽ dừng lại - vui lòng chạy lại và đợi cài đặt hoàn tất")
    sys.exit(1)
"""
with open("/tmp/check_gpu.py", "w") as f:
    f.write(check_gpu_script)

gpu_check_result = subprocess.run(
    ["venv_py310/bin/python", "/tmp/check_gpu.py"],
    cwd=str(current_dir),
    capture_output=True,
    text=True
)

print(gpu_check_result.stdout)
if gpu_check_result.stderr:
    print(gpu_check_result.stderr)

if gpu_check_result.returncode != 0:
    print("\n⚠️ PyTorch chưa được cài đặt hoàn chỉnh")
    print("   Vui lòng chạy lại script từ đầu và đợi cài đặt hoàn tất")

print("=" * 60)

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

# Nếu config ở trong config/rasa/, copy vào root để Rasa tìm thấy
# Colab filesystem không hỗ trợ symlink tốt, nên dùng copy
root_config = current_dir / "config.yml"
rasa_config = current_dir / "config/rasa/config.yml"

if config_path_used == rasa_config:
    print(f"   Copy config từ {rasa_config} -> {root_config}")
    
    # Xóa file cũ nếu tồn tại (kể cả broken symlink)
    # Dùng os.path.lexists để detect cả broken symlink
    root_config_str = str(root_config)
    if os.path.lexists(root_config_str):
        try:
            # Xóa file/symlink (kể cả broken)
            if os.path.islink(root_config_str):
                os.unlink(root_config_str)
                print("   ✅ Đã xóa symlink cũ")
            else:
                os.remove(root_config_str)
                print("   ✅ Đã xóa file cũ")
        except Exception as e:
            print(f"   ⚠️ Không thể xóa file cũ: {e}")
            # Thử xóa bằng shutil
            try:
                if os.path.isdir(root_config_str):
                    shutil.rmtree(root_config_str)
                else:
                    os.remove(root_config_str)
                print("   ✅ Đã force xóa file cũ")
            except Exception:
                pass
    
    # Copy file bằng shutil.copyfile (xử lý tốt hơn)
    try:
        shutil.copyfile(str(rasa_config), root_config_str)
        # Verify file đã được tạo
        if os.path.exists(root_config_str) and os.path.isfile(root_config_str):
            print("   ✅ Đã copy config.yml vào root")
            config_file = "config.yml"
        else:
            raise FileNotFoundError("File không tồn tại sau khi copy")
    except Exception as e:
        print(f"   ❌ Không thể copy file: {e}")
        print(f"   Source: {rasa_config} (exists: {rasa_config.exists()})")
        print(f"   Destination: {root_config_str}")
        print(f"   Current dir: {os.getcwd()}")
        raise FileNotFoundError(f"Không thể tạo config.yml ở root: {e}")

# Copy các file config khác vào root
rasa_config_files = ["domain.yml", "endpoints.yml", "credentials.yml"]
for filename in rasa_config_files:
    rasa_path = current_dir / "config/rasa" / filename
    root_path = current_dir / filename
    
    if rasa_path.exists():
        root_path_str = str(root_path)
        # Xóa file cũ nếu tồn tại (kể cả broken symlink)
        if os.path.lexists(root_path_str):
            try:
                if os.path.islink(root_path_str):
                    os.unlink(root_path_str)
                else:
                    os.remove(root_path_str)
            except Exception:
                pass
        
        # Copy file bằng shutil
        try:
            shutil.copyfile(str(rasa_path), root_path_str)
            if os.path.exists(root_path_str) and os.path.isfile(root_path_str):
                print(f"   ✅ Đã copy {filename} vào root")
            else:
                print(f"   ⚠️ File {filename} không tồn tại sau khi copy")
        except Exception as e:
            print(f"   ⚠️ Không thể copy {filename}: {e}")

# Đọc và cập nhật config (đảm bảo dùng file ở root)
config_to_update = current_dir / "config.yml"

# Đảm bảo config.yml tồn tại ở root
if not config_to_update.exists():
    raise FileNotFoundError("config.yml không tồn tại ở root! Đảm bảo đã copy file từ config/rasa/")

print(f"   Đang cập nhật: {config_to_update}")

# Đọc config
with open(config_to_update, "r", encoding="utf-8") as f:
    config = f.read()

# Cập nhật config
config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

# Ghi lại config vào root
with open(config_to_update, "w", encoding="utf-8") as f:
    f.write(config)

# Cũng cập nhật file gốc trong config/rasa/ để đồng bộ
if rasa_config.exists():
    with open(rasa_config, "w", encoding="utf-8") as f:
        f.write(config)
    print("   ✅ Đã cập nhật cả file gốc trong config/rasa/")

print("✅ Đã cập nhật config để dùng model online")

# Bước 5.5: Tối ưu config dựa trên GPU (nếu có)
print("\n⚡ Tối ưu config để tận dụng GPU...")

# Kiểm tra GPU memory (sau khi PyTorch đã được cài đặt)
gpu_memory_gb = None
try:
    check_gpu_memory = """
import sys
import os
# Add venv to path
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, venv_path)

try:
    import torch
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        gpu_name = torch.cuda.get_device_name(0)
        print(f"{gpu_memory:.1f}|{gpu_name}")
    else:
        print("0|No GPU")
except ImportError as e:
    print(f"0|PyTorch not installed: {e}")
except Exception as e:
    print(f"0|Error: {e}")
"""
    with open("/tmp/check_gpu_memory.py", "w") as f:
        f.write(check_gpu_memory)
    
    result = subprocess.run(
        ["venv_py310/bin/python", "/tmp/check_gpu_memory.py"],
        capture_output=True,
        text=True,
        cwd=str(current_dir),
        timeout=30
    )
    
    if result.returncode == 0 and result.stdout.strip():
        output = result.stdout.strip()
        if "|" in output:
            parts = output.split("|")
            gpu_memory_gb = float(parts[0])
            gpu_name = parts[1] if len(parts) > 1 else "Unknown"
            if gpu_memory_gb > 0:
                print(f"   GPU: {gpu_name} ({gpu_memory_gb:.1f} GB)")
        else:
            # Fallback: try to parse as float
            try:
                gpu_memory_gb = float(output)
                if gpu_memory_gb > 0:
                    print(f"   GPU Memory: {gpu_memory_gb:.1f} GB")
            except ValueError:
                pass
    else:
        print(f"   ⚠️ Không thể kiểm tra GPU memory: {result.stderr}")
except subprocess.TimeoutExpired:
    print("   ⚠️ Timeout khi kiểm tra GPU memory")
except Exception as e:
    print(f"   ⚠️ Không thể kiểm tra GPU memory: {e}")
    print("   💡 Sẽ sử dụng batch size mặc định")

# Tối ưu batch size dựa trên GPU memory
if gpu_memory_gb and gpu_memory_gb > 0:
    print(f"   GPU Memory: {gpu_memory_gb:.1f} GB")
    
    # Đọc config
    config_file = current_dir / "config.yml"
    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    original_content = config_content
    
    # Tối ưu batch size dựa trên GPU memory
    # Lưu ý: T4 thường có ~15GB nhưng có thể hiển thị 14.7-14.9 GB, nên coi >=14.5 GB là GPU lớn
    if gpu_memory_gb >= 14.5:  # T4 (~15GB), V100, A100
        # T4/V100/A100: Có thể tăng batch size lớn để tận dụng GPU
        print("   🚀 GPU lớn phát hiện (T4/V100/A100) - Tăng batch size để tận dụng GPU")
        print(f"   💡 GPU Memory: {gpu_memory_gb:.1f} GB - Có thể tăng batch size cao hơn")
        # Tối ưu PhoBERTFeaturizer batch_size (sau pooling_strategy)
        # Với T4 15GB, có thể tăng lên 128-256
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            r'\1 256  # Tối ưu cho GPU lớn (T4/V100/A100) - tận dụng GPU memory',
            config_content
        )
        # Tối ưu DIETClassifier batch_size - tăng cao hơn để training nhanh hơn
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\](\s*#.*)?',
            r'\1[256, 512]  # Tối ưu cho GPU lớn - training nhanh hơn',
            config_content
        )
        # Nếu có pattern khác như [64, 128] từ lần tối ưu trước, cũng cập nhật
        config_content = re.sub(
            r'(batch_size:\s*)\[64,\s*128\](\s*#.*)?',
            r'\1[256, 512]  # Tối ưu cho GPU lớn - training nhanh hơn',
            config_content
        )
        config_content = re.sub(
            r'(batch_size:\s*)\[128,\s*256\](\s*#.*)?',
            r'\1[256, 512]  # Tối ưu cho GPU lớn - training nhanh hơn',
            config_content
        )
    elif gpu_memory_gb >= 8:  # P100, K80, hoặc GPU trung bình
        # GPU trung bình
        print("   ⚡ GPU trung bình phát hiện - Tăng batch size vừa phải")
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            r'\1 128  # Tối ưu cho GPU trung bình',
            config_content
        )
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\](\s*#.*)?',
            r'\1[128, 256]  # Tối ưu cho GPU trung bình',
            config_content
        )
    elif gpu_memory_gb >= 4:  # GPU nhỏ
        # GPU nhỏ: giữ nguyên hoặc tăng nhẹ
        print("   📊 GPU nhỏ phát hiện - Tăng batch size nhẹ")
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            r'\1 48  # Tối ưu cho GPU nhỏ',
            config_content
        )
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\]',
            r'\1[32, 64]  # Tối ưu cho GPU nhỏ',
            config_content
        )
    else:
        print("   ℹ️ GPU memory nhỏ - Giữ batch size mặc định")
    
    # Ghi lại config nếu có thay đổi
    if config_content != original_content:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print("   ✅ Đã tối ưu batch size trong config.yml")
        print("   💡 Batch size lớn hơn sẽ:")
        print("      - Sử dụng GPU hiệu quả hơn")
        print("      - Training nhanh hơn (nhiều samples/batch)")
        print("      - Tận dụng GPU memory tốt hơn")
        
        # Cũng cập nhật file gốc trong config/rasa/ để đồng bộ
        rasa_config_path = current_dir / "config/rasa/config.yml"
        if rasa_config_path.exists():
            with open(rasa_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            print("   ✅ Đã cập nhật cả file gốc trong config/rasa/")
    else:
        print("   ℹ️ Config đã tối ưu hoặc không cần thay đổi")
else:
    print("   ℹ️ Không có GPU hoặc không thể detect GPU memory")
    print("   💡 Sẽ sử dụng batch size mặc định (phù hợp cho CPU)")

# Bước 6: Train NLU
print("\n🚀 Bắt đầu training...")
print("💡 Quá trình này có thể mất 30 phút - 2 giờ")
if gpu_memory_gb and gpu_memory_gb > 0:
    print(f"💡 GPU: {gpu_memory_gb:.1f} GB - Batch size đã được tối ưu")

# Đảm bảo config.yml tồn tại ở root trước khi train
if not (current_dir / "config.yml").exists():
    raise FileNotFoundError("config.yml không tồn tại ở root! Không thể train.")

# Kiểm tra Rasa đã được cài đặt trước khi train
print("\n🔍 Kiểm tra Rasa trước khi train...")
check_rasa = """
import sys
import os
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, venv_path)

try:
    import rasa
    print(f"✅ Rasa version: {rasa.__version__}")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Rasa chưa được cài đặt: {e}")
    sys.exit(1)
"""

with open("/tmp/check_rasa.py", "w") as f:
    f.write(check_rasa)

rasa_check = subprocess.run(
    ["venv_py310/bin/python", "/tmp/check_rasa.py"],
    cwd=str(current_dir),
    capture_output=True,
    text=True
)

print(rasa_check.stdout)
if rasa_check.stderr:
    print(rasa_check.stderr)

if rasa_check.returncode != 0:
    print("\n❌ Rasa chưa được cài đặt!")
    print("   ⚠️ Vui lòng chạy lại script từ đầu và đợi cài đặt hoàn tất")
    print("   ⚠️ KHÔNG interrupt quá trình cài đặt dependencies (có thể mất 10-20 phút)")
    raise RuntimeError("Rasa not installed - cannot proceed with training")

print("\n✅ Rasa đã sẵn sàng - Bắt đầu training...\n")

# Train với config ở root
train_process = subprocess.run(
    ["venv_py310/bin/python", "-m", "rasa", "train", "nlu", "--config", "config.yml"],
    cwd=str(current_dir),
    capture_output=False,  # Hiển thị output real-time
    text=True
)

if train_process.returncode != 0:
    print("\n❌ Training thất bại!")
    print("   Vui lòng kiểm tra lỗi ở trên và thử lại")
    raise RuntimeError("Training failed")

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

