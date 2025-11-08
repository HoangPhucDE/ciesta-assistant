# 🔗 Hướng dẫn Setup với Ngrok

## 📋 Tổng quan

Ngrok cho phép expose Rasa backend (localhost:5005) ra internet, giúp frontend trên máy khác có thể kết nối.

## 🚀 Bước 1: Cài đặt Ngrok

### Linux/Mac
```bash
# Download và cài đặt
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# Hoặc dùng snap
sudo snap install ngrok
```

### Windows
1. Download từ: https://ngrok.com/download
2. Giải nén và đặt vào PATH

### Hoặc dùng package manager
```bash
# Homebrew (Mac)
brew install ngrok/ngrok/ngrok

# Scoop (Windows)
scoop install ngrok
```

## 🔑 Bước 2: Đăng ký và lấy Auth Token (Miễn phí)

1. Đăng ký tại: https://dashboard.ngrok.com/signup
2. Vào: https://dashboard.ngrok.com/get-started/your-authtoken
3. Copy auth token
4. Chạy lệnh:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

## 🎯 Bước 3: Chạy Rasa Backend

Trên máy backend, chạy Rasa server:

```bash
# Terminal 1: Action server
rasa run actions

# Terminal 2: Rasa server
rasa run --enable-api --cors "*" --port 5005 --debug
```

Rasa sẽ chạy tại: `http://localhost:5005`

## 🌐 Bước 4: Chạy Ngrok Tunnel

Trên máy backend, mở terminal mới và chạy:

```bash
ngrok http 5005
```

Bạn sẽ thấy output như:
```
Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-xyz-456.ngrok-free.app -> http://localhost:5005

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copy URL**: `https://abc123-xyz-456.ngrok-free.app`

## 💻 Bước 5: Cấu hình Frontend

### Cách 1: Dùng Auto-detect (Tự động)

1. Mở app Ciesta
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Click nút **"🔍 Auto-detect Ngrok"**
5. URL sẽ tự động được điền
6. Click **"✅ Test Connection"** để kiểm tra
7. Click **"Save"**

### Cách 2: Nhập thủ công

1. Mở app Ciesta
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Nhập URL từ ngrok vào ô **Server URL**:
   ```
   https://abc123-xyz-456.ngrok-free.app
   ```
5. Click **"✅ Test Connection"**
6. Click **"Save"**

## 🔧 Cấu hình nâng cao

### Ngrok với domain tĩnh (Paid)

Nếu có ngrok paid plan, có thể dùng domain tĩnh:

```bash
ngrok http 5005 --domain=your-domain.ngrok.app
```

### Ngrok với custom subdomain (Paid)

```bash
ngrok http 5005 --subdomain=ciesta-bot
# URL sẽ là: https://ciesta-bot.ngrok-free.app
```

### Ngrok với authentication (Bảo mật)

```bash
# Yêu cầu username/password
ngrok http 5005 --basic-auth="username:password"
```

### Ngrok với IP whitelist

Trong ngrok dashboard, có thể set IP whitelist để chỉ cho phép IP cụ thể truy cập.

## 📱 Kiểm tra kết nối

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

## ⚠️ Lưu ý quan trọng

### Free Plan Limitations
- **URL thay đổi mỗi lần restart** ngrok
- **Session timeout**: 2 giờ (sau đó cần restart)
- **Bandwidth limit**: 1GB/month
- **Warning page**: Ngrok hiển thị warning page lần đầu (code đã xử lý)

### Bảo mật
- **URL công khai**: Ai biết URL đều có thể truy cập
- **Không có authentication mặc định**
- **Không dùng cho production** (chỉ test/demo)

### Best Practices
1. **Restart ngrok khi cần URL mới**: URL free plan thay đổi mỗi lần restart
2. **Dùng Auto-detect**: Frontend có nút tự động lấy URL từ ngrok API
3. **Monitor usage**: Kiểm tra bandwidth trong ngrok dashboard
4. **Rotate URLs**: Đổi URL định kỳ nếu cần bảo mật

## 🐛 Troubleshooting

### Lỗi: "Cannot connect to ngrok"
- Kiểm tra ngrok có đang chạy không
- Kiểm tra Rasa có đang chạy tại port 5005 không
- Kiểm tra firewall có chặn không

### Lỗi: "ngrok API not accessible"
- Ngrok API chạy tại `localhost:4040`
- Nếu ngrok chạy trên máy khác, cần chỉnh `ngrok_api_url` trong code

### Lỗi: "Warning page"
- Code đã tự động thêm header `ngrok-skip-browser-warning: true`
- Nếu vẫn gặp, có thể cần click "Visit Site" lần đầu

### URL thay đổi liên tục
- Free plan: URL thay đổi mỗi lần restart ngrok
- Giải pháp: Dùng Auto-detect hoặc upgrade lên paid plan

## 🔄 Workflow thường dùng

### Development/Testing
1. Start Rasa: `rasa run --enable-api --cors "*"`
2. Start ngrok: `ngrok http 5005`
3. Copy URL hoặc dùng Auto-detect trong frontend
4. Test và develop

### Demo/Share
1. Start Rasa và ngrok
2. Share ngrok URL cho người khác
3. Họ có thể kết nối từ bất kỳ đâu (có internet)

## 📊 So sánh với các giải pháp khác

| Giải pháp | Setup | Bảo mật | Ổn định | Chi phí |
|-----------|-------|---------|---------|---------|
| **Ngrok** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Free/Paid |
| **Cloudflare Tunnel** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **Tailscale** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **SSH Tunnel** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **LAN IP** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |

## 🎯 Khuyến nghị

- **Test nhanh**: Ngrok (dễ setup)
- **Production**: Cloudflare Tunnel hoặc Tailscale (bảo mật hơn)
- **Cùng mạng LAN**: Dùng LAN IP trực tiếp (không cần ngrok)

## 📝 Checklist

- [ ] Đã cài ngrok
- [ ] Đã đăng ký và add auth token
- [ ] Rasa đang chạy tại localhost:5005
- [ ] Ngrok tunnel đang chạy
- [ ] Đã copy/auto-detect ngrok URL
- [ ] Đã test connection thành công
- [ ] Đã lưu settings trong frontend

## 🔗 Tài liệu tham khảo

- Ngrok Docs: https://ngrok.com/docs
- Ngrok Dashboard: https://dashboard.ngrok.com
- Ngrok API: http://localhost:4040/api/tunnels (khi ngrok đang chạy)

