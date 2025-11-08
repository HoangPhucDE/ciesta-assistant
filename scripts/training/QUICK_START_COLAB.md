# ⚡ Quick Start - Train trên Google Colab

Hướng dẫn nhanh để train Rasa NLU model trên Google Colab trong 5 phút.

## 🚀 Cách 1: Sử dụng Script Tự Động (Nhanh nhất)

### Bước 1: Mở Colab và Clone Repo

```python
# Chạy cell này trong Colab
!git clone YOUR_REPO_URL
%cd ciesta-asisstant
```

### Bước 2: Chạy Script Tự Động

```python
# Chạy script training tự động
!python scripts/training/train_on_colab.py
```

**Xong!** Script sẽ tự động:
- ✅ Cài đặt dependencies
- ✅ Tải PhoBERT-large
- ✅ Train NLU model
- ✅ Download model về máy

---

## 🛠️ Cách 2: Training Thủ Công (5 bước)

### 1. Cài đặt Dependencies

```python
%pip install -q -r requirements.txt
```

### 2. Tải PhoBERT-large

```python
from huggingface_hub import snapshot_download
import os

os.makedirs("models_hub/phobert-large", exist_ok=True)
snapshot_download(
    repo_id="vinai/phobert-large",
    local_dir="models_hub/phobert-large",
    local_dir_use_symlinks=False
)
```

### 3. Setup Model Path

```python
import os, shutil
os.makedirs("models", exist_ok=True)
if os.path.exists("models/phobert-large"):
    shutil.rmtree("models/phobert-large")
shutil.copytree("models_hub/phobert-large", "models/phobert-large")
```

### 4. Train NLU

```python
!rasa train nlu
```

### 5. Download Model

```python
from google.colab import files
from pathlib import Path

latest_model = max(Path("models").glob("*.tar.gz"), key=lambda x: x.stat().st_mtime)
files.download(str(latest_model))
```

---

## 💡 Tips

### Sử dụng GPU (Khuyến nghị)
1. `Runtime` → `Change runtime type` → `GPU`
2. Training nhanh hơn 5-10 lần

### Giảm Memory (Nếu bị lỗi)
Sửa `config.yml`:
```yaml
batch_size: [8, 16]  # Thay vì [16, 32]
epochs: 300          # Thay vì 600
```

### Thời gian Training
- **CPU**: 1-2 giờ
- **GPU T4**: 20-40 phút
- **GPU V100**: 15-30 phút

---

## 📝 Files Cần Thiết

Đảm bảo có các file sau:
- ✅ `config.yml`
- ✅ `data/nlu.yml`
- ✅ `custom_components/phobert_featurizer.py`
- ✅ `requirements.txt`

---

## 🔗 Xem thêm

- Chi tiết đầy đủ: [README_COLAB.md](README_COLAB.md)
- Notebook sẵn: [colab_notebook.ipynb](colab_notebook.ipynb)

