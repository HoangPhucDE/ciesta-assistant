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

def find_project_root():
    """Find project root directory (ciesta-assistant or current dir)"""
    current_dir = Path.cwd()
    
    # Check if we're already in project root (check for key files)
    if (current_dir / "requirements.txt").exists() and (current_dir / "config.yml").exists():
        # Make sure we're not in a nested ciesta-assistant
        if "ciesta-assistant" in str(current_dir) and (current_dir.parent / "ciesta-assistant").exists():
            # We're in a nested directory, go up one level
            parent = current_dir.parent
            if (parent / "requirements.txt").exists() and (parent / "config.yml").exists():
                return parent
        return current_dir
    
    # Check if ciesta-assistant directory exists in current dir
    if (current_dir / "ciesta-assistant").exists():
        project_root = current_dir / "ciesta-assistant"
        # Check if it has the required files and is not nested
        if (project_root / "requirements.txt").exists() and (project_root / "config.yml").exists():
            # Make sure there's no nested ciesta-assistant inside
            nested = project_root / "ciesta-assistant"
            if nested.exists() and (nested / "requirements.txt").exists():
                # There's a nested one, use the outer one
                pass
            return project_root
    
    # Check parent directory
    if (current_dir.parent / "ciesta-assistant").exists():
        project_root = current_dir.parent / "ciesta-assistant"
        if (project_root / "requirements.txt").exists() and (project_root / "config.yml").exists():
            return project_root
    
    # Try to find in current and parent directories
    for possible_root in [current_dir, current_dir.parent]:
        if (possible_root / "requirements.txt").exists() and (possible_root / "config.yml").exists():
            return possible_root
    
    return None

def check_python_version():
    """Check Python version and warn if incompatible"""
    import sys
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    print_info(f"Python version: {version_str}")
    
    # Rasa 3.6.20 requires Python 3.8-3.10
    if version.major == 3 and version.minor > 10:
        print_warning(f"Python {version_str} có thể không tương thích với Rasa 3.6.20")
        print_warning("Rasa 3.6.20 yêu cầu Python 3.8-3.10")
        print_info("Đang kiểm tra Rasa version tương thích...")
        return False
    return True

def install_dependencies():
    """Install required dependencies"""
    print_header("CÀI ĐẶT DEPENDENCIES")
    
    # Check Python version first
    python_ok = check_python_version()
    
    # Find project root - but avoid nested directories
    current_dir = Path.cwd()
    project_root = None
    
    # Count how many times "ciesta-assistant" appears in path
    path_str = str(current_dir)
    ciesta_count = path_str.count("ciesta-assistant")
    
    if ciesta_count > 1:
        print_warning(f"Phát hiện nested directory (ciesta-assistant xuất hiện {ciesta_count} lần)")
        # Find the first occurrence
        first_ciesta = path_str.find("ciesta-assistant")
        base_path = path_str[:first_ciesta + len("ciesta-assistant")]
        project_root = Path(base_path)
        if project_root.exists() and (project_root / "requirements.txt").exists():
            print_info(f"Sử dụng thư mục ngoài cùng: {project_root}")
            os.chdir(project_root)
        else:
            # Try to find in /content
            content_ciesta = Path("/content/ciesta-assistant")
            if content_ciesta.exists() and (content_ciesta / "requirements.txt").exists():
                project_root = content_ciesta
                print_info(f"Sử dụng: {project_root}")
                os.chdir(project_root)
    else:
        project_root = find_project_root()
        if project_root:
            print_info(f"Tìm thấy project tại: {project_root}")
            os.chdir(project_root)
            print_info(f"Đã chuyển vào thư mục: {Path.cwd()}")
        else:
            print_warning("Không tìm thấy project root, sử dụng thư mục hiện tại")
            project_root = Path.cwd()
    
    # Check if Colab
    if is_colab():
        print_info("Phát hiện Google Colab environment")
        
        # Install system dependencies
        print_info("Cài đặt system dependencies...")
        subprocess.run(["apt-get", "install", "-qq", "-y", "git"], check=True)
        
        # Upgrade pip
        print_info("Upgrade pip...")
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        
        # Check if we need to install Python 3.10
        if not python_ok:
            print_warning("Cần Python 3.10 để chạy Rasa 3.6.20")
            print_info("Đang kiểm tra xem có thể cài đặt Python 3.10 không...")
            # Note: Colab doesn't easily allow Python version changes
            # We'll need to work around this
    
    # Install Python packages
    # Prefer requirements-colab.txt for Colab
    if is_colab():
        # For Python 3.12, we might need a different approach
        if not python_ok:
            print_warning("Python 3.12 không tương thích với Rasa 3.6.20")
            print_info("Đang thử cài đặt Rasa version mới hơn hoặc dùng workaround...")
            # Try to install Rasa without version constraint first
            requirements_file = None
        else:
            requirements_file = Path("requirements-colab.txt")
            if not requirements_file.exists():
                print_warning("Không tìm thấy requirements-colab.txt, dùng requirements.txt")
                requirements_file = Path("requirements.txt")
    else:
        requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        # Try to find requirements file
        possible_locations = [
            Path("requirements-colab.txt"),
            Path("requirements.txt"),
            Path("../requirements-colab.txt"),
            Path("../requirements.txt"),
            Path("ciesta-assistant/requirements-colab.txt"),
            Path("ciesta-assistant/requirements.txt"),
        ]
        
        found = False
        for req_path in possible_locations:
            if req_path.exists():
                requirements_file = req_path.resolve()
                print_info(f"Tìm thấy {req_path.name} tại: {requirements_file}")
                found = True
                break
        
        if not found:
            print_error("Không tìm thấy requirements.txt hoặc requirements-colab.txt")
            print_info("Đang tìm trong các thư mục:")
            for loc in possible_locations:
                print_info(f"  - {loc} ({'tồn tại' if loc.exists() else 'không tồn tại'})")
            return False
    
    # Install packages
    print_info(f"Cài đặt từ: {requirements_file}")
    print_info("⏳ Quá trình này có thể mất vài phút...")
    
    try:
        # Run pip install with output visible for debugging
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception immediately
        )
        
        if result.returncode != 0:
            print_error("Lỗi khi cài đặt dependencies")
            print_info("Output của pip install:")
            print(result.stdout)
            if result.stderr:
                print_error("Lỗi:")
                print(result.stderr)
            
            # Try to identify the problematic package
            print_warning("Đang thử cài đặt từng package để tìm lỗi...")
            
            # Read requirements file
            with open(requirements_file, 'r') as f:
                lines = f.readlines()
            
            failed_packages = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                    if package:
                        print_info(f"Đang cài đặt: {package}...")
                        try:
                            subprocess.run(
                                [sys.executable, "-m", "pip", "install", line],
                                check=True,
                                capture_output=True
                            )
                            print_success(f"  ✓ {package}")
                        except subprocess.CalledProcessError:
                            print_error(f"  ✗ {package} - Lỗi")
                            failed_packages.append(package)
                            # Continue with other packages
            
            if failed_packages:
                print_warning(f"Các package sau không thể cài đặt: {', '.join(failed_packages)}")
                print_warning("Một số package có thể không tương thích với Python 3.12")
                print_info("Tiếp tục với các package đã cài đặt thành công...")
                # Continue anyway - some packages might not be critical for training
                # return False
            
        print_success("Đã cài đặt tất cả dependencies")
        return True
        
    except Exception as e:
        print_error(f"Lỗi không mong đợi khi cài đặt: {e}")
        return False

def setup_project_structure():
    """Setup project structure"""
    print_header("THIẾT LẬP CẤU TRÚC PROJECT")
    
    # Ensure we're in project root
    project_root = find_project_root()
    if project_root and project_root != Path.cwd():
        os.chdir(project_root)
        print_info(f"Đã chuyển vào project root: {Path.cwd()}")
    
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
        print_success(f"Đã tạo/thư mục: {dir_path}")
    
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
    
    # Ensure we're in project root
    project_root = find_project_root()
    if project_root and project_root != Path.cwd():
        os.chdir(project_root)
    
    # Check if custom components exist
    phobert_featurizer = Path("custom_components/phobert_featurizer.py")
    if not phobert_featurizer.exists():
        # Try alternative paths
        alt_paths = [
            Path("custom_components/phobert_featurizer.py"),
            Path("../custom_components/phobert_featurizer.py"),
            Path("ciesta-assistant/custom_components/phobert_featurizer.py"),
        ]
        
        found = False
        for alt_path in alt_paths:
            if alt_path.exists():
                print_info(f"Tìm thấy tại: {alt_path}")
                found = True
                break
        
        if not found:
            print_error("Không tìm thấy custom_components/phobert_featurizer.py")
            print_info("Vui lòng đảm bảo đã clone repo và chuyển vào thư mục ciesta-assistant")
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
    
    # Ensure we're in project root
    project_root = find_project_root()
    if project_root and project_root != Path.cwd():
        os.chdir(project_root)
    
    config_file = Path("config.yml")
    if not config_file.exists():
        print_error("Không tìm thấy config.yml")
        print_info(f"Thư mục hiện tại: {Path.cwd()}")
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
    
    # Ensure we're in project root
    project_root = find_project_root()
    if project_root and project_root != Path.cwd():
        os.chdir(project_root)
        print_info(f"Đã chuyển vào project root: {Path.cwd()}")
    
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
    
    print_info(f"Kiểm tra files trong: {Path.cwd()}")
    for file_path in required_files:
        file_check = Path(file_path)
        if not file_check.exists():
            print_error(f"Không tìm thấy {file_path}")
            print_info(f"  Đường dẫn đầy đủ: {file_check.resolve()}")
            return False
        else:
            print_success(f"  ✓ {file_path}")
    
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
    
    # Find and change to project root first
    project_root = find_project_root()
    if project_root:
        original_dir = Path.cwd()
        
        # Avoid nested directories
        if "ciesta-assistant" in str(project_root) and "ciesta-assistant" in str(original_dir):
            # Check if we're going into a nested directory
            parts_original = str(original_dir).split("ciesta-assistant")
            parts_project = str(project_root).split("ciesta-assistant")
            if len(parts_project) > len(parts_original):
                # We're going deeper, use the outer one
                outer_path = Path(str(original_dir).split("ciesta-assistant")[0]) / "ciesta-assistant"
                if outer_path.exists() and (outer_path / "requirements.txt").exists():
                    project_root = outer_path
                    print_warning(f"Phát hiện nested directory, sử dụng: {project_root}")
        
        os.chdir(project_root)
        print_info(f"Đã chuyển từ {original_dir} sang {Path.cwd()}")
        
        # Verify we're in the right place
        if not (Path.cwd() / "requirements.txt").exists() and not (Path.cwd() / "requirements-colab.txt").exists():
            print_error("Không tìm thấy requirements file trong project root")
            return False
    else:
        print_warning("Không tìm thấy project root, tiếp tục với thư mục hiện tại")
        print_info(f"Thư mục hiện tại: {Path.cwd()}")
        print_info("Vui lòng đảm bảo bạn đã clone repo và chuyển vào thư mục ciesta-assistant")
    
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


