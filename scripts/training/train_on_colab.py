#!/usr/bin/env python3
"""
Script tự động train Rasa NLU model trên Google Colab
- Tự động cleanup và clone repo mới từ git (Colab only)
- Tự động setup môi trường
- Download PhoBERT-large model
- Train NLU model
- Download model về máy local

Workflow (Colab):
1. Script tự động xóa repo cũ và clone repo mới từ git
2. (Khuyến nghị) Chạy sync_location_names.py trước để đồng bộ location names
3. Chạy script này để train model
4. Model sẽ được lưu trong models/ và có thể download về máy local

Lưu ý:
- Trên Colab: Script tự động cleanup và clone repo mới mỗi lần chạy
- Có thể set CIESTA_GIT_URL và CIESTA_GIT_BRANCH để clone branch khác
- Script này chỉ phục vụ training, không fix entity alignments
- Entity alignments nên được fix trước bằng sync_location_names.py
- Xem docs/README_SYNC_LOCATIONS.md để biết thêm chi tiết
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional
import time
import re

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
        import importlib.util
        return importlib.util.find_spec('google.colab') is not None
    except (ImportError, AttributeError):
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
    
    # Initialize python_cmd - will be used throughout the function
    python_cmd = None
    
    # Check if Colab
    if is_colab():
        print_info("Phát hiện Google Colab environment")
        
        # Install system dependencies
        print_info("Cài đặt system dependencies...")
        subprocess.run(["apt-get", "update", "-qq"], check=False)
        subprocess.run(["apt-get", "install", "-qq", "-y", "git", "software-properties-common"], check=False)
        
        # Determine which Python to use
        # After cloning new repo, sys.executable might point to non-existent venv
        # So we need to check if it exists, otherwise use system Python
        if sys.executable and Path(sys.executable).exists():
            python_cmd = sys.executable
            print_info(f"Sử dụng Python từ sys.executable: {python_cmd}")
        else:
            # Try to find system Python
            for py_cmd in ["python3", "python"]:
                try:
                    result = subprocess.run(["which", py_cmd], capture_output=True, text=True, check=False)
                    if result.returncode == 0 and result.stdout.strip():
                        python_cmd = result.stdout.strip()
                        print_info(f"Sử dụng system Python: {python_cmd}")
                        break
                except Exception:
                    continue
            
            if not python_cmd:
                # Fallback to sys.executable (even if path doesn't exist, it might work)
                python_cmd = sys.executable
                print_warning(f"Sử dụng sys.executable (có thể không tồn tại): {python_cmd}")
        
        # Upgrade pip
        print_info("Upgrade pip...")
        try:
            subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], 
                         check=False, timeout=300)
        except Exception as e:
            print_warning(f"Không thể upgrade pip với {python_cmd}: {e}")
            # Try with python3 directly
            try:
                subprocess.run(["python3", "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], 
                             check=False, timeout=300)
                python_cmd = "python3"
            except Exception as e2:
                print_error(f"Không thể upgrade pip: {e2}")
    else:
        # Not Colab - use sys.executable
        python_cmd = sys.executable
    
    # Check if we need to install Python 3.10 (only on Colab)
    if is_colab() and not python_ok:
        print_warning("Cần Python 3.10 để chạy Rasa 3.6.20")
        print_info("Đang cài đặt Python 3.10 trên Colab...")
        
        # Install Python 3.10
        try:
            # Install Python 3.10 from apt
            print_info("Đang cài đặt Python 3.10 và các package cần thiết...")
            subprocess.run([
                "apt-get", "install", "-y", "-qq",
                "python3.10", "python3.10-venv", "python3.10-dev"
            ], check=False)
            
            # Create virtual environment with Python 3.10
            print_info("Đang tạo virtual environment với Python 3.10...")
            venv_path = Path("venv_py310")
            
            # Remove old venv if exists
            if venv_path.exists():
                shutil.rmtree(venv_path)
            
            # Create new venv
            result = subprocess.run([
                "python3.10", "-m", "venv", str(venv_path)
            ], check=False, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get Python path from venv
                python310_path = venv_path / "bin" / "python"
                
                if python310_path.exists():
                    print_success(f"Đã tạo virtual environment với Python 3.10 tại: {python310_path}")
                    sys.executable = str(python310_path)
                    # Update python_cmd for subsequent operations
                    python_cmd = str(python310_path)
                    # Update PATH to include venv
                    venv_bin = str(venv_path / "bin")
                    os.environ["PATH"] = venv_bin + ":" + os.environ.get("PATH", "")
                    python_ok = True
                    
                    # Upgrade pip in the new venv
                    print_info("Upgrade pip trong venv mới...")
                    subprocess.run([python_cmd, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], 
                                 check=False, timeout=300)
                else:
                    raise Exception("Không tìm thấy Python trong venv")
            else:
                raise Exception(f"Không thể tạo venv: {result.stderr}")
                
        except Exception as e:
            print_warning(f"Không thể cài Python 3.10: {e}")
            print_info("Sẽ sử dụng Python 3.12 với Rasa version mới hơn...")
            print_info("💡 Lưu ý: Một số tính năng có thể không hoạt động với Python 3.12")
            # Ensure python_cmd is set even if venv creation failed
            if not python_cmd:
                python_cmd = "python3"
    
    # Find requirements file
    requirements_file = None
    possible_locations = [
        Path("requirements-colab.txt"),
        Path("requirements.txt"),
        Path("../requirements-colab.txt"),
        Path("../requirements.txt"),
        Path("ciesta-assistant/requirements-colab.txt"),
        Path("ciesta-assistant/requirements.txt"),
    ]
    
    # Try to find requirements file
    original_requirements_file = None
    for req_path in possible_locations:
        if req_path.exists():
            original_requirements_file = req_path.resolve()
            print_info(f"Tìm thấy {req_path.name} tại: {original_requirements_file}")
            break
    
    # Fix requirements file for compatibility (for Python 3.10 with Rasa 3.6.20)
    if python_ok and original_requirements_file:
        # Rasa 3.6.20 requires regex<2022.11, but requirements-colab.txt might have newer version
        # Create a fixed requirements file
        print_info("Đang kiểm tra và sửa conflicts trong requirements file...")
        temp_requirements = Path("requirements-colab-fixed.txt")
        try:
            # Read original requirements
            with open(original_requirements_file, 'r') as f:
                original_req = f.read()
            
            updated_req = original_req
            
            # Fix regex version conflict: Rasa 3.6.20 requires regex<2022.11
            # Replace any regex version >= 2022.11 with compatible version
            regex_patterns = [
                r'regex\s*==\s*(\d{4})\.(\d+)\.(\d+)',  # regex==2024.5.15
                r'regex\s*==\s*(\d{4})\.(\d+)',  # regex==2024.5
                r'regex\s*>=\s*(\d{4})',  # regex>=2024
            ]
            
            regex_found = False
            for pattern in regex_patterns:
                regex_match = re.search(pattern, updated_req)
                if regex_match:
                    regex_found = True
                    # Extract year and month if available
                    year = int(regex_match.group(1))
                    month = int(regex_match.group(2)) if len(regex_match.groups()) >= 2 else 0
                    
                    # Check if version is incompatible (year > 2022 or year == 2022 and month >= 11)
                    if year > 2022 or (year == 2022 and month >= 11):
                        # Replace with last compatible version: regex==2022.9.13
                        updated_req = re.sub(
                            r'regex\s*==\s*[\d.]+',
                            'regex==2022.9.13  # Fixed: Rasa 3.6.20 requires regex<2022.11',
                            updated_req
                        )
                        # Also replace >= patterns
                        updated_req = re.sub(
                            r'regex\s*>=\s*[\d.]+',
                            'regex==2022.9.13  # Fixed: Rasa 3.6.20 requires regex<2022.11',
                            updated_req
                        )
                        print_success("   ✅ Đã sửa regex version để tương thích với Rasa 3.6.20")
                        print_info("      regex==2024.5.15 -> regex==2022.9.13")
                        break
            
            # If no regex found, add it with compatible version
            if not regex_found and 'rasa' in updated_req.lower():
                # Add regex with compatible version
                updated_req += "\n# Text preprocessing for Vietnamese - Fixed for Rasa 3.6.20 compatibility\nregex==2022.9.13\n"
                print_info("   ✅ Đã thêm regex version tương thích")
            
            # Also ensure numpy version is compatible
            if 'numpy' in updated_req:
                # Rasa 3.6.20 works with numpy 1.23.5 or 1.24.x (but not 2.x)
                updated_req = re.sub(
                    r'numpy\s*==\s*2\.\d+',
                    'numpy==1.26.4  # Fixed: Rasa 3.6.20 requires numpy<2.0',
                    updated_req
                )
            
            # Write fixed requirements file
            with open(temp_requirements, 'w') as f:
                f.write(updated_req)
            
            requirements_file = temp_requirements
            print_info(f"✅ Đã tạo requirements file đã sửa: {temp_requirements}")
            print_info("💡 File này đã được điều chỉnh để tương thích với Rasa 3.6.20")
            
        except Exception as e:
            print_warning(f"Không thể tạo requirements file đã sửa: {e}")
            print_info("Sẽ sử dụng requirements file gốc...")
            requirements_file = original_requirements_file
    elif not python_ok and is_colab():
        # Python 3.12 - create requirements with newer Rasa version
        if original_requirements_file:
            print_warning("Python 3.12 không tương thích với Rasa 3.6.20")
            print_info("Tạo requirements file tạm thời với Rasa version mới hơn (>=3.7.0)...")
            
            temp_requirements = Path("requirements-colab-py312.txt")
            try:
                with open(original_requirements_file, 'r') as f:
                    original_req = f.read()
                
                # Replace Rasa version with newer one that supports Python 3.12
                updated_req = re.sub(
                    r'rasa==[\d.]+',
                    'rasa>=3.7.0',
                    original_req
                )
                updated_req = re.sub(
                    r'rasa-sdk==[\d.]+',
                    'rasa-sdk>=3.7.0',
                    updated_req
                )
                
                # Update numpy to a version compatible with Python 3.12
                updated_req = re.sub(
                    r'numpy\s*==\s*1\.23\.5',
                    'numpy>=1.24.0',
                    updated_req
                )
                
                with open(temp_requirements, 'w') as f:
                    f.write(updated_req)
                
                requirements_file = temp_requirements
                print_info(f"✅ Đã tạo requirements file tạm thời: {temp_requirements}")
                print_info("💡 File này sử dụng Rasa >=3.7.0 (hỗ trợ Python 3.12)")
            except Exception as e:
                print_error(f"Không thể tạo requirements file tạm thời: {e}")
                print_warning("Sẽ sử dụng requirements file gốc - có thể gặp lỗi với Python 3.12")
                requirements_file = original_requirements_file
        else:
            print_error("Không tìm thấy requirements.txt và Python 3.12 không tương thích")
            print_info("Vui lòng cài Python 3.10 hoặc tạo requirements.txt")
            return False
    else:
        # Python is OK or not Colab, use original requirements file
        requirements_file = original_requirements_file
    
    if not requirements_file:
        print_error("Không tìm thấy requirements.txt hoặc requirements-colab.txt")
        print_info("Đang tìm trong các thư mục:")
        for loc in possible_locations:
            exists = loc.exists()
            print_info(f"  - {loc} ({'tồn tại' if exists else 'không tồn tại'})")
        return False
    
    if not requirements_file.exists():
        print_error(f"Requirements file không tồn tại: {requirements_file}")
        return False
    
    # Install packages
    print_info(f"Cài đặt từ: {requirements_file}")
    print_info(f"   Đường dẫn đầy đủ: {requirements_file.resolve()}")
    print_info("⏳ Quá trình này có thể mất 10-20 phút, KHÔNG interrupt!")
    print_warning("⚠️ QUAN TRỌNG: Quá trình này có thể mất 10-20 phút, KHÔNG interrupt!")
    print_info("   Để cài đặt chạy đến khi hoàn tất...")
    
    # Verify requirements file exists and is readable
    if not requirements_file.exists():
        print_error(f"Requirements file không tồn tại: {requirements_file}")
        return False
    
    # Check file size
    file_size = requirements_file.stat().st_size
    if file_size == 0:
        print_error(f"Requirements file rỗng: {requirements_file}")
        return False
    
    print_info(f"   Kích thước file: {file_size} bytes")
    
    # Ensure python_cmd is set (fallback to sys.executable if not set)
    if not python_cmd:
        python_cmd = sys.executable
    
    # Upgrade pip first
    print_info("Đang upgrade pip...")
    pip_upgrade_result = subprocess.run(
        [python_cmd, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        check=False,
        capture_output=True,
        text=True
    )
    
    if pip_upgrade_result.returncode != 0:
        print_warning("Có lỗi khi upgrade pip, nhưng sẽ tiếp tục...")
        if pip_upgrade_result.stderr:
            print_warning(f"  {pip_upgrade_result.stderr[:200]}")
    else:
        print_success("Đã upgrade pip thành công")
    
    try:
        # Run pip install with real-time output
        print_info(f"Đang cài đặt packages từ {requirements_file.name}...")
        print_info("   (Quá trình này có thể mất 10-20 phút, vui lòng đợi...)")
        
        # Run pip install with output captured for error analysis
        pip_process = subprocess.run(
            [python_cmd, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,  # Capture output để phân tích lỗi
            text=True,
            check=False,
            timeout=1800  # 30 phút timeout
        )
        
        # Print output
        if pip_process.stdout:
            print(pip_process.stdout)
        if pip_process.stderr:
            print(pip_process.stderr)
        
        if pip_process.returncode != 0:
            print_error("Lỗi khi cài đặt dependencies!")
            print_info("Chi tiết lỗi:")
            if pip_process.stderr:
                print_error(pip_process.stderr)
            if pip_process.stdout:
                # Tìm dòng lỗi trong output
                for line in pip_process.stdout.split('\n'):
                    if 'error' in line.lower() or 'failed' in line.lower() or 'ERROR' in line:
                        print_error(f"  {line}")
            
            print_warning("Vui lòng chạy lại script từ đầu")
            print_warning(f"Hoặc cài đặt thủ công: {python_cmd} -m pip install -r {requirements_file}")
            
            # Thử cài đặt từng package để tìm package lỗi
            print_info("Đang thử cài đặt từng package để tìm lỗi...")
            try:
                with open(requirements_file, 'r') as f:
                    lines = f.readlines()
                
                failed_packages = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        if package:
                            print_info(f"Đang thử cài: {package}...")
                            result = subprocess.run(
                                [python_cmd, "-m", "pip", "install", line],
                                capture_output=True,
                                text=True,
                                timeout=300
                            )
                            if result.returncode == 0:
                                print_success(f"  ✓ {package}")
                            else:
                                print_error(f"  ✗ {package} - Lỗi")
                                if result.stderr:
                                    print_error(f"    {result.stderr[:200]}")
                                failed_packages.append(package)
            except Exception as e:
                print_warning(f"Không thể phân tích lỗi chi tiết: {e}")
            
            return False
        
        print_success("Đã cài đặt dependencies thành công!")
        
        # Kiểm tra các packages quan trọng
        print_info("Kiểm tra packages quan trọng...")
        check_packages_script = """
import sys
import os
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)
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
        check_file = Path("/tmp/check_packages.py")
        with open(check_file, "w") as f:
            f.write(check_packages_script)
        
        # python_cmd should already be set, but ensure it's set just in case
        if not python_cmd:
            python_cmd = sys.executable
        
        result = subprocess.run(
            [python_cmd, str(check_file)],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())
        )
        
        if result.returncode != 0:
            print(result.stdout)
            print_error("Một số packages quan trọng chưa được cài đặt!")
            print_warning("⚠️ Vui lòng chạy lại script từ đầu và đợi cài đặt hoàn tất")
            print_warning("⚠️ KHÔNG interrupt quá trình cài đặt (có thể mất 10-20 phút)")
            return False
        else:
            print(result.stdout)
            print_success("Tất cả packages quan trọng đã được cài đặt")
        
        return True
        
    except Exception as e:
        print_error(f"Lỗi không mong đợi khi cài đặt: {e}")
        import traceback
        traceback.print_exc()
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

def cleanup_and_clone_repo(git_url: str = "https://github.com/HoangPhucDE/ciesta-assistant.git", 
                           branch: str = "main",
                           target_dir: str = "ciesta-assistant"):
    """
    Cleanup old repo and clone fresh from git (Colab only)
    
    Args:
        git_url: Git repository URL
        branch: Branch to clone (default: main)
        target_dir: Target directory name
    """
    if not is_colab():
        print_info("Không phải Colab - bỏ qua cleanup và clone")
        return False
    
    # Check if git is available
    git_check = subprocess.run(["which", "git"], capture_output=True, text=True)
    if git_check.returncode != 0:
        print_warning("Git chưa được cài đặt, đang cài đặt...")
        subprocess.run(["apt-get", "update", "-qq"], check=False)
        subprocess.run(["apt-get", "install", "-y", "-qq", "git"], check=False)
        print_success("Đã cài đặt git")
    
    print_header("CLEANUP VÀ CLONE REPO MỚI")
    
    current_dir = Path.cwd()
    target_path = current_dir / target_dir
    
    # Step 1: Remove old directory if exists
    if target_path.exists():
        print_info(f"Đang xóa thư mục cũ: {target_path}")
        try:
            shutil.rmtree(target_path)
            print_success(f"Đã xóa thư mục cũ: {target_path}")
        except Exception as e:
            print_error(f"Không thể xóa thư mục cũ: {e}")
            print_warning("Sẽ thử clone vào thư mục khác...")
            target_path = current_dir / f"{target_dir}-new"
            if target_path.exists():
                try:
                    shutil.rmtree(target_path)
                except Exception:
                    pass
    
    # Step 2: Clone fresh repo
    print_info(f"Đang clone repo từ: {git_url}")
    print_info(f"   Branch: {branch}")
    print_info(f"   Target: {target_path}")
    print_warning("⚠️ Quá trình này có thể mất 1-2 phút...")
    
    try:
        # Clone repository với shallow clone (chỉ lấy commit mới nhất)
        clone_cmd = ["git", "clone", "--depth", "1", "--branch", branch, git_url, str(target_path)]
        result = subprocess.run(
            clone_cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode != 0:
            print_warning(f"Không thể clone branch {branch}: {result.stderr}")
            # Try without branch specification (clone default branch)
            print_info("Thử clone branch mặc định...")
            clone_cmd = ["git", "clone", "--depth", "1", git_url, str(target_path)]
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                print_error(f"Lỗi khi clone repo: {result.stderr}")
                if result.stdout:
                    print_error(f"Output: {result.stdout}")
                return False
            else:
                print_info("Đã clone branch mặc định thành công")
        else:
            print_success(f"Đã clone branch {branch} thành công")
        
        print_success(f"Đã clone repo thành công vào: {target_path}")
        
        # Step 3: Change to cloned directory
        if target_path.exists():
            # Check if it's a valid repo
            if (target_path / "requirements.txt").exists() or (target_path / "requirements-colab.txt").exists():
                os.chdir(target_path)
                print_success(f"Đã chuyển vào thư mục: {Path.cwd()}")
                return True
            else:
                # Maybe it's a nested directory
                nested_paths = [
                    target_path / "ciesta-assistant",
                    target_path / "ciesta-asisstant",  # Typo variant
                ]
                for nested_path in nested_paths:
                    if nested_path.exists() and ((nested_path / "requirements.txt").exists() or (nested_path / "requirements-colab.txt").exists()):
                        os.chdir(nested_path)
                        print_success(f"Đã chuyển vào thư mục: {Path.cwd()}")
                        return True
                
                print_error(f"Thư mục clone không hợp lệ (không tìm thấy requirements.txt): {target_path}")
                print_info(f"Các file trong thư mục: {list(target_path.iterdir())[:10]}")
                return False
        else:
            print_error(f"Thư mục clone không tồn tại: {target_path}")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Timeout khi clone repo (quá 5 phút)")
        return False
    except Exception as e:
        print_error(f"Lỗi không mong đợi khi clone: {e}")
        import traceback
        traceback.print_exc()
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

def get_gpu_info():
    """Get GPU information including name and memory"""
    # First check with nvidia-smi
    nvidia_result = None
    try:
        nvidia_result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
        if nvidia_result.returncode != 0:
            return {'available': False, 'name': None, 'memory_gb': 0}
    except Exception:
        return {'available': False, 'name': None, 'memory_gb': 0}
    
    # Then check with PyTorch (from venv if available)
    try:
        # Try to import torch from venv
        venv_path = Path("venv_py310")
        if venv_path.exists():
            venv_site_packages = venv_path / "lib" / "python3.10" / "site-packages"
            if venv_site_packages.exists():
                import sys
                sys.path.insert(0, str(venv_site_packages))
        
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
            gpu_memory_gb = gpu_memory_bytes / (1024**3)
            return {
                'name': gpu_name,
                'memory_gb': gpu_memory_gb,
                'available': True
            }
    except Exception:
        # If torch not available, still return True if nvidia-smi works
        if nvidia_result and nvidia_result.returncode == 0:
            return {'available': True, 'name': 'GPU (detected by nvidia-smi)', 'memory_gb': 0}
        pass
    
    return {'available': False, 'name': None, 'memory_gb': 0}

def optimize_config_for_gpu(config_file: Path, gpu_info: dict):
    """Optimize config.yml for maximum speed on GPU while avoiding OOM"""
    # Get GPU memory from PyTorch
    gpu_memory_gb = None
    gpu_name = None
    
    try:
        # Try to import torch from venv
        venv_path = Path("venv_py310")
        if venv_path.exists():
            venv_site_packages = venv_path / "lib" / "python3.10" / "site-packages"
            if venv_site_packages.exists():
                import sys
                sys.path.insert(0, str(venv_site_packages))
        
        check_gpu_memory_script = """
import sys
import os
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
if os.path.exists(venv_path):
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
        check_file = Path("/tmp/check_gpu_memory.py")
        with open(check_file, "w") as f:
            f.write(check_gpu_memory_script)
        
        result = subprocess.run(
            [sys.executable, str(check_file)],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd()),
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            output = result.stdout.strip()
            if "|" in output:
                parts = output.split("|")
                gpu_memory_gb = float(parts[0])
                gpu_name = parts[1] if len(parts) > 1 else "Unknown"
    except Exception as e:
        print_warning(f"Không thể kiểm tra GPU memory: {e}")
    
    if not gpu_info['available'] or (gpu_memory_gb and gpu_memory_gb == 0):
        print_warning("Không có GPU - Giữ cấu hình mặc định")
        return False
    
    if gpu_memory_gb:
        print_info(f"GPU: {gpu_name} ({gpu_memory_gb:.1f} GB)")
    else:
        print_info(f"GPU: {gpu_info.get('name', 'Unknown')}")
        gpu_memory_gb = 0  # Fallback
    
    # Read config
    with open(config_file, "r", encoding="utf-8") as f:
        config_content = f.read()
    
    original_content = config_content
    optimized = False
    
    # Tối ưu batch size dựa trên GPU memory
    # Lưu ý: T4 thường có ~15GB nhưng có thể hiển thị 14.7-14.9 GB, nên coi >=14.5 GB là GPU lớn
    if gpu_memory_gb >= 14.5:  # T4 (~15GB), V100, A100
        print_success(f"🚀 GPU lớn phát hiện ({gpu_name}) - Tăng batch size để tận dụng GPU")
        print_info(f"   💡 GPU Memory: {gpu_memory_gb:.1f} GB - Có thể tăng batch size cao hơn")
        
        # Tối ưu PhoBERTFeaturizer batch_size (sau pooling_strategy)
        # Ultra optimization: Với T4 15GB, tăng lên 256 để sử dụng 80%+ GPU memory
        phobert_batch = 256
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            rf'\1 {phobert_batch}  # Ultra optimization cho GPU lớn (T4/V100/A100) - tận dụng tối đa GPU memory',
            config_content
        )
        print_success(f"   ✅ PhoBERTFeaturizer batch_size: {phobert_batch}")
        
        # Ultra optimization: DIETClassifier batch_size - tăng cao [192, 384] để training nhanh hơn 2-3x
        # T4 15GB có thể chịu được batch size này
        diet_batch = [192, 384]
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\](\s*#.*)?',
            rf'\1{diet_batch}  # Ultra optimization cho GPU lớn - training nhanh hơn 2-3x',
            config_content
        )
        # Nếu có pattern khác từ lần tối ưu trước, cũng cập nhật
        config_content = re.sub(
            r'(batch_size:\s*)\[64,\s*128\](\s*#.*)?',
            rf'\1{diet_batch}  # Ultra optimization cho GPU lớn - training nhanh hơn 2-3x',
            config_content
        )
        config_content = re.sub(
            r'(batch_size:\s*)\[128,\s*256\](\s*#.*)?',
            rf'\1{diet_batch}  # Ultra optimization cho GPU lớn - training nhanh hơn 2-3x',
            config_content
        )
        print_success(f"   ✅ DIETClassifier batch_size: {diet_batch}")
        optimized = True
        
    elif gpu_memory_gb >= 8:  # P100, K80, hoặc GPU trung bình
        print_info(f"⚡ GPU trung bình phát hiện ({gpu_name}) - Tăng batch size vừa phải")
        phobert_batch = 96
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            rf'\1 {phobert_batch}  # Tối ưu cho GPU trung bình',
            config_content
        )
        diet_batch = [64, 128]
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\](\s*#.*)?',
            rf'\1{diet_batch}  # Tối ưu cho GPU trung bình',
            config_content
        )
        print_success(f"   ✅ PhoBERTFeaturizer batch_size: {phobert_batch}")
        print_success(f"   ✅ DIETClassifier batch_size: {diet_batch}")
        optimized = True
        
    elif gpu_memory_gb >= 4:  # GPU nhỏ
        print_info(f"📊 GPU nhỏ phát hiện ({gpu_name}) - Tăng batch size nhẹ")
        phobert_batch = 48
        config_content = re.sub(
            r'(pooling_strategy:\s*"mean_max"\s*\n\s*batch_size:)\s*\d+(\s*#.*)?',
            rf'\1 {phobert_batch}  # Tối ưu cho GPU nhỏ',
            config_content
        )
        diet_batch = [32, 64]
        config_content = re.sub(
            r'(batch_size:\s*)\[16,\s*32\]',
            rf'\1{diet_batch}  # Tối ưu cho GPU nhỏ',
            config_content
        )
        print_success(f"   ✅ PhoBERTFeaturizer batch_size: {phobert_batch}")
        print_success(f"   ✅ DIETClassifier batch_size: {diet_batch}")
        optimized = True
    else:
        print_info("   ℹ️ GPU memory nhỏ - Giữ batch size mặc định")
    
    # Ghi lại config nếu có thay đổi
    if optimized and config_content != original_content:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print_success("   ✅ Đã tối ưu batch size trong config.yml")
        print_info("   💡 Batch size lớn hơn sẽ:")
        print_info("      - Sử dụng GPU hiệu quả hơn")
        print_info("      - Training nhanh hơn (nhiều samples/batch)")
        print_info("      - Tận dụng GPU memory tốt hơn")
        
        # Cũng cập nhật file gốc trong config/rasa/ để đồng bộ
        rasa_config_path = Path.cwd() / "config" / "rasa" / "config.yml"
        if rasa_config_path.exists():
            with open(rasa_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            print_success("   ✅ Đã cập nhật cả file gốc trong config/rasa/")
        return True
    else:
        print_info("   ℹ️ Config đã tối ưu hoặc không cần thay đổi")
    
    return False

def ultra_optimize_for_gpu(config_file: Path = None):
    """
    Ultra optimize config for maximum GPU usage
    - Disable validation during training để tăng tốc
    - Đảm bảo batch size đã được set cao
    """
    print_header("ULTRA OPTIMIZATION FOR GPU")
    
    if config_file is None:
        config_file = Path("config.yml")
        if not config_file.exists():
            config_file = Path("config/rasa/config.yml")
    
    if not config_file.exists():
        print_warning("Không tìm thấy config.yml để ultra optimize")
        return False
    
    print_info("🚀 Ultra optimization: Disable validation để tăng tốc training")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    original_content = config_content
    optimized = False
    
    # 1. Disable validation during training (chỉ validate cuối cùng)
    # Tìm DIETClassifier và set evaluate_every_number_of_epochs: -1
    if re.search(r'evaluate_every_number_of_epochs:\s*\d+', config_content):
        config_content = re.sub(
            r'evaluate_every_number_of_epochs:\s*\d+',
            'evaluate_every_number_of_epochs: -1  # Disable validation during training để tăng tốc',
            config_content
        )
        print_success("   ✅ Disabled validation during training (evaluate_every_number_of_epochs: -1)")
        optimized = True
    
    # 2. Đảm bảo evaluate_on_number_of_examples: 0 (không validate trong training)
    if re.search(r'evaluate_on_number_of_examples:\s*\d+', config_content):
        config_content = re.sub(
            r'evaluate_on_number_of_examples:\s*\d+',
            'evaluate_on_number_of_examples: 0  # Disable validation để tăng tốc',
            config_content
        )
        print_success("   ✅ Disabled evaluation examples (evaluate_on_number_of_examples: 0)")
        optimized = True
    
    # 3. Ghi lại config nếu có thay đổi
    if optimized and config_content != original_content:
        with open(config_file, "w", encoding="utf-8") as f:
            f.write(config_content)
        print_success("   ✅ Đã ultra optimize config.yml")
        print_info("   💡 Validation đã được disable - Training sẽ nhanh hơn 2-3x")
        
        # Cũng cập nhật file gốc trong config/rasa/ để đồng bộ
        rasa_config_path = Path.cwd() / "config" / "rasa" / "config.yml"
        if rasa_config_path.exists() and rasa_config_path != config_file:
            with open(rasa_config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            print_success("   ✅ Đã cập nhật cả file gốc trong config/rasa/")
        return True
    else:
        print_info("   ℹ️ Config đã được ultra optimize hoặc không cần thay đổi")
    
    return False


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

def parse_rasa_progress(line: str):
    """Parse Rasa training progress line"""
    # Pattern: Epochs: 10% 60/600 [02:46<27:40:43, 166.35s/it, t_loss=32.3, m_acc=0.228, i_acc=0.186, e_f1=0.0868]
    pattern = r'Epochs:\s*(\d+)%\s*(\d+)/(\d+)\s*\[([\d:]+)<([\d:]+),\s*([\d.]+)s/it(?:,\s*t_loss=([\d.]+))?(?:,\s*m_acc=([\d.]+))?(?:,\s*i_acc=([\d.]+))?(?:,\s*e_f1=([\d.]+))?\]'
    match = re.search(pattern, line)
    
    if match:
        return {
            'percent': int(match.group(1)),
            'current': int(match.group(2)),
            'total': int(match.group(3)),
            'elapsed': match.group(4),
            'remaining': match.group(5),
            'time_per_epoch': float(match.group(6)),
            't_loss': float(match.group(7)) if match.group(7) else None,
            'm_acc': float(match.group(8)) if match.group(8) else None,
            'i_acc': float(match.group(9)) if match.group(9) else None,
            'e_f1': float(match.group(10)) if match.group(10) else None,
        }
    return None

def format_time(seconds: float) -> str:
    """Format seconds to human readable time"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"

def print_progress_bar(percent: int, width: int = 40):
    """Print progress bar"""
    filled = int(width * percent / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percent}%"

def train_nlu(epochs: Optional[int] = None):
    """Train NLU model with real-time progress display"""
    print_header("BẮT ĐẦU TRAIN NLU MODEL")
    
    # Ensure we're in project root
    project_root = find_project_root()
    if project_root and project_root != Path.cwd():
        os.chdir(project_root)
        print_info(f"Đã chuyển vào project root: {Path.cwd()}")
    
    # Check GPU (get detailed info from venv)
    gpu_info = get_gpu_info()
    
    # Try to get more detailed GPU info from venv
    venv_path = Path("venv_py310")
    if venv_path.exists():
        venv_site_packages = venv_path / "lib" / "python3.10" / "site-packages"
        if venv_site_packages.exists():
            try:
                import sys
                sys.path.insert(0, str(venv_site_packages))
                import torch
                if torch.cuda.is_available():
                    gpu_name = torch.cuda.get_device_name(0)
                    gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
                    gpu_memory_gb = gpu_memory_bytes / (1024**3)
                    gpu_info = {
                        'available': True,
                        'name': gpu_name,
                        'memory_gb': gpu_memory_gb
                    }
            except Exception:
                pass  # Use gpu_info from get_gpu_info()
    
    if gpu_info['available']:
        gpu_name = gpu_info.get('name', 'GPU')
        gpu_memory_gb = gpu_info.get('memory_gb', 0)
        if gpu_memory_gb > 0:
            print_success(f"GPU đã sẵn sàng: {gpu_name} ({gpu_memory_gb:.1f} GB)")
        else:
            print_success(f"GPU đã sẵn sàng: {gpu_name}")
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
    
    # Show expected training time based on GPU
    gpu_memory_gb = gpu_info.get('memory_gb', 0)
    if gpu_info['available']:
        if gpu_memory_gb >= 14.5:
            print_info("⚡ Training với GPU lớn (T4/V100/A100) - Ước tính: 15-30 phút")
        elif gpu_memory_gb >= 8:
            print_info("⚡ Training với GPU trung bình - Ước tính: 30-60 phút")
        elif gpu_memory_gb > 0:
            print_info("⚡ Training với GPU nhỏ - Ước tính: 45-90 phút")
        else:
            print_info("⚡ Training với GPU (memory unknown) - Ước tính: 30-60 phút")
    else:
        print_info("⏳ Training với CPU - Ước tính: 1-2 giờ")
    
    print()
    
    start_time = time.time()
    last_update_time = start_time
    last_epoch = 0
    total_epochs = None
    progress_data = None
    
    # Check Rasa đã được cài đặt trước khi train
    print_info("Kiểm tra Rasa trước khi train...")
    check_rasa_script = """
import sys
import os
venv_path = os.path.join(os.getcwd(), 'venv_py310', 'lib', 'python3.10', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)

try:
    import rasa
    print(f"✅ Rasa version: {rasa.__version__}")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Rasa chưa được cài đặt: {e}")
    sys.exit(1)
"""
    check_file = Path("/tmp/check_rasa.py")
    with open(check_file, "w") as f:
        f.write(check_rasa_script)
    
    rasa_check = subprocess.run(
        [sys.executable, str(check_file)],
        capture_output=True,
        text=True,
        cwd=str(Path.cwd())
    )
    
    print(rasa_check.stdout)
    if rasa_check.stderr:
        print(rasa_check.stderr)
    
    if rasa_check.returncode != 0:
        print_error("Rasa chưa được cài đặt!")
        print_warning("⚠️ Vui lòng chạy lại script từ đầu và đợi cài đặt hoàn tất")
        print_warning("⚠️ KHÔNG interrupt quá trình cài đặt dependencies (có thể mất 10-20 phút)")
        return False
    
    print_success("Rasa đã sẵn sàng - Bắt đầu training...")
    
    try:
        # Train NLU with real-time output (use config.yml from root)
        # Đảm bảo config.yml tồn tại ở root trước khi train
        if not (Path.cwd() / "config.yml").exists():
            print_error("config.yml không tồn tại ở root! Không thể train.")
            return False
        
        cmd = [sys.executable, "-m", "rasa", "train", "nlu", "--config", "config.yml"]
        if epochs:
            print_warning("Epochs được cấu hình trong config.yml")
        
        # Start process with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            cwd=str(Path.cwd())
        )
        
        print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.HEADER}📊 TIẾN ĐỘ TRAINING{Colors.ENDC}")
        print(f"{Colors.OKCYAN}{'='*80}{Colors.ENDC}\n")
        
        # Read output line by line
        for line in process.stdout:
            line = line.rstrip()
            
            # Parse progress line
            progress = parse_rasa_progress(line)
            if progress:
                progress_data = progress
                total_epochs = progress['total']
                current_epoch = progress['current']
                
                # Calculate speed
                current_time = time.time()
                if current_epoch > last_epoch:
                    time_diff = current_time - last_update_time
                    epochs_diff = current_epoch - last_epoch
                    if time_diff > 0:
                        epochs_per_sec = epochs_diff / time_diff
                        time_per_epoch = time_diff / epochs_diff
                    else:
                        epochs_per_sec = 0
                        time_per_epoch = 0
                    
                    last_update_time = current_time
                    last_epoch = current_epoch
                else:
                    epochs_per_sec = 0
                    time_per_epoch = progress.get('time_per_epoch', 0)
                
                # Calculate ETA
                remaining_epochs = total_epochs - current_epoch
                if epochs_per_sec > 0:
                    eta_seconds = remaining_epochs / epochs_per_sec
                elif time_per_epoch > 0:
                    eta_seconds = remaining_epochs * time_per_epoch
                else:
                    eta_seconds = 0
                
                # Calculate elapsed time
                elapsed_seconds = current_time - start_time
                
                # Print progress block (simple scrolling output for Colab compatibility)
                print(f"\n{Colors.OKCYAN}{'─'*80}{Colors.ENDC}")
                print(f"{Colors.BOLD}Epoch: {Colors.OKGREEN}{current_epoch}/{total_epochs}{Colors.ENDC} {Colors.BOLD}({progress['percent']}%){Colors.ENDC}")
                print(f"{Colors.OKCYAN}{print_progress_bar(progress['percent'])}{Colors.ENDC}")
                
                # Metrics
                metrics_line = []
                if progress['t_loss'] is not None:
                    metrics_line.append(f"{Colors.BOLD}Loss:{Colors.ENDC} {Colors.WARNING}{progress['t_loss']:.4f}{Colors.ENDC}")
                if progress['i_acc'] is not None:
                    metrics_line.append(f"{Colors.BOLD}Intent Acc:{Colors.ENDC} {Colors.OKGREEN}{progress['i_acc']:.4f}{Colors.ENDC}")
                if progress['e_f1'] is not None:
                    metrics_line.append(f"{Colors.BOLD}Entity F1:{Colors.ENDC} {Colors.OKGREEN}{progress['e_f1']:.4f}{Colors.ENDC}")
                if progress['m_acc'] is not None:
                    metrics_line.append(f"{Colors.BOLD}Memory Acc:{Colors.ENDC} {Colors.OKGREEN}{progress['m_acc']:.4f}{Colors.ENDC}")
                
                if metrics_line:
                    print(f"  {' | '.join(metrics_line)}")
                
                # Speed and time info
                speed_line = []
                if epochs_per_sec > 0:
                    speed_line.append(f"{Colors.BOLD}Tốc độ:{Colors.ENDC} {Colors.OKCYAN}{epochs_per_sec:.3f} epochs/s{Colors.ENDC}")
                if time_per_epoch > 0:
                    speed_line.append(f"{Colors.BOLD}Thời gian/epoch:{Colors.ENDC} {Colors.OKCYAN}{format_time(time_per_epoch)}{Colors.ENDC}")
                speed_line.append(f"{Colors.BOLD}Đã trôi qua:{Colors.ENDC} {Colors.OKCYAN}{format_time(elapsed_seconds)}{Colors.ENDC}")
                if eta_seconds > 0:
                    speed_line.append(f"{Colors.BOLD}ETA:{Colors.ENDC} {Colors.WARNING}{format_time(eta_seconds)}{Colors.ENDC}")
                
                if speed_line:
                    print(f"  {' | '.join(speed_line)}")
                print(f"{Colors.OKCYAN}{'─'*80}{Colors.ENDC}", flush=True)
            else:
                # Print other important lines (warnings, errors, etc.)
                if any(keyword in line.lower() for keyword in ['warning', 'error', 'exception', 'traceback']):
                    print(f"\n{Colors.WARNING}{line}{Colors.ENDC}")
                elif any(keyword in line.lower() for keyword in ['success', 'complete', 'finished', 'done']):
                    print(f"\n{Colors.OKGREEN}{line}{Colors.ENDC}")
                elif line.strip() and not line.startswith('Epochs:'):
                    # Print other non-empty lines (but not progress lines)
                    if 'Processing' in line or 'Training' in line or 'Validating' in line:
                        print(f"\n{Colors.OKCYAN}{line}{Colors.ENDC}")
        
        # Wait for process to complete
        return_code = process.wait()
        
        print(f"\n{Colors.OKCYAN}{'='*80}{Colors.ENDC}\n")
        
        if return_code != 0:
            print_error(f"Training thất bại với exit code: {return_code}")
            return False
        
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        
        print_success(f"Training hoàn tất! Thời gian: {hours}h {minutes}m {seconds}s")
        
        # Print final metrics if available
        if progress_data:
            print(f"\n{Colors.BOLD}📊 Kết quả cuối cùng:{Colors.ENDC}")
            if progress_data['t_loss'] is not None:
                print(f"  {Colors.BOLD}Training Loss:{Colors.ENDC} {progress_data['t_loss']:.4f}")
            if progress_data['i_acc'] is not None:
                print(f"  {Colors.BOLD}Intent Accuracy:{Colors.ENDC} {progress_data['i_acc']:.4f}")
            if progress_data['e_f1'] is not None:
                print(f"  {Colors.BOLD}Entity F1 Score:{Colors.ENDC} {progress_data['e_f1']:.4f}")
            if progress_data['m_acc'] is not None:
                print(f"  {Colors.BOLD}Memory Accuracy:{Colors.ENDC} {progress_data['m_acc']:.4f}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print_error(f"Lỗi khi train: {e}")
        return False
    except KeyboardInterrupt:
        print_warning("\nTraining bị dừng bởi người dùng")
        if 'process' in locals():
            process.terminate()
        return False
    except Exception as e:
        print_error(f"Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Step 0: Cleanup and clone fresh repo (Colab only)
        print_header("CLEANUP VÀ CLONE REPO MỚI")
        print_info("🔄 Đang xóa repo cũ và clone repo mới từ git...")
        
        # Get git URL and branch from environment or use defaults
        git_url = os.environ.get("CIESTA_GIT_URL", "https://github.com/HoangPhucDE/ciesta-assistant.git")
        git_branch = os.environ.get("CIESTA_GIT_BRANCH", "main")
        
        print_info(f"   Git URL: {git_url}")
        print_info(f"   Branch: {git_branch}")
        
        # Go to /content (Colab's default directory)
        content_dir = Path("/content")
        if content_dir.exists():
            os.chdir(content_dir)
            print_info(f"Đã chuyển vào: {Path.cwd()}")
        
        # Cleanup and clone
        if cleanup_and_clone_repo(git_url=git_url, branch=git_branch, target_dir="ciesta-assistant"):
            print_success("✅ Đã clone repo mới thành công")
            # Now we're in the cloned directory
            project_root = Path.cwd()
        else:
            print_warning("⚠️ Không thể clone repo mới, sẽ tìm project root hiện có...")
            project_root = find_project_root()
            if project_root:
                os.chdir(project_root)
                print_info(f"Đã chuyển vào project root: {Path.cwd()}")
            else:
                print_error("Không tìm thấy project root")
                return False
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
    
    # Verify we're in the right place
    if not (Path.cwd() / "requirements.txt").exists() and not (Path.cwd() / "requirements-colab.txt").exists():
        print_error("Không tìm thấy requirements file trong project root")
        print_info(f"Thư mục hiện tại: {Path.cwd()}")
        return False
    
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
    
    # Step 5.5: Cập nhật config để dùng model online
    print_header("CẬP NHẬT CONFIG")
    current_dir = Path.cwd()
    
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
            print_info(f"Tìm thấy config tại: {path}")
            break
    
    if not config_file:
        print_error("Không tìm thấy config.yml")
        return False
    
    # Nếu config ở trong config/rasa/, copy vào root để Rasa tìm thấy
    root_config = current_dir / "config.yml"
    rasa_config = current_dir / "config/rasa/config.yml"
    
    if config_path_used == rasa_config:
        print_info(f"Copy config từ {rasa_config} -> {root_config}")
        
        # Xóa file cũ nếu tồn tại
        root_config_str = str(root_config)
        if os.path.lexists(root_config_str):
            try:
                if os.path.islink(root_config_str):
                    os.unlink(root_config_str)
                else:
                    os.remove(root_config_str)
            except Exception:
                pass
        
        # Copy file
        try:
            shutil.copyfile(str(rasa_config), root_config_str)
            if os.path.exists(root_config_str) and os.path.isfile(root_config_str):
                print_success("Đã copy config.yml vào root")
                config_file = "config.yml"
        except Exception as e:
            print_error(f"Không thể copy file: {e}")
            return False
    
    # Copy các file config khác vào root
    rasa_config_files = ["domain.yml", "endpoints.yml", "credentials.yml"]
    for filename in rasa_config_files:
        rasa_path = current_dir / "config/rasa" / filename
        root_path = current_dir / filename
        
        if rasa_path.exists():
            root_path_str = str(root_path)
            if os.path.lexists(root_path_str):
                try:
                    if os.path.islink(root_path_str):
                        os.unlink(root_path_str)
                    else:
                        os.remove(root_path_str)
                except Exception:
                    pass
            
            try:
                shutil.copyfile(str(rasa_path), root_path_str)
                if os.path.exists(root_path_str) and os.path.isfile(root_path_str):
                    print_success(f"Đã copy {filename} vào root")
            except Exception as e:
                print_warning(f"Không thể copy {filename}: {e}")
    
    # Đọc và cập nhật config (đảm bảo dùng file ở root)
    config_to_update = current_dir / "config.yml"
    
    if not config_to_update.exists():
        print_error("config.yml không tồn tại ở root!")
        return False
    
    print_info(f"Đang cập nhật: {config_to_update}")
    
    # Đọc config
    with open(config_to_update, "r", encoding="utf-8") as f:
        config = f.read()
    
    # Cập nhật config để dùng model online
    config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
    config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)
    
    # Ghi lại config vào root
    with open(config_to_update, "w", encoding="utf-8") as f:
        f.write(config)
    
    # Cũng cập nhật file gốc trong config/rasa/ để đồng bộ
    if rasa_config.exists():
        with open(rasa_config, "w", encoding="utf-8") as f:
            f.write(config)
        print_success("Đã cập nhật cả file gốc trong config/rasa/")
    
    print_success("Đã cập nhật config để dùng model online")
    
    # Step 6: Verify config
    if not verify_config():
        print_warning("Config có thể chưa đúng - vui lòng kiểm tra")
    
    # Step 6.5: Entity alignments
    # Lưu ý: Entity alignments nên được fix trước bằng script sync_location_names.py
    # Script này chỉ phục vụ training, không fix entities
    # Xem docs/README_SYNC_LOCATIONS.md để biết thêm chi tiết
    print_info("💡 Lưu ý: Nếu có entity alignment warnings, chạy sync_location_names.py trước khi train")
    print_info("   Xem: scripts/training/sync_location_names.py hoặc docs/README_SYNC_LOCATIONS.md")
    
    # Step 7: Optimize config for GPU
    print_header("TỐI ƯU HÓA CONFIG CHO GPU")
    gpu_info = get_gpu_info()
    if gpu_info['available']:
        config_file_path = Path("config.yml")
        if not config_file_path.exists():
            config_file_path = Path("config/rasa/config.yml")
        optimize_config_for_gpu(config_file_path, gpu_info)
        
        # Ultra optimization cho GPU lớn (T4/V100/A100)
        if gpu_info.get('memory_gb', 0) >= 14.5:
            ultra_optimize_for_gpu(config_file_path)
    
    # Step 7.5: Verify config
    verify_config()
    
    # Step 8: Train NLU
    if not train_nlu():
        print_error("Training thất bại")
        return False
    
    # Step 9: Download model
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