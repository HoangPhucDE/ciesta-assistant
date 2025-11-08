#!/usr/bin/env python3
"""
Script tự động train Rasa NLU model trên Google Colab
- Tự động setup môi trường
- Download PhoBERT-large model
- Train NLU model
- Download model về máy local
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional
import time

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print header with color"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def is_colab() -> bool:
    """Check if running on Google Colab"""
    try:
        import google.colab
        return True
    except ImportError:
        return False

def check_gpu() -> bool:
    """Check if GPU is available"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def install_dependencies():
    """Install required dependencies"""
    print_header("CÀI ĐẶT DEPENDENCIES")
    
    # Check if Colab
    if is_colab():
        print_info("Phát hiện Google Colab environment")
        
        # Install system dependencies
        print_info("Cài đặt system dependencies...")
        subprocess.run(["apt-get", "install", "-qq", "-y", "git"], check=True)
        
        # Upgrade pip
        print_info("Upgrade pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    
    # Install Python packages
    print_info("Cài đặt Python packages từ requirements.txt...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print_error("Không tìm thấy requirements.txt")
        return False
    
    # Install packages
    subprocess.run([
        sys.executable, "-m", "pip", "install", "-q",
        "-r", str(requirements_file)
    ], check=True)
    
    print_success("Đã cài đặt tất cả dependencies")
    return True

def setup_project_structure():
    """Setup project structure"""
    print_header("THIẾT LẬP CẤU TRÚC PROJECT")
    
    # Create necessary directories
    directories = [
        "models",
        "models_hub",
        "models_hub/phobert-large",
        "custom_components",
        "data",
        "data/knowledge_base",
        "data/knowledge_base/provinces",
        "actions"
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print_success(f"Đã tạo thư mục: {dir_path}")
    
    return True

def download_phobert_model(model_name: str = "vinai/phobert-large", 
                          local_dir: str = "models_hub/phobert-large"):
    """Download PhoBERT model from HuggingFace"""
    print_header("TẢI PHOBERT-LARGE MODEL")
    
    local_path = Path(local_dir)
    
    # Check if model already exists
    config_file = local_path / "config.json"
    if config_file.exists():
        print_success(f"Model đã tồn tại tại {local_dir}")
        return True
    
    print_info(f"Đang tải model {model_name} từ HuggingFace...")
    print_warning("Quá trình này có thể mất 5-10 phút tùy vào tốc độ mạng")
    
    try:
        from huggingface_hub import snapshot_download
        
        snapshot_download(
            repo_id=model_name,
            local_dir=str(local_path),
            local_dir_use_symlinks=False,
            resume_download=True
        )
        
        print_success(f"Đã tải model thành công vào {local_dir}")
        return True
        
    except Exception as e:
        print_error(f"Lỗi khi tải model: {e}")
        return False

def setup_custom_components():
    """Setup custom components"""
    print_header("THIẾT LẬP CUSTOM COMPONENTS")
    
    # Check if custom components exist
    phobert_featurizer = Path("custom_components/phobert_featurizer.py")
    if not phobert_featurizer.exists():
        print_error("Không tìm thấy custom_components/phobert_featurizer.py")
        print_info("Vui lòng upload file này vào Colab")
        return False
    
    print_success("Custom components đã sẵn sàng")
    return True

def create_symlink():
    """Create symlink from models/phobert-large to models_hub/phobert-large"""
    print_header("TẠO SYMLINK CHO MODEL")
    
    source = Path("models_hub/phobert-large")
    target = Path("models/phobert-large")
    
    if not source.exists():
        print_error(f"Không tìm thấy {source}")
        return False
    
    # Remove existing symlink or directory
    if target.exists():
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)
    
    # Create symlink
    try:
        target.symlink_to(source.relative_to(target.parent))
        print_success(f"Đã tạo symlink: {target} -> {source}")
        return True
    except Exception as e:
        # On Windows or if symlink fails, copy directory
        print_warning(f"Không thể tạo symlink: {e}")
        print_info("Đang copy thư mục...")
        shutil.copytree(source, target)
        print_success(f"Đã copy model vào {target}")
        return True

def verify_config():
    """Verify config.yml is correct"""
    print_header("KIỂM TRA CONFIG")
    
    config_file = Path("config.yml")
    if not config_file.exists():
        print_error("Không tìm thấy config.yml")
        return False
    
    # Read config
    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    # Check if using local model
    if "models/phobert-large" in config_content:
        print_success("Config đang sử dụng model local")
    else:
        print_warning("Config có thể chưa được cấu hình để dùng model local")
    
    return True

def train_nlu(epochs: Optional[int] = None):
    """Train NLU model"""
    print_header("BẮT ĐẦU TRAIN NLU MODEL")
    
    # Check GPU
    has_gpu = check_gpu()
    if has_gpu:
        print_success("GPU đã sẵn sàng - Training sẽ nhanh hơn")
    else:
        print_warning("Không có GPU - Training sẽ chậm hơn (có thể mất 1-2 giờ)")
    
    # Verify files exist
    required_files = [
        "config.yml",
        "data/nlu.yml",
        "custom_components/phobert_featurizer.py"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print_error(f"Không tìm thấy {file_path}")
            return False
    
    print_info("Bắt đầu training...")
    print_info("Quá trình này có thể mất 30 phút - 2 giờ tùy vào cấu hình")
    
    start_time = time.time()
    
    try:
        # Train NLU
        cmd = [sys.executable, "-m", "rasa", "train", "nlu"]
        if epochs:
            # Note: epochs is set in config.yml, but we can override if needed
            print_warning("Epochs được cấu hình trong config.yml")
        
        result = subprocess.run(cmd, check=True)
        
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        
        print_success(f"Training hoàn tất! Thời gian: {hours}h {minutes}m")
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Lỗi khi train: {e}")
        return False
    except KeyboardInterrupt:
        print_warning("Training bị dừng bởi người dùng")
        return False

def get_latest_model():
    """Get the latest trained model"""
    models_dir = Path("models")
    if not models_dir.exists():
        return None
    
    # Find all .tar.gz files
    model_files = list(models_dir.glob("*.tar.gz"))
    if not model_files:
        return None
    
    # Sort by modification time
    model_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return model_files[0]

def download_model_to_local():
    """Download model to local machine (Colab specific)"""
    if not is_colab():
        print_warning("Không phải Colab environment - bỏ qua download")
        return
    
    print_header("TẢI MODEL VỀ MÁY LOCAL")
    
    latest_model = get_latest_model()
    if not latest_model:
        print_error("Không tìm thấy model đã train")
        return
    
    print_info(f"Model mới nhất: {latest_model.name}")
    print_info(f"Kích thước: {latest_model.stat().st_size / (1024*1024):.2f} MB")
    
    try:
        from google.colab import files
        files.download(str(latest_model))
        print_success("Đã bắt đầu tải model về máy local")
    except Exception as e:
        print_error(f"Lỗi khi tải model: {e}")
        print_info(f"Bạn có thể tải thủ công từ: {latest_model}")

def main():
    """Main function"""
    print_header("RASA NLU TRAINING TRÊN GOOGLE COLAB")
    
    # Check environment
    if is_colab():
        print_success("Đang chạy trên Google Colab")
    else:
        print_warning("Không phải Colab - script vẫn hoạt động nhưng một số tính năng có thể bị giới hạn")
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print_error("Cài đặt dependencies thất bại")
        return False
    
    # Step 2: Setup project structure
    if not setup_project_structure():
        print_error("Thiết lập cấu trúc project thất bại")
        return False
    
    # Step 3: Download model
    if not download_phobert_model():
        print_error("Tải model thất bại")
        return False
    
    # Step 4: Create symlink
    if not create_symlink():
        print_error("Tạo symlink thất bại")
        return False
    
    # Step 5: Setup custom components
    if not setup_custom_components():
        print_error("Thiết lập custom components thất bại")
        return False
    
    # Step 6: Verify config
    if not verify_config():
        print_warning("Config có thể chưa đúng - vui lòng kiểm tra")
    
    # Step 7: Train NLU
    if not train_nlu():
        print_error("Training thất bại")
        return False
    
    # Step 8: Download model
    download_model_to_local()
    
    print_header("HOÀN TẤT!")
    print_success("Training đã hoàn tất thành công!")
    
    latest_model = get_latest_model()
    if latest_model:
        print_info(f"Model đã được lưu tại: {latest_model}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nScript bị dừng bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print_error(f"Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

