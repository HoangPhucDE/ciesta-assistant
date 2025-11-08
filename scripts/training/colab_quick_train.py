#!/usr/bin/env python3
"""
Script đơn giản để train Rasa NLU trên Google Colab
Copy-paste toàn bộ script này vào một cell trong Colab và chạy
"""

# ============================================================================
# CONFIGURATION - Chỉnh sửa phần này nếu cần
# ============================================================================
USE_GPU = True  # Set True để sử dụng GPU (khuyến nghị)
REDUCE_MEMORY = False  # Set True nếu gặp lỗi Out of Memory
EPOCHS = None  # None = dùng epochs từ config.yml, hoặc set số cụ thể (ví dụ: 300)

# ============================================================================
# MAIN SCRIPT - Không cần chỉnh sửa phần dưới
# ============================================================================

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step_num, message):
    """Print step message"""
    print(f"\n{'='*60}")
    print(f"BƯỚC {step_num}: {message}")
    print(f"{'='*60}\n")

def check_colab():
    """Check if running on Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def check_gpu():
    """Check GPU availability"""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False

# ============================================================================
# STEP 1: Install Dependencies
# ============================================================================
print_step(1, "CÀI ĐẶT DEPENDENCIES")

# Install system packages
if check_colab():
    print("Đang cài đặt system packages...")
    subprocess.run(["apt-get", "install", "-qq", "-y", "git"], check=True)

# Install Python packages
print("Đang cài đặt Python packages...")
subprocess.run([
    sys.executable, "-m", "pip", "install", "-q",
    "--upgrade", "pip", "setuptools", "wheel"
], check=True)

if Path("requirements.txt").exists():
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-q",
        "-r", "requirements.txt"
    ], check=True)
    print("✅ Đã cài đặt dependencies")
else:
    print("⚠ Không tìm thấy requirements.txt")

# ============================================================================
# STEP 2: Check GPU
# ============================================================================
print_step(2, "KIỂM TRA GPU")

if USE_GPU and check_gpu():
    print("✅ GPU đã sẵn sàng - Training sẽ nhanh hơn")
elif USE_GPU:
    print("⚠ GPU không khả dụng - Sử dụng CPU")
    print("💡 Tip: Vào Runtime → Change runtime type → GPU")
else:
    print("ℹ Đang sử dụng CPU")

# ============================================================================
# STEP 3: Setup Directories
# ============================================================================
print_step(3, "THIẾT LẬP THỨ MỤC")

dirs = ["models", "models_hub/phobert-large", "custom_components"]
for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)

print("✅ Đã tạo các thư mục cần thiết")

# ============================================================================
# STEP 4: Download PhoBERT Model
# ============================================================================
print_step(4, "TẢI PHOBERT-LARGE MODEL")

model_path = Path("models_hub/phobert-large/config.json")
if model_path.exists():
    print("✅ Model đã tồn tại")
else:
    print("Đang tải model từ HuggingFace...")
    print("⏳ Quá trình này có thể mất 5-10 phút...")
    
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id="vinai/phobert-large",
            local_dir="models_hub/phobert-large",
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print("✅ Đã tải model thành công")
    except Exception as e:
        print(f"❌ Lỗi khi tải model: {e}")
        sys.exit(1)

# ============================================================================
# STEP 5: Setup Model Path
# ============================================================================
print_step(5, "THIẾT LẬP ĐƯỜNG DẪN MODEL")

target = Path("models/phobert-large")
if target.exists():
    if target.is_symlink():
        target.unlink()
    else:
        shutil.rmtree(target)

try:
    target.symlink_to(Path("../models_hub/phobert-large").relative_to(target.parent))
    print("✅ Đã tạo symlink")
except:
    shutil.copytree("models_hub/phobert-large", "models/phobert-large")
    print("✅ Đã copy model")

# ============================================================================
# STEP 6: Verify Files
# ============================================================================
print_step(6, "KIỂM TRA FILES")

required_files = {
    "config.yml": Path("config.yml"),
    "data/nlu.yml": Path("data/nlu.yml"),
    "custom_components/phobert_featurizer.py": Path("custom_components/phobert_featurizer.py"),
}

missing_files = []
for name, path in required_files.items():
    if path.exists():
        print(f"✅ {name}")
    else:
        print(f"❌ {name} - KHÔNG TÌM THẤY")
        missing_files.append(name)

if missing_files:
    print(f"\n⚠ Thiếu các file sau: {', '.join(missing_files)}")
    print("Vui lòng upload các file này vào Colab trước khi tiếp tục")
    sys.exit(1)

# ============================================================================
# STEP 7: Adjust Config (if needed)
# ============================================================================
if REDUCE_MEMORY:
    print_step(7, "ĐIỀU CHỈNH CONFIG (Giảm Memory)")
    
    config_file = Path("config.yml")
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Reduce batch size
        content = content.replace("batch_size: [16, 32]", "batch_size: [8, 16]")
        content = content.replace("batch_size: [32, 64]", "batch_size: [8, 16]")
        
        # Reduce epochs if needed
        if EPOCHS:
            import re
            content = re.sub(r"epochs:\s*\d+", f"epochs: {EPOCHS}", content)
        
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Đã điều chỉnh config để giảm memory usage")

# ============================================================================
# STEP 8: Train NLU Model
# ============================================================================
print_step(8, "BẮT ĐẦU TRAIN NLU MODEL")

print("⏳ Training sẽ bắt đầu...")
print("💡 Thời gian ước tính:")
if check_gpu():
    print("   - GPU: 20-40 phút (600 epochs)")
else:
    print("   - CPU: 1-2 giờ (600 epochs)")

print("\n" + "="*60)
print("BẮT ĐẦU TRAINING...")
print("="*60 + "\n")

try:
    import time
    start_time = time.time()
    
    # Train NLU
    result = subprocess.run(
        [sys.executable, "-m", "rasa", "train", "nlu"],
        check=True
    )
    
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    
    print("\n" + "="*60)
    print(f"✅ TRAINING HOÀN TẤT! Thời gian: {hours}h {minutes}m")
    print("="*60 + "\n")
    
except subprocess.CalledProcessError as e:
    print(f"\n❌ Lỗi khi train: {e}")
    sys.exit(1)
except KeyboardInterrupt:
    print("\n⚠ Training bị dừng bởi người dùng")
    sys.exit(1)

# ============================================================================
# STEP 9: Get Latest Model
# ============================================================================
print_step(9, "TÌM MODEL ĐÃ TRAIN")

models_dir = Path("models")
model_files = list(models_dir.glob("*.tar.gz"))

if not model_files:
    print("❌ Không tìm thấy model đã train")
    sys.exit(1)

latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
size_mb = latest_model.stat().st_size / (1024 * 1024)

print(f"✅ Model mới nhất: {latest_model.name}")
print(f"📦 Kích thước: {size_mb:.2f} MB")
print(f"📁 Đường dẫn: {latest_model}")

# ============================================================================
# STEP 10: Download Model (Colab only)
# ============================================================================
if check_colab():
    print_step(10, "TẢI MODEL VỀ MÁY LOCAL")
    
    try:
        from google.colab import files
        files.download(str(latest_model))
        print("✅ Đã bắt đầu tải model về máy local")
    except Exception as e:
        print(f"⚠ Không thể tải tự động: {e}")
        print(f"💡 Bạn có thể tải thủ công từ: {latest_model}")
else:
    print_step(10, "HOÀN TẤT")
    print(f"✅ Model đã được lưu tại: {latest_model}")

print("\n" + "="*60)
print("🎉 HOÀN TẤT TẤT CẢ CÁC BƯỚC!")
print("="*60)
print(f"\n📦 Model: {latest_model.name}")
print(f"📊 Kích thước: {size_mb:.2f} MB")
print(f"📁 Vị trí: {latest_model}\n")


