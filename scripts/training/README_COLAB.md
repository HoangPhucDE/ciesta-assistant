# 🚀 Hướng dẫn Train trên Google Colab

Hướng dẫn chi tiết để train Rasa NLU model với PhoBERT-large trên Google Colab.

## 📋 Yêu cầu

1. **Google Colab account** (miễn phí)
2. **Files cần thiết**:
   - `config.yml`
   - `data/nlu.yml`
   - `domain.yml`
   - `custom_components/phobert_featurizer.py`
   - `custom_components/vietnamese_preprocessor.py`
   - `requirements.txt`
   - `actions/actions.py` (nếu có)

## 🎯 Cách 1: Sử dụng Script Tự Động (Khuyến nghị)

### Bước 1: Mở Google Colab

1. Truy cập: https://colab.research.google.com/
2. Tạo notebook mới hoặc mở `colab_notebook.ipynb`

### Bước 2: Upload Files

**Cách A: Clone từ Git (Khuyến nghị)**

```python
# Chạy trong cell đầu tiên
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
```

**Lưu ý:** Tên thư mục sau khi clone là `ciesta-assistant` (không phải `ciesta-asisstant`)

**Cách B: Upload thủ công**

1. Upload tất cả files cần thiết vào Colab
2. Sử dụng file browser bên trái để upload

### Bước 3: Chạy Script Tự Động

```python
# Chạy script training tự động
!python scripts/training/train_on_colab.py
```

Script sẽ tự động:
- ✅ Cài đặt dependencies
- ✅ Tải PhoBERT-large model
- ✅ Setup custom components
- ✅ Train NLU model
- ✅ Download model về máy local

## 🎯 Cách 2: Training Thủ Công

### Bước 1: Cài đặt Dependencies

```python
!pip install -q -r requirements.txt
```

### Bước 2: Tải PhoBERT-large Model

```python
from huggingface_hub import snapshot_download
import os

os.makedirs("models_hub/phobert-large", exist_ok=True)

snapshot_download(
    repo_id="vinai/phobert-large",
    local_dir="models_hub/phobert-large",
    local_dir_use_symlinks=False,
    resume_download=True
)

print("✅ Đã tải model thành công")
```

### Bước 3: Setup Model Path

```python
import os
import shutil

os.makedirs("models", exist_ok=True)

# Tạo symlink hoặc copy
if os.path.exists("models/phobert-large"):
    if os.path.islink("models/phobert-large"):
        os.unlink("models/phobert-large")
    else:
        shutil.rmtree("models/phobert-large")

try:
    os.symlink("../models_hub/phobert-large", "models/phobert-large")
    print("✅ Đã tạo symlink")
except:
    shutil.copytree("models_hub/phobert-large", "models/phobert-large")
    print("✅ Đã copy model")
```

### Bước 4: Kiểm tra Config

Đảm bảo `config.yml` có cấu hình:

```yaml
- name: custom_components.phobert_featurizer.PhoBERTFeaturizer
  model_name: "models/phobert-large"
  cache_dir: null
  max_length: 256
  pooling_strategy: "mean_max"
```

### Bước 5: Train NLU Model

```python
!rasa train nlu
```

### Bước 6: Download Model

```python
from google.colab import files
from pathlib import Path

models_dir = Path("models")
model_files = list(models_dir.glob("*.tar.gz"))

if model_files:
    # Get latest model
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)
    print(f"📦 Model mới nhất: {latest_model.name}")
    print(f"📊 Kích thước: {latest_model.stat().st_size / (1024*1024):.2f} MB")
    
    files.download(str(latest_model))
    print("✅ Đã bắt đầu tải model về máy")
else:
    print("❌ Không tìm thấy model")
```

## 🔧 Tối Ưu Hóa cho Colab

### Sử dụng GPU (Khuyến nghị)

1. Vào `Runtime` → `Change runtime type`
2. Chọn `GPU` (T4 hoặc tốt hơn)
3. Training sẽ nhanh hơn 5-10 lần

### Giảm Memory Usage

Nếu gặp lỗi Out of Memory, chỉnh sửa `config.yml`:

```yaml
- name: DIETClassifier
  batch_size: [8, 16]  # Giảm từ [16, 32]
  epochs: 300          # Giảm từ 600
```

### Tăng tốc Training

```yaml
- name: DIETClassifier
  epochs: 400          # Giảm epochs để train nhanh hơn
  batch_size: [32, 64] # Tăng batch size nếu có GPU
```

## 🔍 Troubleshooting

### Lỗi: Out of Memory

**Giải pháp:**
1. Giảm `batch_size` trong `config.yml`
2. Giảm `epochs`
3. Sử dụng PhoBERT-base thay vì Large

### Lỗi: Training quá lâu

**Giải pháp:**
1. Sử dụng GPU
2. Giảm `epochs` xuống 300-400
3. Giảm `batch_size`

### Lỗi: Không tìm thấy model

**Giải pháp:**
1. Kiểm tra đường dẫn trong `config.yml`
2. Đảm bảo model đã được tải vào `models_hub/phobert-large`
3. Kiểm tra symlink hoặc copy đã tạo chưa

### Lỗi: Import error

**Giải pháp:**
1. Chạy lại cell cài đặt dependencies
2. Kiểm tra `requirements.txt` có đầy đủ không
3. Restart runtime: `Runtime` → `Restart runtime`

### Lỗi: Cannot find custom component

**Giải pháp:**
1. Đảm bảo `custom_components/phobert_featurizer.py` đã được upload
2. Kiểm tra `custom_components/__init__.py` có tồn tại không
3. Tạo file `__init__.py` nếu chưa có:
   ```python
   # custom_components/__init__.py
   # File này để Python nhận diện thư mục là package
   ```

## 📊 Thời Gian Training

- **CPU**: 1-2 giờ (600 epochs)
- **GPU T4**: 20-40 phút (600 epochs)
- **GPU V100**: 15-30 phút (600 epochs)

## ✅ Checklist

Trước khi train, đảm bảo:

- [ ] Đã upload tất cả files cần thiết
- [ ] Đã cài đặt dependencies
- [ ] Đã tải PhoBERT-large model
- [ ] Đã tạo symlink/copy model
- [ ] Đã kiểm tra config.yml
- [ ] Đã bật GPU (nếu có)
- [ ] Đã kiểm tra custom components

## 📝 Notes

- Colab có giới hạn thời gian sử dụng (12 giờ cho free tier)
- Model sẽ bị xóa sau khi đóng Colab
- Nhớ download model về máy local sau khi train xong
- Có thể lưu model lên Google Drive để backup

## 🔗 Links Hữu Ích

- [Google Colab](https://colab.research.google.com/)
- [Rasa Documentation](https://rasa.com/docs/)
- [PhoBERT HuggingFace](https://huggingface.co/vinai/phobert-large)


