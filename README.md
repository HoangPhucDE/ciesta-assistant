# 🌏 Ciesta - Bot Du lịch Việt Nam

Bot chatbot thông minh giới thiệu văn hóa và du lịch **34 tỉnh thành Việt Nam** theo Nghị quyết sắp xếp đơn vị hành chính cấp tỉnh (12/6/2025).

## 🚀 Tính năng

- ✅ **Giới thiệu văn hóa** 34 tỉnh thành sau sáp nhập
- ✅ **Gợi ý địa điểm** tham quan, check-in
- ✅ **Ẩm thực đặc sản** và quà lưu niệm
- ✅ **Lễ hội truyền thống** và sự kiện văn hóa
- ✅ **Mẹo du lịch** và thông tin di chuyển
- ✅ Sử dụng **PhoBERT Large** cho tiếng Việt
- ✅ Hỗ trợ nhiều cách gọi tên địa điểm

## 📋 Yêu cầu hệ thống

- Python 3.8+
- RAM: Tối thiểu 8GB (khuyến nghị 16GB cho PhoBERT Large)
- Disk: ~5GB cho model và dependencies

## 🛠️ Cài đặt

### Bước 1: Clone repository

```bash
git clone <your-repo-url>
cd ciesta-assistant
```

### Bước 2: Tạo virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc
.venv\Scripts\activate  # Windows
```

### Bước 3: Cài đặt dependencies

```bash
pip install rasa==3.6.0
pip install transformers torch
pip install rasa-sdk
```

### Bước 4: Cấu trúc thư mục

```
ciesta-assistant/
├── config.yml                    # Cấu hình pipeline (PhoBERT)
├── domain.yml                    # Domain với intents, entities, actions
├── endpoints.yml                 # Cấu hình endpoints
├── credentials.yml               # Cấu hình channels
├── actions.py                    # Custom actions
├── validate_knowledge_base.py    # Script kiểm tra KB
├── data/
│   ├── nlu.yml                  # Training data cho NLU
│   ├── rules.yml                # Rules cho bot
│   ├── stories.yml              # Stories cho training
│   └── knowledge_base/          # 34 file JSON
│       ├── ha_noi.json
│       ├── bac_ninh.json
│       ├── an_giang.json
│       └── ... (31 files khác)
└── models/                      # Models sau khi train
```

## 📦 Chuẩn bị dữ liệu

### Kiểm tra knowledge base

```bash
python validate_knowledge_base.py
```

### Tạo file template cho tỉnh thiếu

```bash
python validate_knowledge_base.py --create-missing
```

Sau đó điền thông tin vào các file JSON được tạo.

## 🎯 Training

### Train model

```bash
rasa train
```

**Lưu ý:** Lần train đầu tiên sẽ tải PhoBERT Large (~1.3GB), có thể mất 10-30 phút.

### Train chỉ NLU

```bash
rasa train nlu
```

### Train chỉ Core

```bash
rasa train core
```

## 🚀 Chạy bot

### Chạy trong shell (test)

```bash
# Terminal 1: Start action server
rasa run actions

# Terminal 2: Start shell
rasa shell
```

### Chạy với REST API

```bash
# Terminal 1: Action server
rasa run actions

# Terminal 2: Rasa server
rasa run --enable-api --cors "*"
```

API sẽ chạy tại: `http://localhost:5005`

### Test API

```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "Giới thiệu về Bắc Ninh"
  }'
```

## 💬 Ví dụ sử dụng

### Hỏi về văn hóa
```
User: Giới thiệu về Bắc Ninh
Bot: [Thông tin văn hóa Bắc Ninh sau sáp nhập Bắc Giang]
```

### Hỏi về địa điểm
```
User: Đà Nẵng có địa điểm nào đẹp?
Bot: [Danh sách địa điểm tham quan]
```

### Hỏi về ẩm thực
```
User: Ăn gì ở Hội An?
Bot: [Món ăn đặc sản Đà Nẵng - bao gồm cả Hội An]
```

### Hỏi về lễ hội
```
User: Bắc Ninh có lễ hội gì?
Bot: [Hội Lim, lễ hội Quan họ...]
```

### Hỏi về tỉnh sau sáp nhập
```
User: Bắc Giang giờ thuộc tỉnh nào?
Bot: [Thông tin về sáp nhập vào Bắc Ninh]
```

## 🔧 Cấu hình

### Thay đổi model

Trong `config.yml`, có thể đổi sang PhoBERT Base để giảm RAM:

```yaml
- name: LanguageModelFeaturizer
  model_name: "vinai/phobert-base"  # Thay vì phobert-large
  model_weights: "vinai/phobert-base"
```

### Giảm batch size nếu thiếu RAM

```yaml
- name: DIETClassifier
  epochs: 100
  batch_size: [32, 64]  # Giảm từ [64, 256]
```

### Thêm channels

Trong `credentials.yml`:

```yaml
# Facebook Messenger
facebook:
  verify: "your-verify-token"
  secret: "your-app-secret"
  page-access-token: "your-page-token"

# Telegram
telegram:
  access_token: "your-bot-token"
  verify: "your-verify-token"
  webhook_url: "https://your-domain/webhooks/telegram/webhook"
```

## 📊 34 Tỉnh thành

### 6 Thành phố trực thuộc TW
1. Hà Nội
2. Huế  
3. Đà Nẵng (← Quảng Nam)
4. Hải Phòng (← Hải Dương)
5. Hồ Chí Minh (← Bình Dương, Bà Rịa Vũng Tàu)
6. Cần Thơ (← Sóc Trăng, Hậu Giang)

### 28 Tỉnh (xem file danh sách đầy đủ)

## 🐛 Xử lý lỗi

### Lỗi: `Can't load class for name 'HFTransformersNLP'`

**Nguyên nhân:** Component cũ đã bị loại bỏ  
**Giải pháp:** Sử dụng `LanguageModelFeaturizer` như trong config.yml mẫu

### Lỗi: Out of Memory

**Giải pháp:**
1. Đổi sang PhoBERT Base
2. Giảm `batch_size`
3. Giảm `epochs`
4. Tăng RAM

### Lỗi: Intent không được nhận diện

**Giải pháp:**
1. Kiểm tra `domain.yml` có đầy đủ intent không
2. Thêm ví dụ trong `nlu.yml`
3. Train lại model

### Bot không tìm thấy tỉnh

**Giải pháp:**
1. Kiểm tra file JSON có trong `data/knowledge_base/`
2. Chạy `python validate_knowledge_base.py`
3. Kiểm tra `location_map` trong `actions.py`

## 📝 Bổ sung dữ liệu

### Thêm tỉnh mới

1. Tạo file `ten_tinh.json` trong `data/knowledge_base/`
2. Sao chép cấu trúc từ `bac_ninh.json`
3. Điền thông tin
4. Chạy validate: `python validate_knowledge_base.py`

### Thêm intent mới

1. Thêm vào `domain.yml`:
```yaml
intents:
  - intent_moi
```

2. Thêm examples vào `nlu.yml`:
```yaml
- intent: intent_moi
  examples: |
    - câu ví dụ 1
    - câu ví dụ 2
```

3. Thêm rule/story vào `rules.yml` hoặc `stories.yml`

4. Train lại: `rasa train`

## 🧪 Testing

### Test NLU

```bash
rasa test nlu --nlu data/nlu.yml
```

### Test stories

```bash
rasa test core --stories data/stories.yml
```

### Interactive learning

```bash
rasa interactive
```

## 📈 Monitoring

### Xem logs

```bash
rasa run --debug
```

### Tracker store (lưu lịch sử)

Uncomment trong `endpoints.yml`:

```yaml
tracker_store:
  type: SQL
  dialect: "postgresql"
  url: "postgresql://user:password@localhost/rasa"
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo branch: `git checkout -b feature/new-feature`
3. Commit: `git commit -m 'Add new feature'`
4. Push: `git push origin feature/new-feature`
5. Tạo Pull Request

## 📄 License

MIT License

## 👥 Liên hệ

- Email: your-email@example.com
- Issues: [GitHub Issues](your-repo-url/issues)

## 🙏 Credits

- **Rasa**: Framework chatbot
- **PhoBERT**: VinAI Research
- **Dữ liệu**: Nghị quyết Quốc hội về sắp xếp đơn vị hành chính (12/6/2025)

---

Made with ❤️ for Vietnam Tourism