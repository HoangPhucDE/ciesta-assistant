#!/bin/bash
# Script để fix vấn đề PyTorch không nhận diện GPU
# Chạy script này nếu PyTorch không detect được GPU mặc dù đã có CUDA

echo "🔧 FIX PYTORCH CUDA - Cài đặt PyTorch với CUDA support"
echo "=================================================="
echo ""

# Kiểm tra nvidia-smi
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ Không tìm thấy nvidia-smi"
    echo "   → Cài đặt CUDA driver trước: https://developer.nvidia.com/cuda-downloads"
    exit 1
fi

echo "✅ Tìm thấy nvidia-smi"
nvidia-smi --query-gpu=name,driver_version,cuda_version --format=csv,noheader
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Không tìm thấy python3"
    exit 1
fi

echo "✅ Tìm thấy Python: $(python3 --version)"
echo ""

# Kiểm tra pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ Không tìm thấy pip3"
    exit 1
fi

echo "✅ Tìm thấy pip3"
echo ""

# Hỏi user chọn CUDA version
echo "Chọn CUDA version để cài đặt PyTorch:"
echo "1. CUDA 12.1 (khuyến nghị - tương thích với CUDA 13.0)"
echo "2. CUDA 12.4"
echo "3. CUDA 11.8"
read -p "Chọn (1/2/3, mặc định: 1): " choice
choice=${choice:-1}

case $choice in
    1)
        CUDA_VERSION="cu121"
        INDEX_URL="https://download.pytorch.org/whl/cu121"
        ;;
    2)
        CUDA_VERSION="cu124"
        INDEX_URL="https://download.pytorch.org/whl/cu124"
        ;;
    3)
        CUDA_VERSION="cu118"
        INDEX_URL="https://download.pytorch.org/whl/cu118"
        ;;
    *)
        echo "❌ Lựa chọn không hợp lệ"
        exit 1
        ;;
esac

echo ""
echo "📦 Đang gỡ PyTorch cũ..."
pip3 uninstall -y torch torchvision torchaudio

echo ""
echo "📦 Đang cài đặt PyTorch với CUDA $CUDA_VERSION..."
pip3 install torch torchvision torchaudio --index-url $INDEX_URL

echo ""
echo "🔍 Kiểm tra cài đặt..."
python3 -c "import torch; print('PyTorch version:', torch.__version__); print('CUDA available:', torch.cuda.is_available()); print('CUDA version:', torch.version.cuda if torch.cuda.is_available() else 'N/A'); print('GPU name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo ""
if python3 -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>/dev/null; then
    echo "✅ Thành công! GPU đã được PyTorch nhận diện"
    echo ""
    echo "🚀 Bây giờ bạn có thể train với GPU:"
    echo "   rasa train nlu"
else
    echo "❌ Vẫn chưa nhận diện được GPU"
    echo ""
    echo "💡 Thử các giải pháp sau:"
    echo "   1. Restart terminal/IDE"
    echo "   2. Kiểm tra CUDA toolkit đã được cài đặt:"
    echo "      nvcc --version"
    echo "   3. Kiểm tra PATH có chứa CUDA:"
    echo "      echo \$PATH | grep cuda"
    echo "   4. Cài đặt CUDA toolkit nếu chưa có:"
    echo "      https://developer.nvidia.com/cuda-downloads"
fi

