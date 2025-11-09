# ============================================
# TỐI ƯU GPU - CHẠY TRONG COLAB
# ============================================
# Script này kiểm tra và tối ưu batch size để tận dụng GPU tốt hơn
# Chạy script này TRƯỚC KHI train hoặc DỪNG training hiện tại và chạy lại

import os
import re
import subprocess
from pathlib import Path

print("⚡ Tối ưu GPU Utilization cho Rasa Training")
print("=" * 60)

# Kiểm tra GPU
print("\n🎮 Kiểm tra GPU...")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ GPU được phát hiện")
        # Extract GPU name
        if "T4" in result.stdout:
            print("   GPU: T4 (15GB)")
        elif "V100" in result.stdout:
            print("   GPU: V100 (16GB)")
        elif "A100" in result.stdout:
            print("   GPU: A100 (40GB)")
        else:
            print("   GPU: Unknown")
    else:
        print("❌ Không tìm thấy GPU")
        print("   Vui lòng bật GPU: Runtime → Change runtime type → GPU")
        exit(1)
except Exception as e:
    print(f"⚠️ Lỗi khi kiểm tra GPU: {e}")

# Kiểm tra GPU memory bằng PyTorch
print("\n🔍 Kiểm tra GPU Memory...")
check_gpu_memory = """
try:
    import torch
    if torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        gpu_name = torch.cuda.get_device_name(0)
        print(f"{gpu_memory:.1f}|{gpu_name}")
    else:
        print("0|No GPU")
except Exception as e:
    print(f"0|Error: {e}")
"""
with open("/tmp/check_gpu_memory.py", "w") as f:
    f.write(check_gpu_memory)

try:
    result = subprocess.run(
        ["python3", "/tmp/check_gpu_memory.py"],
        capture_output=True,
        text=True,
        cwd=os.getcwd()
    )
    if result.returncode == 0 and "|" in result.stdout:
        parts = result.stdout.strip().split("|")
        gpu_memory_gb = float(parts[0])
        gpu_name = parts[1] if len(parts) > 1 else "Unknown"
        print(f"   GPU: {gpu_name}")
        print(f"   Memory: {gpu_memory_gb:.1f} GB")
    else:
        print("   ⚠️ Không thể kiểm tra GPU memory")
        gpu_memory_gb = None
except Exception as e:
    print(f"   ⚠️ Lỗi: {e}")
    gpu_memory_gb = None

# Tìm config file
print("\n📁 Tìm config file...")
current_dir = Path.cwd()
config_paths = [
    current_dir / "config.yml",
    current_dir / "config/rasa/config.yml",
]

config_file = None
for path in config_paths:
    if path.exists():
        config_file = path
        print(f"   ✅ Tìm thấy: {config_file}")
        break

if not config_file:
    print("   ❌ Không tìm thấy config.yml")
    print("   Vui lòng đảm bảo đang ở đúng thư mục project")
    exit(1)

# Đọc config hiện tại
print("\n📖 Đọc config hiện tại...")
with open(config_file, "r", encoding="utf-8") as f:
    config_content = f.read()

# Kiểm tra batch size hiện tại
phobert_batch_match = re.search(r'pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:\s*(\d+)', config_content)
diet_batch_match = re.search(r'batch_size:\s*\[(\d+),\s*(\d+)\]', config_content)

if phobert_batch_match:
    phobert_batch = int(phobert_batch_match.group(1))
    print(f"   PhoBERTFeaturizer batch_size: {phobert_batch}")
else:
    print("   ⚠️ Không tìm thấy PhoBERTFeaturizer batch_size")
    phobert_batch = None

if diet_batch_match:
    diet_batch = [int(diet_batch_match.group(1)), int(diet_batch_match.group(2))]
    print(f"   DIETClassifier batch_size: {diet_batch_match.group(0)}")
else:
    print("   ⚠️ Không tìm thấy DIETClassifier batch_size")
    diet_batch = None

# Đề xuất batch size tối ưu
print("\n💡 Đề xuất batch size tối ưu:")
if gpu_memory_gb and gpu_memory_gb >= 15:
    recommended_phobert = 128
    recommended_diet = [128, 256]
    print(f"   GPU lớn ({gpu_memory_gb:.1f}GB) - Khuyến nghị:")
    print(f"   - PhoBERTFeaturizer: {recommended_phobert}")
    print(f"   - DIETClassifier: {recommended_diet}")
elif gpu_memory_gb and gpu_memory_gb >= 8:
    recommended_phobert = 64
    recommended_diet = [64, 128]
    print(f"   GPU trung bình ({gpu_memory_gb:.1f}GB) - Khuyến nghị:")
    print(f"   - PhoBERTFeaturizer: {recommended_phobert}")
    print(f"   - DIETClassifier: {recommended_diet}")
elif gpu_memory_gb and gpu_memory_gb >= 4:
    recommended_phobert = 48
    recommended_diet = [32, 64]
    print(f"   GPU nhỏ ({gpu_memory_gb:.1f}GB) - Khuyến nghị:")
    print(f"   - PhoBERTFeaturizer: {recommended_phobert}")
    print(f"   - DIETClassifier: {recommended_diet}")
else:
    print("   ⚠️ Không thể detect GPU memory - Giữ batch size hiện tại")
    recommended_phobert = None
    recommended_diet = None

# Kiểm tra xem có cần update không
need_update = False
if recommended_phobert and phobert_batch and phobert_batch < recommended_phobert:
    print(f"\n⚠️ PhoBERT batch_size ({phobert_batch}) nhỏ hơn khuyến nghị ({recommended_phobert})")
    need_update = True

if recommended_diet and diet_batch:
    if diet_batch[0] < recommended_diet[0] or diet_batch[1] < recommended_diet[1]:
        print(f"⚠️ DIET batch_size ({diet_batch}) nhỏ hơn khuyến nghị ({recommended_diet})")
        need_update = True

# Update config nếu cần
if need_update and recommended_phobert and recommended_diet:
    print("\n🔄 Cập nhật config...")
    original_content = config_content
    
    # Update PhoBERT batch_size
    if phobert_batch and phobert_batch < recommended_phobert:
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            f'\\1 {recommended_phobert}  # Tối ưu cho GPU ({gpu_memory_gb:.1f}GB)',
            config_content
        )
        print(f"   ✅ Đã cập nhật PhoBERT batch_size: {phobert_batch} → {recommended_phobert}")
    
    # Update DIET batch_size
    if diet_batch:
        config_content = re.sub(
            r'(batch_size:\s*)\[\d+,\s*\d+\]',
            f'\\1{recommended_diet}  # Tối ưu cho GPU ({gpu_memory_gb:.1f}GB)',
            config_content
        )
        print(f"   ✅ Đã cập nhật DIET batch_size: {diet_batch} → {recommended_diet}")
    
    # Ghi lại config
    if config_content != original_content:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print("\n✅ Đã cập nhật config.yml")
        print("\n⚠️ QUAN TRỌNG:")
        print("   1. DỪNG training hiện tại (nếu đang chạy)")
        print("   2. Chạy lại training với config mới:")
        print("      !rasa train nlu --config config.yml")
        print("   3. GPU RAM usage sẽ tăng lên 50-70%")
        print("   4. Training sẽ nhanh hơn đáng kể")
    else:
        print("   ℹ️ Config đã được tối ưu")
else:
    if not need_update:
        print("\n✅ Batch size đã được tối ưu!")
        print("   GPU sẽ được sử dụng hiệu quả hơn")
    else:
        print("\n⚠️ Không thể tự động tối ưu (không detect được GPU)")
        print("   Có thể tăng batch size thủ công trong config.yml")

print("\n" + "=" * 60)
print("💡 Tip: Monitor GPU usage trong Resources panel")
print("   GPU RAM nên sử dụng 50-70% khi training với batch size tối ưu")

