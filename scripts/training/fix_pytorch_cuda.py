#!/usr/bin/env python3
"""
Script Python để fix vấn đề PyTorch không nhận diện GPU
Chạy script này nếu PyTorch không detect được GPU mặc dù đã có CUDA
"""

import subprocess
import sys

def run_command(cmd, check=True):
    """Chạy command và return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout.strip(), e.returncode

def check_nvidia_smi():
    """Kiểm tra nvidia-smi - tìm ở nhiều vị trí"""
    # Thử các lệnh khác nhau
    commands = [
        "nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader",
        "/usr/bin/nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader",
        "/usr/local/bin/nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader",
        "which nvidia-smi && nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader",
    ]
    
    for cmd in commands:
        output, code = run_command(cmd, check=False)
        if code == 0 and output:
            return output
    
    return None

def main():
    print("🔧 FIX PYTORCH CUDA - Cài đặt PyTorch với CUDA support")
    print("=" * 60)
    print()
    
    # Kiểm tra nvidia-smi
    nvidia_info = check_nvidia_smi()
    if nvidia_info:
        print("✅ Tìm thấy GPU qua nvidia-smi:")
        for line in nvidia_info.split('\n'):
            if line.strip():
                parts = line.split(', ')
                if len(parts) >= 3:
                    print(f"   GPU: {parts[0].strip()}")
                    print(f"   Driver: {parts[1].strip()}")
                    print(f"   CUDA (System): {parts[2].strip()}")
        print()
    else:
        print("⚠️  Không tìm thấy nvidia-smi trong PATH")
        print("   (Nhưng bạn có thể vẫn có GPU)")
        print()
        
        # Hỏi user xác nhận
        try:
            confirm = input("Bạn có GPU NVIDIA và muốn tiếp tục cài đặt PyTorch với CUDA? (y/n): ").strip().lower()
            if confirm != 'y' and confirm != 'yes':
                print("❌ Đã hủy")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n❌ Đã hủy")
            sys.exit(0)
    
    # Kiểm tra PyTorch hiện tại
    try:
        import torch
        print(f"📦 PyTorch hiện tại: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print()
            print("✅ GPU đã được nhận diện! Không cần fix.")
            sys.exit(0)
    except ImportError:
        print("⚠️  PyTorch chưa được cài đặt")
    except Exception as e:
        print(f"⚠️  Lỗi khi kiểm tra PyTorch: {e}")
    print()
    
    # Hỏi user chọn CUDA version
    print("Chọn CUDA version để cài đặt PyTorch:")
    print("1. CUDA 12.1 (khuyến nghị - tương thích với CUDA 12.x và 13.0)")
    print("2. CUDA 12.4 (tương thích với CUDA 12.x và 13.0)")
    print("3. CUDA 11.8 (cho hệ thống cũ)")
    print("4. CPU only (không có GPU)")
    
    try:
        choice = input("Chọn (1/2/3/4, mặc định: 1): ").strip() or "1"
    except KeyboardInterrupt:
        print("\n❌ Đã hủy")
        sys.exit(1)
    
    cuda_versions = {
        "1": ("cu121", "https://download.pytorch.org/whl/cu121", True),
        "2": ("cu124", "https://download.pytorch.org/whl/cu124", True),
        "3": ("cu118", "https://download.pytorch.org/whl/cu118", True),
        "4": (None, None, False),  # CPU only
    }
    
    if choice not in cuda_versions:
        print("❌ Lựa chọn không hợp lệ")
        sys.exit(1)
    
    cuda_version, index_url, use_cuda = cuda_versions[choice]
    
    if not use_cuda:
        # CPU only
        print()
        print("📦 Đang gỡ PyTorch cũ...")
        run_command("pip uninstall -y torch torchvision torchaudio", check=False)
        
        print()
        print("📦 Đang cài đặt PyTorch (CPU only)...")
        output, code = run_command("pip install torch torchvision torchaudio", check=False)
        
        if code != 0:
            print("❌ Lỗi khi cài đặt PyTorch:")
            print(output)
            sys.exit(1)
        
        print()
        print("✅ Đã cài đặt PyTorch (CPU only)")
        print("⚠️  Training sẽ chậm hơn nhiều so với GPU")
        sys.exit(0)
    
    print()
    print("📦 Đang gỡ PyTorch cũ...")
    output, _ = run_command("pip uninstall -y torch torchvision torchaudio", check=False)
    if output:
        print("   (Đã gỡ các package cũ)")
    
    print()
    print(f"📦 Đang cài đặt PyTorch với CUDA {cuda_version}...")
    print("   (Quá trình này có thể mất 2-5 phút, vui lòng đợi...)")
    print(f"   URL: {index_url}")
    cmd = f"pip install torch torchvision torchaudio --index-url {index_url}"
    output, code = run_command(cmd, check=False)
    
    if code != 0:
        print("❌ Lỗi khi cài đặt PyTorch:")
        print(output)
        sys.exit(1)
    
    print()
    print("🔍 Kiểm tra cài đặt...")
    try:
        import torch
        print(f"   PyTorch version: {torch.__version__}")
        print(f"   CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   CUDA version: {torch.version.cuda}")
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print()
            print("✅ Thành công! GPU đã được PyTorch nhận diện")
            print()
            print("🚀 Bây giờ bạn có thể train với GPU:")
            print("   rasa train nlu")
        else:
            print()
            print("❌ Vẫn chưa nhận diện được GPU")
            print()
            print("💡 Thử các giải pháp sau:")
            print("   1. Restart terminal/IDE")
            print("   2. Kiểm tra CUDA toolkit đã được cài đặt:")
            print("      nvcc --version")
            print("   3. Kiểm tra PATH có chứa CUDA:")
            print("      echo $PATH | grep cuda")
            print("   4. Cài đặt CUDA toolkit nếu chưa có:")
            print("      https://developer.nvidia.com/cuda-downloads")
    except ImportError:
        print("❌ Không thể import torch sau khi cài đặt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

