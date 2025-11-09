# 🔧 Fix Lỗi "Không tìm thấy requirements.txt" trên Colab

## ⚠️ Vấn Đề

Script không tìm thấy `requirements.txt` vì đang chạy từ thư mục sai.

## ✅ Giải Pháp

### Cách 1: Chạy từ đúng thư mục (Khuyến nghị)

```python
# Bước 1: Clone và chuyển vào thư mục
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# Bước 2: Kiểm tra
import os
print(f"Thư mục hiện tại: {os.getcwd()}")
!ls -la requirements.txt

# Bước 3: Chạy script
!python scripts/training/train_on_colab.py
```

### Cách 2: Script tự động (Đã cập nhật)

Script đã được cập nhật để tự động tìm thư mục project. Chỉ cần:

```python
# Clone repo
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git

# Chạy script (sẽ tự động tìm và chuyển vào thư mục đúng)
!python ciesta-assistant/scripts/training/train_on_colab.py
```

### Cách 3: Training thủ công (Nếu script vẫn lỗi)

```python
# 1. Clone và chuyển vào thư mục
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant

# 2. Cài đặt dependencies
%pip install -q -r requirements.txt

# 3. Tải model
from huggingface_hub import snapshot_download
import os
os.makedirs("models_hub/phobert-large", exist_ok=True)
snapshot_download(
    repo_id="vinai/phobert-large",
    local_dir="models_hub/phobert-large",
    local_dir_use_symlinks=False
)

# 4. Setup model path
import shutil
os.makedirs("models", exist_ok=True)
if os.path.exists("models/phobert-large"):
    shutil.rmtree("models/phobert-large")
shutil.copytree("models_hub/phobert-large", "models/phobert-large")

# 5. Train
!rasa train nlu

# 6. Download model
from google.colab import files
from pathlib import Path
latest_model = max(Path("models").glob("*.tar.gz"), key=lambda x: x.stat().st_mtime)
files.download(str(latest_model))
```

## 🔍 Kiểm Tra

```python
import os
from pathlib import Path

# Kiểm tra thư mục hiện tại
print(f"Thư mục hiện tại: {os.getcwd()}")

# Kiểm tra requirements.txt
req_file = Path("requirements.txt")
print(f"requirements.txt tồn tại: {req_file.exists()}")
if req_file.exists():
    print(f"  Đường dẫn: {req_file.resolve()}")

# Kiểm tra ciesta-assistant
ciesta_dir = Path("ciesta-assistant")
print(f"ciesta-assistant tồn tại: {ciesta_dir.exists()}")
if ciesta_dir.exists():
    req_in_ciesta = ciesta_dir / "requirements.txt"
    print(f"  requirements.txt trong ciesta-assistant: {req_in_ciesta.exists()}")
```

## 📝 Checklist

- [ ] Đã clone repository
- [ ] Đã chuyển vào thư mục `ciesta-assistant`
- [ ] Đã kiểm tra `requirements.txt` tồn tại
- [ ] Đã chạy script từ đúng thư mục

## 🚀 Quick Fix (Copy toàn bộ)

```python
# Setup và chạy tự động
import os
from pathlib import Path

# Clone nếu chưa có
if not Path("ciesta-assistant").exists():
    !git clone https://github.com/HoangPhucDE/ciesta-assistant.git

# Chuyển vào thư mục
%cd ciesta-assistant
print(f"✅ Thư mục: {os.getcwd()}")

# Kiểm tra files
if Path("requirements.txt").exists():
    print("✅ requirements.txt tồn tại")
    !python scripts/training/train_on_colab.py
else:
    print("❌ Không tìm thấy requirements.txt")
    print("Vui lòng kiểm tra lại")
```

