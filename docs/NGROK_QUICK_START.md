# ⚡ Ngrok Quick Start

## 🎯 Setup nhanh trong 5 phút

### Bước 1: Cài ngrok
```bash
# Linux/Mac
sudo snap install ngrok
# hoặc
brew install ngrok/ngrok/ngrok

# Windows: Download từ https://ngrok.com/download
```

### Bước 2: Đăng ký & lấy token
1. Đăng ký: https://dashboard.ngrok.com/signup
2. Lấy token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Chạy: `ngrok config add-authtoken YOUR_TOKEN`

### Bước 3: Chạy Rasa + Ngrok

**Máy Backend:**
```bash
# Terminal 1: Action server
rasa run actions

# Terminal 2: Rasa server  
rasa run --enable-api --cors "*"

# Terminal 3: Ngrok
ngrok http 5005
```

Copy URL từ ngrok (ví dụ: `https://abc123.ngrok-free.app`)

### Bước 4: Cấu hình Frontend

**Máy Frontend:**
1. Mở app Ciesta
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Click **"🔍 Auto-detect Ngrok"** (tự động lấy URL)
   - Hoặc nhập URL thủ công: `https://abc123.ngrok-free.app`
5. Click **"✅ Test Connection"**
6. Click **"Save"**

## ✅ Done!

Bây giờ frontend có thể kết nối đến backend qua ngrok.

## 🔄 Khi URL thay đổi

Free plan: URL thay đổi mỗi lần restart ngrok.

**Giải pháp:**
- Dùng **Auto-detect** (tự động lấy URL mới)
- Hoặc copy URL mới từ ngrok terminal

## 📖 Xem thêm

Chi tiết đầy đủ: [NGROK_SETUP.md](NGROK_SETUP.md)

