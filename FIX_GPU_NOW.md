# 🚨 FIX NGAY: PyTorch Không Nhận Diện GPU

## ❌ Vấn Đề Của Bạn

Bạn có:
- ✅ GPU: NVIDIA GeForce RTX 3050
- ✅ CUDA Driver: 13.0
- ❌ PyTorch: 2.1.2+cu121 (CUDA 12.1) - **KHÔNG nhận diện GPU**

## ✅ Giải Pháp Nhanh (5 phút)

### Bước 1: Gỡ PyTorch cũ
```bash
pip uninstall -y torch torchvision torchaudio
```

### Bước 2: Cài đặt PyTorch với CUDA 12.1
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Bước 3: Kiểm tra
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

**Kết quả mong đợi:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3050 ...
```

## 🔧 Hoặc Sử Dụng Script Tự Động

### Cách 1: Script Python (Khuyến nghị)
```bash
python scripts/training/fix_pytorch_cuda.py
```

### Cách 2: Script Bash
```bash
bash scripts/training/fix_pytorch_cuda.sh
```

## 🎯 Sau Khi Fix

Sau khi fix thành công, training sẽ sử dụng GPU:

```bash
# Training với GPU (nhanh hơn 10-50 lần)
rasa train nlu
```

**Thời gian training:**
- ❌ CPU: 1-2 giờ
- ✅ GPU: 15-30 phút ⚡

## ⚠️ Nếu Vẫn Không Được

### Kiểm tra CUDA Toolkit
```bash
nvcc --version
```

Nếu không có output, cần cài đặt CUDA Toolkit:
- Download: https://developer.nvidia.com/cuda-downloads
- Chọn CUDA 12.1 hoặc 12.4 (tương thích với driver 13.0)

### Kiểm tra PATH
```bash
echo $PATH | grep cuda
```

Nếu không có, thêm vào `~/.bashrc`:
```bash
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

### Restart Terminal/IDE
Sau khi cài đặt, restart terminal hoặc IDE để áp dụng thay đổi.

## 📝 Tóm Tắt

1. **Vấn đề:** PyTorch không nhận diện GPU mặc dù có CUDA driver
2. **Nguyên nhân:** PyTorch cần CUDA toolkit tương thích
3. **Giải pháp:** Cài đặt lại PyTorch với CUDA 12.1/12.4
4. **Kết quả:** GPU được nhận diện, training nhanh hơn 10-50 lần

## 🔗 Tài Liệu

- [FIX_GPU_ISSUE.md](scripts/training/FIX_GPU_ISSUE.md) - Hướng dẫn chi tiết
- [check_training_setup.py](scripts/training/check_training_setup.py) - Script kiểm tra

