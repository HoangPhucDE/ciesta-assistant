#!/bin/bash
# Script cài đặt ngrok nhanh

set -e

echo "🔧 Cài đặt Ngrok..."
echo ""

# Kiểm tra OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Detected: Linux"
    
    # Kiểm tra snap
    if command -v snap &> /dev/null; then
        echo "✅ Installing via snap..."
        sudo snap install ngrok
    elif command -v apt &> /dev/null; then
        echo "✅ Installing via apt..."
        curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
        echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
        sudo apt update && sudo apt install ngrok
    else
        echo "❌ Không tìm thấy package manager phù hợp"
        echo "💡 Vui lòng cài đặt thủ công: https://ngrok.com/download"
        exit 1
    fi
    
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 Detected: macOS"
    
    if command -v brew &> /dev/null; then
        echo "✅ Installing via Homebrew..."
        brew install ngrok/ngrok/ngrok
    else
        echo "❌ Homebrew chưa được cài đặt"
        echo "💡 Cài Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "💡 Hoặc download từ: https://ngrok.com/download"
        exit 1
    fi
    
else
    echo "❌ OS không được hỗ trợ tự động"
    echo "💡 Vui lòng cài đặt thủ công: https://ngrok.com/download"
    exit 1
fi

echo ""
echo "✅ Ngrok đã được cài đặt!"
echo ""
echo "🔑 Bước tiếp theo:"
echo "1. Đăng ký tại: https://dashboard.ngrok.com/signup"
echo "2. Lấy auth token tại: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "3. Chạy: ngrok config add-authtoken YOUR_AUTH_TOKEN"
echo ""
echo "🚀 Sau đó chạy: ngrok http 5005"

