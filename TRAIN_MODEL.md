# Hướng dẫn Train lại Model

## Vấn đề đã sửa

1. ✅ Thêm nhiều examples cho `greet` intent (30+ examples)
2. ✅ Thêm nhiều examples cho `bot_challenge` intent (20+ examples)
3. ✅ Thêm nhiều examples cho `goodbye` intent (30+ examples)
4. ✅ Thêm nhiều examples cho `ask_cuisine` với format "ẩm thực [location]" (30+ examples cho tất cả 34 tỉnh)
5. ✅ Thêm logic fallback trong `ActionQueryKnowledgeBase` để detect intent từ message text nếu intent bị nhầm
6. ✅ Thêm logic fallback trong `ActionRAGFallback` để detect greet/goodbye/bot_challenge từ message text
7. ✅ Điều chỉnh `FallbackClassifier` threshold từ 0.55 xuống 0.50
8. ✅ Điều chỉnh `DIETClassifier` confidence_threshold từ 0.60 xuống 0.55

## Các bước train lại model

### Bước 1: Dừng action server (nếu đang chạy)
```bash
# Nhấn Ctrl+C trong terminal đang chạy action server
```

### Bước 2: Train lại model
```bash
# Train toàn bộ model (NLU + Core)
rasa train

# Hoặc chỉ train NLU
rasa train nlu

# Hoặc chỉ train Core
rasa train core
```

### Bước 3: Khởi động lại action server
```bash
rasa run actions
```

### Bước 4: Khởi động lại Rasa server
```bash
# Trong terminal khác
rasa run --enable-api --cors "*"
```

### Bước 5: Test lại
```bash
# Test với shell
rasa shell

# Hoặc test với API
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "ẩm thực Đà Nẵng"
  }'
```

## Lưu ý

- Training có thể mất 10-30 phút tùy vào cấu hình máy
- Đảm bảo có đủ RAM (khuyến nghị 8GB+)
- Nếu gặp lỗi Out of Memory, giảm `batch_size` trong `config.yml`

## Kiểm tra kết quả

Sau khi train xong, test các câu sau:
- "xin chào" / "Xin chào" / "xin chao" / "chào" → nên nhận diện là `greet` hoặc fallback sẽ xử lý
- "Bạn là ai" / "bạn là ai" → nên nhận diện là `bot_challenge` hoặc fallback sẽ xử lý
- "Tạm biệt" / "tạm biệt" / "bye" → nên nhận diện là `goodbye` hoặc fallback sẽ xử lý
- "ẩm thực Đà Nẵng" → nên nhận diện là `ask_cuisine` (không phải `ask_transportation`)
- "ẩm thực Hà Nội" → nên nhận diện là `ask_cuisine`
- "Ẩm thực Sài Gòn" → nên nhận diện là `ask_cuisine`

**Lưu ý:** Ngay cả khi model chưa được train lại, logic fallback trong actions sẽ tự động xử lý các trường hợp:
- Greet/goodbye/bot_challenge bị nhầm thành `nlu_fallback` hoặc `out_of_scope`
- `ask_cuisine` bị nhầm thành `ask_transportation`

