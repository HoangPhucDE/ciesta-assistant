# 🚀 Quick Fix: RAG Fallback không gọi được

## Vấn đề

Lỗi: `Cannot connect to host localhost:5055 ssl:default [Connection refused]`

## Nguyên nhân

Action server chưa được khởi động hoặc đã bị dừng.

## Giải pháp nhanh

### Bước 1: Khởi động Action Server

Mở terminal mới và chạy:

```bash
cd /ciesta-asisstant
rasa run actions
```

Bạn sẽ thấy output như:
```
2025-11-07 08:25:57 INFO     rasa_sdk.endpoint  - Starting action endpoint server...
2025-11-07 08:25:57 INFO     rasa_sdk.endpoint  - Action endpoint is up and running on http://0.0.0.0:5055
```

### Bước 2: Đảm bảo Action Server đang chạy

Kiểm tra:
```bash
curl http://localhost:5055/webhook
```

Nếu thấy response (có thể là error nhưng vẫn là response), nghĩa là action server đang chạy.

### Bước 3: Test lại với Rasa

Trong terminal khác, chạy Rasa server:
```bash
rasa run --enable-api --cors "*"
```

Hoặc nếu đang dùng shell:
```bash
rasa shell
```

### Bước 4: Test với message out_of_scope

Test với:
```
giá vàng hôm nay
thời tiết mai
kể chuyện cười
```

## Lưu ý

1. **Action server phải chạy trước Rasa server**
   - Terminal 1: `rasa run actions`
   - Terminal 2: `rasa run --enable-api` hoặc `rasa shell`

2. **Action server phải chạy trên port 5055**
   - Kiểm tra `endpoints.yml` có đúng URL không
   - Mặc định: `http://localhost:5055/webhook`

3. **Nếu vẫn lỗi, kiểm tra:**
   - Action server có đang chạy không: `ps aux | grep "rasa run actions"`
   - Port 5055 có đang được sử dụng không: `lsof -i :5055`
   - Firewall có chặn port 5055 không

## Debug

Nếu vẫn không được, chạy:

```bash
python debug_rag.py
```

Script này sẽ kiểm tra:
- API key có được load không
- RAG retriever có khởi tạo được không
- Synthesis có hoạt động không

