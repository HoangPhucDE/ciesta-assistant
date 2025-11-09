# 🔧 Fix Vấn Đề PyTorch Không Nhận Diện GPU

## ❌ Vấn Đề

Bạn có GPU (NVIDIA GeForce RTX 3050) và CUDA 13.0, nhưng PyTorch không nhận diện được GPU.

**Triệu chứng:**
```bash
$ python -c "import torch; print(torch.cuda.is_available())"
False
```

**Nguyên nhân:**
- PyTorch được compile với CUDA 12.1 (`2.1.2+cu121`)
- Hệ thống có CUDA 13.0
- PyTorch không tương thích với CUDA version cao hơn

## ✅ Giải Pháp

### Cách 1: Sử dụng Script Tự Động (Khuyến nghị)

```bash
bash scripts/training/fix_pytorch_cuda.sh
```

Script sẽ:
1. Kiểm tra nvidia-smi
2. Gỡ PyTorch cũ
3. Cài đặt PyTorch với CUDA 12.1 (tương thích với CUDA 13.0)
4. Kiểm tra lại

### Cách 2: Cài Đặt Thủ Công

#### Bước 1: Gỡ PyTorch cũ
```bash
pip uninstall torch torchvision torchaudio
```

#### Bước 2: Cài đặt PyTorch với CUDA 12.1
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

#### Bước 3: Kiểm tra
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

Kết quả mong đợi:
```
CUDA available: True
GPU: NVIDIA GeForce RTX 3050 ...
```

### Cách 3: Cài Đặt với CUDA 12.4 (Nếu CUDA 12.1 không hoạt động)

```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

## 🔍 Kiểm Tra Sau Khi Cài Đặt

### 1. Kiểm tra PyTorch
```bash
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA available:', torch.cuda.is_available())"
```

### 2. Kiểm tra GPU
```bash
python -c "import torch; print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

### 3. Chạy script kiểm tra đầy đủ
```bash
python scripts/training/check_training_setup.py
```

## 🚀 Sau Khi Fix

Sau khi fix thành công, training sẽ sử dụng GPU và nhanh hơn nhiều:

```bash
# Training với GPU (nhanh hơn 10-50 lần)
rasa train nlu
```

**Thời gian training:**
- CPU: 1-2 giờ
- GPU: 15-30 phút ⚡

## ⚠️ Lưu Ý

1. **CUDA Toolkit vs CUDA Driver:**
   - CUDA Driver (từ nvidia-smi): Version driver GPU
   - CUDA Toolkit: Version để compile code
   - PyTorch cần CUDA Toolkit tương thích với CUDA Driver

2. **Tương thích:**
   - CUDA 13.0 Driver → PyTorch CUDA 12.1/12.4 (tương thích ngược)
   - CUDA 12.x Driver → PyTorch CUDA 12.1/12.4
   - CUDA 11.x Driver → PyTorch CUDA 11.8

3. **Nếu vẫn không được:**
   - Restart terminal/IDE
   - Kiểm tra CUDA toolkit: `nvcc --version`
   - Kiểm tra PATH: `echo $PATH | grep cuda`
   - Cài đặt CUDA toolkit: https://developer.nvidia.com/cuda-downloads

## 📝 Troubleshooting

### Lỗi: "No module named torch"
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Lỗi: "CUDA out of memory"
- Giảm batch_size trong config.yml
- Sử dụng config_local.yml

### Lỗi: "Cannot find CUDA"
- Kiểm tra CUDA toolkit đã được cài đặt
- Kiểm tra PATH có chứa CUDA
- Restart terminal

## 🔗 Tài Liệu Tham Khảo

- PyTorch Installation: https://pytorch.org/get-started/locally/
- CUDA Toolkit: https://developer.nvidia.com/cuda-downloads
- NVIDIA Drivers: https://www.nvidia.com/Download/index.aspx

