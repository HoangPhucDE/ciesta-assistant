# ⚡ Ngrok Quick Guide - Mở và lấy URL

## 🚀 3 Bước nhanh

### Bước 1: Cài đặt Ngrok (nếu chưa có)

```bash
# Kiểm tra ngrok đã cài chưa
which ngrok

# Nếu chưa có, cài đặt:
# Linux
sudo snap install ngrok

# Mac
brew install ngrok/ngrok/ngrok

# Windows: Download từ https://ngrok.com/download
```

### Bước 2: Đăng ký và lấy Auth Token

1. **Đăng ký miễn phí**: https://dashboard.ngrok.com/signup
2. **Lấy token**: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Cấu hình token**:
   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN
   ```

### Bước 3: Chạy Ngrok và lấy URL

#### Cách 1: Chạy trực tiếp (Đơn giản nhất)

```bash
# Chạy ngrok tunnel cho port 5005 (Rasa server)
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

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**Copy URL**: `https://abc123-xyz-456.ngrok-free.app`

#### Cách 2: Lấy URL từ Ngrok API (Tự động)

Ngrok cung cấp API tại `http://localhost:4040/api/tunnels` khi đang chạy.

**Từ terminal:**
```bash
# Lấy URL từ ngrok API
curl http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url'

# Hoặc không có jq:
curl http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*"' | head -1 | cut -d'"' -f4
```

**Từ browser:**
Mở: http://localhost:4040/api/tunnels

Bạn sẽ thấy JSON với URL:
```json
{
  "tunnels": [
    {
      "public_url": "https://abc123-xyz-456.ngrok-free.app",
      ...
    }
  ]
}
```

#### Cách 3: Dùng Auto-detect trong Frontend (Khuyến nghị)

1. Mở app Ciesta Desktop
2. Vào **Settings** (⚙️)
3. Chọn **Connection Type: Ngrok**
4. Click nút **"🔍 Auto-detect Ngrok"**
   - App sẽ tự động lấy URL từ ngrok API
   - URL sẽ tự động được điền

## 📋 Checklist

Trước khi chạy ngrok, đảm bảo:

- [ ] Ngrok đã được cài đặt (`which ngrok`)
- [ ] Đã đăng ký và add auth token (`ngrok config add-authtoken ...`)
- [ ] Rasa server đang chạy tại port 5005 (`rasa run --enable-api --cors "*"`)
- [ ] Action server đang chạy (`rasa run actions`)

## 🎯 Workflow hoàn chỉnh

### Terminal 1: Action Server
```bash
cd /ciesta-asisstant
rasa run actions
```

### Terminal 2: Rasa Server
```bash
cd /ciesta-asisstant
rasa run --enable-api --cors "*"
```

### Terminal 3: Ngrok
```bash
ngrok http 5005
```

**Copy URL** từ output hoặc dùng Auto-detect trong frontend.

## 🔍 Kiểm tra Ngrok đang chạy

```bash
# Kiểm tra process
ps aux | grep ngrok

# Kiểm tra port 4040 (ngrok web interface)
curl http://localhost:4040/api/tunnels

# Kiểm tra tunnel
curl http://localhost:4040/api/tunnels | jq '.tunnels[0].public_url'
```

## ⚠️ Lưu ý

1. **Giữ terminal ngrok mở** - Nếu đóng, tunnel sẽ dừng
2. **URL thay đổi mỗi lần restart** - Free plan URL thay đổi mỗi lần restart ngrok
3. **Dùng Auto-detect** - Tự động lấy URL mới khi restart
4. **Session timeout** - Free plan có timeout 2 giờ, sau đó cần restart

## 🐛 Troubleshooting

### Lỗi: "ngrok: command not found"
```bash
# Cài đặt ngrok
sudo snap install ngrok
# hoặc
brew install ngrok/ngrok/ngrok
```

### Lỗi: "authtoken is required"
```bash
# Thêm auth token
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### Lỗi: "bind: address already in use"
```bash
# Port 5005 đã được sử dụng
# Kiểm tra process nào đang dùng port 5005
lsof -i :5005

# Hoặc dùng port khác
ngrok http 5006
```

### Không thấy URL trong output
```bash
# Kiểm tra ngrok web interface
# Mở browser: http://localhost:4040
# Hoặc lấy từ API
curl http://localhost:4040/api/tunnels
```

## 📝 Ví dụ Output

Khi chạy `ngrok http 5005`, bạn sẽ thấy:

```
ngrok                                                                               

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.1.0
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123-xyz-456.ngrok-free.app -> http://localhost:5005

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

**URL cần copy**: `https://abc123-xyz-456.ngrok-free.app`

## ✅ Sau khi có URL

1. **Copy URL** từ ngrok terminal
2. **Hoặc dùng Auto-detect** trong frontend (khuyến nghị)
3. **Test connection** trong frontend
4. **Save settings**

Done! Frontend có thể kết nối đến backend qua ngrok.

