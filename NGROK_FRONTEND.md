# 🚀 Mở Ngrok cho Frontend - Hướng dẫn nhanh

## ⚡ Setup trong 3 bước

### Bước 1: Cài đặt và cấu hình Ngrok

#### Cài đặt Ngrok

**Linux:**
```bash
sudo snap install ngrok
# hoặc
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

**Mac:**
```bash
brew install ngrok/ngrok/ngrok
```

**Windows:**
- Download từ: https://ngrok.com/download
- Giải nén và đặt vào PATH

#### Đăng ký và lấy Auth Token

1. Đăng ký miễn phí tại: https://dashboard.ngrok.com/signup
2. Vào: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy auth token
4. Chạy:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Bước 2: Chạy Backend và Ngrok

Mở **3 terminal** trên máy backend:

**Terminal 1: Action Server**
```bash
cd /ciesta-asisstant
rasa run actions
```

**Terminal 2: Rasa Server**
```bash
cd /ciesta-asisstant
rasa run --enable-api --cors "*"
```

**Terminal 3: Ngrok Tunnel**
```bash
ngrok http 5005
```

Bạn sẽ thấy output như:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-xyz-456.ngrok-free.app -> http://localhost:5005
```

**Copy URL**: `https://abc123-xyz-456.ngrok-free.app`

### Bước 3: Cấu hình Frontend

#### Cách 1: Auto-detect (Tự động - Khuyến nghị)

1. Mở app Ciesta Desktop
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Click nút **"🔍 Auto-detect Ngrok"**
   - App sẽ tự động lấy URL từ ngrok API (localhost:4040)
   - URL sẽ tự động được điền vào ô Server URL
5. Click **"✅ Test Connection"** để kiểm tra
6. Nếu thành công, click **"Save"**

#### Cách 2: Nhập thủ công

1. Mở app Ciesta Desktop
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Nhập URL từ ngrok vào ô **Server URL**:
   ```
   https://abc123-xyz-456.ngrok-free.app
   ```
5. Click **"✅ Test Connection"**
6. Nếu thành công, click **"Save"**

## ✅ Kiểm tra kết nối

### Test từ terminal
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "Xin chào"
  }'
```

### Test từ browser
Mở: `https://your-ngrok-url.ngrok-free.app/status`

Nếu thấy response, nghĩa là ngrok đang hoạt động!

## 🔄 Khi URL thay đổi

**Free plan:** URL thay đổi mỗi lần restart ngrok.

**Giải pháp:**
1. **Dùng Auto-detect** (khuyến nghị)
   - Click "🔍 Auto-detect Ngrok" lại
   - URL mới sẽ tự động được lấy

2. **Hoặc copy URL mới** từ ngrok terminal
   - Copy URL mới từ terminal ngrok
   - Paste vào Settings > Server URL
   - Test và Save

## ⚠️ Lưu ý quan trọng

### Free Plan Limitations
- ✅ **URL thay đổi** mỗi lần restart ngrok
- ✅ **Session timeout**: 2 giờ (sau đó cần restart)
- ✅ **Bandwidth limit**: 1GB/month
- ✅ **Warning page**: Ngrok hiển thị warning page lần đầu (code đã xử lý)

### Bảo mật
- ⚠️ **URL công khai**: Ai biết URL đều có thể truy cập
- ⚠️ **Không có authentication mặc định**
- ⚠️ **Không dùng cho production** (chỉ test/demo)

### Best Practices
1. **Giữ ngrok terminal mở** - Nếu đóng, tunnel sẽ dừng
2. **Dùng Auto-detect** - Tự động lấy URL mới khi restart
3. **Monitor usage** - Kiểm tra bandwidth trong ngrok dashboard
4. **Rotate URLs** - Đổi URL định kỳ nếu cần bảo mật

## 🐛 Troubleshooting

### Lỗi: "Cannot connect to ngrok"
- ✅ Kiểm tra ngrok có đang chạy không: `ps aux | grep ngrok`
- ✅ Kiểm tra Rasa có đang chạy tại port 5005 không: `lsof -i :5005`
- ✅ Kiểm tra firewall có chặn không

### Lỗi: "ngrok API not accessible"
- ✅ Ngrok API chạy tại `localhost:4040`
- ✅ Nếu ngrok chạy trên máy khác, cần chỉnh `ngrok_api_url` trong code
- ✅ Kiểm tra ngrok có đang chạy không

### Lỗi: "Warning page"
- ✅ Code đã tự động thêm header `ngrok-skip-browser-warning: true`
- ✅ Nếu vẫn gặp, có thể cần click "Visit Site" lần đầu

### URL thay đổi liên tục
- ✅ Free plan: URL thay đổi mỗi lần restart ngrok
- ✅ Giải pháp: Dùng Auto-detect hoặc upgrade lên paid plan

## 📋 Checklist

- [ ] Đã cài ngrok
- [ ] Đã đăng ký và add auth token
- [ ] Action server đang chạy (`rasa run actions`)
- [ ] Rasa server đang chạy (`rasa run --enable-api --cors "*"`)
- [ ] Ngrok tunnel đang chạy (`ngrok http 5005`)
- [ ] Đã copy/auto-detect ngrok URL
- [ ] Đã test connection thành công
- [ ] Đã lưu settings trong frontend

## 🎯 Workflow thường dùng

### Development/Testing
1. Start Action Server: `rasa run actions`
2. Start Rasa Server: `rasa run --enable-api --cors "*"`
3. Start ngrok: `ngrok http 5005`
4. Mở app Ciesta → Settings → Auto-detect Ngrok
5. Test và develop

### Demo/Share
1. Start tất cả services (action server, rasa server, ngrok)
2. Share ngrok URL cho người khác
3. Họ có thể kết nối từ bất kỳ đâu (có internet)

## 🔗 Tài liệu tham khảo

- **Ngrok Docs**: https://ngrok.com/docs
- **Ngrok Dashboard**: https://dashboard.ngrok.com
- **Ngrok API**: http://localhost:4040/api/tunnels (khi ngrok đang chạy)
- **Chi tiết đầy đủ**: [docs/NGROK_SETUP.md](docs/NGROK_SETUP.md)

