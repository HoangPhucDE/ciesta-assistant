#!/usr/bin/env python3
"""
Script đơn giản để train Rasa NLU trên Google Colab
- Chỉ train, không download model trước
- Tự động tải model về sau khi train xong
"""

import os
import sys
import subprocess
from pathlib import Path

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"{msg}")
    print(f"{'='*60}\n")

def check_colab():
    try:
        import google.colab
        return True
    except ImportError:
        return False

def setup_colab():
    """Setup Colab environment"""
    print_step("SETUP GOOGLE COLAB")
    
    # Check Python version
    import sys
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    print(f"Python version: {py_version}")
    
    if sys.version_info.minor > 10:
        print("⚠ Cảnh báo: Python 3.12 không tương thích với Rasa 3.6.20")
        print("💡 Giải pháp: Sử dụng Python 3.10")
        print("\nĐang cài đặt Python 3.10...")
        
        # Install Python 3.10
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "-qq", "python3.10", "python3.10-venv", "python3.10-dev"], check=True)
        
        # Create virtual environment with Python 3.10
        if not Path("venv_py310").exists():
            subprocess.run(["python3.10", "-m", "venv", "venv_py310"], check=True)
        
        print("✅ Đã tạo virtual environment Python 3.10")
        print("📝 Lưu ý: Bạn cần activate virtual environment và chạy lại script")
        print("   source venv_py310/bin/activate")
        return False
    
    # Install system dependencies
    subprocess.run(["apt-get", "install", "-qq", "-y", "git"], check=True)
    
    # Upgrade pip
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    
    return True

def find_and_setup_project():
    """Find project directory and setup"""
    print_step("TÌM VÀ SETUP PROJECT")
    
    current_dir = Path.cwd()
    print(f"Thư mục hiện tại: {current_dir}")
    
    # Check for nested directories
    path_str = str(current_dir)
    if "ciesta-assistant" in path_str:
        # Count occurrences
        count = path_str.count("ciesta-assistant")
        if count > 1:
            print(f"⚠ Phát hiện {count} thư mục ciesta-assistant lồng nhau")
            # Find the first one
            first_pos = path_str.find("ciesta-assistant")
            base_path = path_str[:first_pos + len("ciesta-assistant")]
            target = Path(base_path)
            if target.exists():
                print(f"✅ Chuyển về thư mục: {target}")
                os.chdir(target)
            else:
                # Try /content/ciesta-assistant
                target = Path("/content/ciesta-assistant")
                if target.exists():
                    print(f"✅ Chuyển về: {target}")
                    os.chdir(target)
        else:
            # Check if we're already in ciesta-assistant
            if current_dir.name == "ciesta-assistant":
                print("✅ Đã ở trong thư mục ciesta-assistant")
            elif (current_dir / "ciesta-assistant").exists():
                print("✅ Tìm thấy ciesta-assistant, chuyển vào...")
                os.chdir(current_dir / "ciesta-assistant")
    else:
        # Check if ciesta-assistant exists
        if (current_dir / "ciesta-assistant").exists():
            print("✅ Tìm thấy ciesta-assistant, chuyển vào...")
            os.chdir(current_dir / "ciesta-assistant")
        elif (Path("/content") / "ciesta-assistant").exists():
            print("✅ Tìm thấy trong /content, chuyển vào...")
            os.chdir(Path("/content") / "ciesta-assistant")
        else:
            print("❌ Không tìm thấy thư mục ciesta-assistant")
            print("💡 Vui lòng chạy: !git clone https://github.com/HoangPhucDE/ciesta-assistant.git")
            return False
    
    project_dir = Path.cwd()
    print(f"📁 Project directory: {project_dir}")
    
    # Check required files
    required = ["config.yml", "data/nlu.yml", "custom_components/phobert_featurizer.py"]
    missing = []
    for file in required:
        if not (project_dir / file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Thiếu các file: {missing}")
        return False
    
    print("✅ Tất cả files cần thiết đã có")
    return True

def install_dependencies():
    """Install dependencies"""
    print_step("CÀI ĐẶT DEPENDENCIES")
    
    # Use requirements-colab.txt if available, otherwise requirements.txt
    req_file = "requirements-colab.txt"
    if not Path(req_file).exists():
        req_file = "requirements.txt"
    
    if not Path(req_file).exists():
        print(f"❌ Không tìm thấy {req_file}")
        return False
    
    print(f"📦 Cài đặt từ: {req_file}")
    
    # Install core packages first
    core_packages = [
        "transformers==4.35.2",
        "torch",
        "numpy",
        "faiss-cpu",
        "huggingface_hub",
        "requests",
    ]
    
    print("📦 Cài đặt core packages...")
    for pkg in core_packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg], check=True)
            print(f"  ✓ {pkg.split('==')[0]}")
        except:
            print(f"  ✗ {pkg.split('==')[0]}")
    
    # Try to install Rasa (might fail on Python 3.12)
    print("\n📦 Cài đặt Rasa...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "rasa==3.6.20", "rasa-sdk==3.6.2"], check=True)
        print("  ✓ Rasa installed")
    except:
        print("  ✗ Rasa không thể cài đặt (cần Python 3.10)")
        print("  💡 Bạn cần dùng Python 3.10 để train Rasa")
        return False
    
    # Install other packages
    print("\n📦 Cài đặt các packages còn lại...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "-r", req_file], check=False)
    except:
        pass
    
    print("✅ Đã cài đặt dependencies")
    return True

def setup_model_config():
    """Setup model config to use online model"""
    print_step("THIẾT LẬP CONFIG MODEL")
    
    config_file = Path("config.yml")
    if not config_file.exists():
        print("❌ Không tìm thấy config.yml")
        return False
    
    # Read config
    with open(config_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if already using online model
    if "vinai/phobert-large" in content and "models/phobert-large" not in content:
        print("✅ Config đã sử dụng model online")
        return True
    
    # Update to use online model
    if "models/phobert-large" in content:
        content = content.replace("models/phobert-large", "vinai/phobert-large")
        content = content.replace('cache_dir: null', 'cache_dir: "models_hub/phobert_cache"')
        
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print("✅ Đã cập nhật config để dùng model online")
    
    return True

def train_nlu():
    """Train NLU model"""
    print_step("BẮT ĐẦU TRAIN NLU")
    
    # Check GPU
    try:
        import torch
        if torch.cuda.is_available():
            print("✅ GPU đã sẵn sàng")
        else:
            print("⚠ Sử dụng CPU - Training sẽ chậm hơn")
    except:
        print("⚠ Không thể kiểm tra GPU")
    
    print("⏳ Bắt đầu training...")
    print("💡 Quá trình này có thể mất 30 phút - 2 giờ")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "rasa", "train", "nlu"],
            check=True
        )
        print("\n✅ Training hoàn tất!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Lỗi khi train: {e}")
        return False

def download_model():
    """Download trained model"""
    print_step("TẢI MODEL VỀ MÁY")
    
    if not check_colab():
        print("⚠ Không phải Colab, bỏ qua download")
        return
    
    models_dir = Path("models")
    if not models_dir.exists():
        print("❌ Không tìm thấy thư mục models")
        return
    
    model_files = list(models_dir.glob("*.tar.gz"))
    if not model_files:
        print("❌ Không tìm thấy model đã train")
        return
    
    # Get latest model
    latest = max(model_files, key=lambda x: x.stat().st_mtime)
    size_mb = latest.stat().st_size / (1024 * 1024)
    
    print(f"📦 Model: {latest.name}")
    print(f"📊 Kích thước: {size_mb:.2f} MB")
    
    try:
        from google.colab import files
        files.download(str(latest))
        print("✅ Đã bắt đầu tải model về máy")
    except Exception as e:
        print(f"❌ Lỗi khi tải: {e}")
        print(f"💡 Bạn có thể tải thủ công từ: {latest}")

def main():
    """Main function"""
    print_step("RASA NLU TRAINING - COLAB SIMPLE")
    
    # Step 1: Setup Colab
    if not setup_colab():
        print("\n❌ Setup thất bại. Vui lòng sử dụng Python 3.10")
        return False
    
    # Step 2: Find and setup project
    if not find_and_setup_project():
        return False
    
    # Step 3: Install dependencies
    if not install_dependencies():
        print("\n❌ Cài đặt dependencies thất bại")
        return False
    
    # Step 4: Setup model config (use online model)
    if not setup_model_config():
        return False
    
    # Step 5: Train NLU
    if not train_nlu():
        return False
    
    # Step 6: Download model
    download_model()
    
    print_step("HOÀN TẤT!")
    print("✅ Training đã hoàn tất thành công!")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠ Đã dừng bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

