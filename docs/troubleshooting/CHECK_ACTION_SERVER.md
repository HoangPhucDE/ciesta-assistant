# 🔍 Kiểm tra Action Server

## Vấn đề

Lỗi: `Cannot connect to host localhost:5055 ssl:default [Connection refused]`

## Kiểm tra nhanh

### 1. Action server có đang chạy không?

```bash
ps aux | grep "rasa run actions" | grep -v grep
```

Nếu không thấy process, action server chưa chạy.

### 2. Port 5055 có đang được sử dụng không?

```bash
lsof -i :5055
# hoặc
netstat -tuln | grep 5055
```

Nếu không thấy, port 5055 chưa được sử dụng.

### 3. Action server có phản hồi không?

```bash
curl http://localhost:5055/webhook
```

Nếu thấy response (có thể là error), action server đang chạy.

## Giải pháp

### Nếu action server chưa chạy:

1. **Khởi động action server:**
   ```bash
   cd /ciesta-asisstant
   rasa run actions
   ```

2. **Đảm bảo action server chạy thành công:**
   Bạn sẽ thấy:
   ```
   INFO     rasa_sdk.endpoint  - Action endpoint is up and running on http://0.0.0.0:5055
   ```

3. **Giữ terminal này mở** (action server phải chạy liên tục)

### Nếu action server đang chạy nhưng vẫn lỗi:

1. **Kiểm tra endpoints.yml:**
   ```yaml
   action_endpoint:
     url: "http://localhost:5055/webhook"
   ```

2. **Kiểm tra firewall:**
   ```bash
   # Nếu dùng firewall, cho phép port 5055
   sudo ufw allow 5055
   ```

3. **Restart cả hai server:**
   ```bash
   # Terminal 1: Action server
   rasa run actions
   
   # Terminal 2: Rasa server
   rasa run --enable-api --cors "*"
   ```

## Debug

Nếu vẫn không được, kiểm tra logs của action server:

```bash
# Xem logs của action server
# (Trong terminal đang chạy action server)
```

Tìm các dòng:
- `[Actions] Loaded .env from ...`
- `[RAG] Could not initialize retriever: ...`
- `Action endpoint is up and running on ...`

## Lưu ý

- **Action server phải chạy trước Rasa server**
- **Action server phải chạy liên tục** (không được dừng)
- **Cả hai server phải chạy trên cùng một máy** (hoặc cấu hình network đúng)

