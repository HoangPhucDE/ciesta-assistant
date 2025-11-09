# ⚡ Copy-Paste Nhanh cho Colab

## 🎮 BẬT GPU TRƯỚC KHI CHẠY (QUAN TRỌNG!)

**⚠️ Để training nhanh hơn, bạn CẦN bật GPU trên Colab:**

1. Vào menu: **Runtime → Change runtime type**
2. Trong phần **Hardware accelerator**, chọn **GPU**
3. Chọn GPU type: **T4** (miễn phí) hoặc **A100/V100** (trả phí, nhanh hơn)
4. Click **Save**
5. Colab sẽ restart runtime
6. Chạy script từ đầu

**💡 Lưu ý:**
- Không bật GPU: Training sẽ chạy trên CPU (chậm hơn 10-20 lần)
- Bật GPU: Training nhanh hơn đáng kể (30 phút - 2 giờ thay vì 5-10 giờ)
- Colab free tier có giới hạn GPU usage (khoảng 12 giờ/ngày)
- Script sẽ tự động kiểm tra GPU và cảnh báo nếu không có
- **Script tự động tối ưu batch size dựa trên GPU memory:**
  - T4/V100/A100 (15GB+): batch_size = 128-256 (tận dụng tối đa GPU)
  - GPU trung bình (8-15GB): batch_size = 64-128
  - GPU nhỏ (4-8GB): batch_size = 32-64

## 🚀 Cách 1: Copy từ file Python (KHUYẾN NGHỊ - TRÁNH LỖI)
1. Mở file `colab_setup_train.py` trong thư mục này
2. Copy toàn bộ nội dung (Ctrl+A, Ctrl+C)
3. Paste vào 1 cell Python trên Colab
4. Chạy cell

**Ưu điểm**: Không có markdown syntax, không có ký tự đặc biệt, copy trực tiếp không lỗi!

## 🚀 Cách 2: Copy từ block code bên dưới
**⚠️ QUAN TRỌNG: Chỉ copy code trong block Python bên dưới, KHÔNG copy dấu ``` (backticks) và phần Markdown!**

```python
# ============================================
# SETUP VÀ TRAIN - COLAB
# ============================================

import os
from pathlib import Path
import re

# Bước 1: Cleanup và Clone
if Path("ciesta-assistant").exists():
    !rm -rf ciesta-assistant

!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
%cd ciesta-assistant
print(f"✅ Thư mục: {os.getcwd()}")

# Bước 2: Cài đặt Python 3.10 (QUAN TRỌNG!)
print("\n🐍 Cài đặt Python 3.10...")
!apt-get update -qq
!apt-get install -y -qq python3.10 python3.10-venv python3.10-dev

# Bước 3: Tạo virtual environment
print("\n📦 Tạo virtual environment...")
!python3.10 -m venv venv_py310

# Bước 4: Cài đặt dependencies
print("\n📦 Cài đặt dependencies...")
!venv_py310/bin/pip install --upgrade pip
!venv_py310/bin/pip install -r requirements.txt

# Bước 5: Cập nhật config để dùng model online
print("\n⚙️ Cập nhật config...")
with open("config.yml", "r") as f:
    config = f.read()

config = re.sub(r'model_name:\s*"models/phobert-large"', 'model_name: "vinai/phobert-large"', config)
config = re.sub(r'cache_dir:\s*null', 'cache_dir: "models_hub/phobert_cache"', config)

with open("config.yml", "w") as f:
    f.write(config)
print("✅ Đã cập nhật config để dùng model online")

# Bước 6: Train NLU
print("\n🚀 Bắt đầu training...")
print("💡 Quá trình này có thể mất 30 phút - 2 giờ")
!venv_py310/bin/python -m rasa train nlu

# Bước 7: Download model
print("\n📥 Tải model về máy...")
from google.colab import files
from pathlib import Path

models = list(Path("models").glob("*.tar.gz"))
if models:
    latest = max(models, key=lambda x: x.stat().st_mtime)
    size_mb = latest.stat().st_size / (1024*1024)
    print(f"📦 Model: {latest.name} ({size_mb:.2f} MB)")
    files.download(str(latest))
    print("✅ Đã bắt đầu tải model về máy")
else:
    print("❌ Không tìm thấy model")

print("\n🎉 Hoàn tất!")
```

## 📝 Giải Thích

1. **Cleanup**: Xóa thư mục cũ nếu có (tránh nested directory)
2. **Clone**: Clone repository từ GitHub
3. **Python 3.10**: Cài đặt Python 3.10 (Rasa 3.6.20 cần Python 3.8-3.10)
4. **Virtual Environment**: Tạo venv với Python 3.10
5. **Dependencies**: Cài đặt tất cả packages
6. **Config**: Cập nhật để dùng model online (không cần download trước)
7. **Train**: Train NLU model
8. **Download**: Tải model đã train về máy

## ⚠️ Lưu Ý

- **Python 3.10**: Bắt buộc phải dùng Python 3.10
- **Model online**: Config đã được cập nhật để dùng model từ HuggingFace
- **GPU**: Bật GPU để train nhanh hơn (Runtime -> Change runtime type -> GPU)
- **Thời gian**: Training mất 30 phút - 2 giờ tùy vào GPU

## 🔧 Troubleshooting

### ⚠️ Vấn đề: KeyboardInterrupt / Dependencies chưa được cài đặt
**Nguyên nhân**: Script bị interrupt (nhấn Stop) trong quá trình cài đặt dependencies.

**Triệu chứng**:
- Lỗi: `KeyboardInterrupt` khi cài đặt packages
- Lỗi: `No module named rasa` hoặc `No module named torch`
- Script tiếp tục chạy dù dependencies chưa cài xong
- GPU check không thể detect GPU memory (vì PyTorch chưa cài)

**Giải pháp**:
1. **QUAN TRỌNG: KHÔNG interrupt quá trình cài đặt!**
   - Cài đặt dependencies có thể mất **10-20 phút**
   - **Để script chạy đến khi hoàn tất** - không nhấn Stop/Cancel
   - Có thể thấy nhiều warnings nhưng đó là bình thường
   - Script sẽ hiển thị: `⚠️ QUAN TRỌNG: Quá trình này có thể mất 10-20 phút, KHÔNG interrupt!`

2. **Nếu đã bị interrupt:**
   - Chạy lại script từ đầu
   - Đảm bảo đợi đến khi thấy: `✅ Tất cả packages quan trọng đã được cài đặt`
   - Sau đó script mới tiếp tục với GPU check và training

3. **Kiểm tra dependencies đã cài xong:**
   ```python
   !venv_py310/bin/python -c "import rasa; import torch; print('✅ Dependencies OK')"
   ```

4. **Script tự động kiểm tra:**
   - Script sẽ kiểm tra `rasa`, `torch`, `transformers` sau khi cài đặt
   - Nếu thiếu packages, script sẽ dừng lại và yêu cầu chạy lại
   - Script sẽ không tiếp tục training nếu Rasa chưa được cài đặt

### Lỗi: SyntaxError: invalid character hoặc invalid syntax
**Nguyên nhân**: Đã copy cả markdown syntax (```) hoặc ký tự đặc biệt vào cell Python.

**Giải pháp**: 
- **Sử dụng file `colab_setup_train.py`** (Cách 1) - đảm bảo không có lỗi
- Hoặc chỉ copy phần code giữa 2 dấu ```, KHÔNG copy dấu ``` vào cell Python

### Lỗi: ERROR: Cannot install regex - conflicting dependencies
**Nguyên nhân**: `regex==2024.5.15` không tương thích với `rasa 3.6.20` (rasa yêu cầu `regex<2022.11`).

**Giải pháp**: 
- File `requirements.txt` đã được cập nhật với `regex==2022.9.13` (tương thích với rasa 3.6.20)
- Pull code mới nhất từ repo hoặc cập nhật requirements.txt thủ công:
  ```bash
  regex==2022.9.13
  ```

### Lỗi: FileNotFoundError: config.yml
**Nguyên nhân**: File config không ở root, mà nằm trong `config/rasa/config.yml`.

**Giải pháp**: 
- Script đã được cập nhật để tự động tìm và tạo symlink từ `config/rasa/config.yml` -> `config.yml`
- Đảm bảo bạn đang dùng phiên bản mới nhất của script

### Vấn đề: Không tìm thấy GPU / Training chạy trên CPU
**Nguyên nhân**: Chưa bật GPU runtime trên Colab.

**Triệu chứng**: 
- Thông báo: `[PhoBERTFeaturizer] ⚠️ No GPU detected - Using CPU`
- Training chạy rất chậm (5-10 giờ thay vì 30 phút - 2 giờ)

**Giải pháp**:
1. **Bật GPU runtime:**
   - Vào menu: **Runtime → Change runtime type**
   - Chọn **Hardware accelerator**: **GPU**
   - Chọn GPU type: **T4** (miễn phí) hoặc **A100/V100** (trả phí)
   - Click **Save**
   - Colab sẽ restart runtime

2. **Chạy lại script từ đầu** (sau khi bật GPU)

3. **Kiểm tra GPU:**
   - Script sẽ tự động kiểm tra GPU sau khi cài dependencies
   - Nếu thấy `✅ GPU được phát hiện` và `✅ PyTorch phát hiện GPU` → OK
   - Nếu thấy `❌ Không tìm thấy GPU` → Cần bật GPU runtime

4. **Lưu ý:**
   - Colab free tier có thể không có GPU available vào một số thời điểm
   - Có thể cần đợi vài phút hoặc thử lại sau
   - Training vẫn chạy được trên CPU, nhưng chậm hơn nhiều

### Vấn đề: GPU không sử dụng hết tài nguyên (GPU RAM thấp)
**Nguyên nhân**: Batch size quá nhỏ, không tận dụng hết GPU memory.

**Triệu chứng**: 
- GPU RAM chỉ sử dụng 10-20% (ví dụ: 1-2GB / 15GB)
- Training chậm hơn so với khả năng GPU (ước tính >20 giờ)
- GPU utilization thấp
- Training time ước tính quá lâu (>20 giờ)

**Giải pháp**:
1. **Script tự động tối ưu (phiên bản mới):**
   - Script sẽ tự động detect GPU memory và tăng batch size
   - T4 (14.7-15GB): batch_size tăng lên 256 (PhoBERT), [256, 512] (DIET)
   - Script sẽ tự động áp dụng khi có GPU >= 14.5GB
   - **Lưu ý**: Nếu training đang chạy, phải dừng và chạy lại script để áp dụng batch size mới

2. **Kiểm tra batch size trong config.yml:**
   ```yaml
   # PhoBERTFeaturizer
   batch_size: 256  # Nên là 128-256 cho T4 GPU (15GB)

   # DIETClassifier
   batch_size: [256, 512]  # Nên là [256, 512] cho T4 GPU để training nhanh hơn
   ```

3. **Nếu training đang chạy với GPU usage thấp (<20%):**
   - **Option 1 (Khuyến nghị)**: Dừng training và chạy lại script từ đầu
     - Script mới sẽ tự động detect T4 (14.7GB) và set batch_size = 256, [256, 512]
     - Training sẽ nhanh hơn đáng kể (từ 27+ giờ xuống ~5-10 giờ)
   - **Option 2**: Chạy script tối ưu riêng (nếu có):
     ```python
     # Chạy script tối ưu để cập nhật batch size
     # Sau đó dừng training và chạy lại: !rasa train nlu --config config.yml
     ```

4. **Batch size tối ưu cho T4 GPU (15GB):**
   - **PhoBERTFeaturizer**: `batch_size: 256` (có thể thử 512 nếu không OOM)
   - **DIETClassifier**: `batch_size: [256, 512]` (có thể thử [512, 1024] nếu không OOM)
   - **Lưu ý**: Nếu gặp Out of Memory (OOM), giảm batch size xuống một nửa

5. **Lưu ý quan trọng:**
   - Batch size lớn hơn = training nhanh hơn, sử dụng GPU tốt hơn (50-80% GPU RAM)
   - Nhưng quá lớn có thể gây Out of Memory (OOM)
   - **PHẢI restart training** sau khi thay đổi batch size (không thể thay đổi giữa chừng)
   - Training time ước tính:
     - Batch size nhỏ (32, [16,32]): 20-30 giờ
     - Batch size trung bình (128, [128,256]): 10-15 giờ
     - Batch size lớn (256, [256,512]): 5-8 giờ

### Lỗi: Nested directory
```python
# Xóa và clone lại
!rm -rf ciesta-assistant
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
```

### Lỗi: Python version
```python
# Kiểm tra Python version
import sys
print(sys.version)

# Phải là Python 3.10 trong venv
!venv_py310/bin/python --version
```

### Lỗi: Rasa không cài được
```python
# Cài đặt lại trong venv
!venv_py310/bin/pip install rasa==3.6.20 rasa-sdk==3.6.2
```

