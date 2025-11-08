# 🌏 Ciesta - Bot Du lịch Việt Nam

Chào bạn! Đây là **Ciesta**, một chatbot thông minh giúp bạn khám phá văn hóa và du lịch của **34 tỉnh thành Việt Nam** sau khi sắp xếp lại đơn vị hành chính (theo Nghị quyết 12/6/2025).

## 🎯 Bot này làm được gì?

Bot có thể trả lời các câu hỏi về:

- **Văn hóa & lịch sử**: Giới thiệu về văn hóa đặc trưng của từng tỉnh sau khi sáp nhập
- **Địa điểm du lịch**: Các điểm tham quan nổi tiếng, di sản thế giới, danh thắng
- **Ẩm thực**: Món ăn đặc sản, quán ăn nổi tiếng, đặc sản theo mùa
- **Lễ hội**: Thời gian, địa điểm, ý nghĩa của các lễ hội truyền thống
- **Mẹo du lịch**: Hơn 400 tips thực tế cho 34 tỉnh - từ thời gian tham quan, phương tiện di chuyển, đến quà lưu niệm và lưu ý an toàn
- **Quà lưu niệm**: Đặc sản nên mua làm quà khi đến mỗi tỉnh

Bot hiểu được nhiều cách gọi tên khác nhau. Ví dụ: "Sài Gòn" → Hồ Chí Minh, "Hội An" → Đà Nẵng, "Bắc Giang" → Bắc Ninh (sau sáp nhập).

## 🚀 Tính năng nổi bật

- ✅ **PhoBERT Large** làm nền tảng xử lý ngôn ngữ tiếng Việt (độ chính xác cao)
- ✅ **RAG Fallback** thông minh: Khi bot không chắc chắn, sẽ tự động tìm kiếm trong knowledge base
- ✅ **REST API** sẵn sàng để tích hợp vào website/app
- ✅ **Giao diện desktop** (PySide6) để test và demo
- ✅ **Hơn 400 travel tips** thực tế cho 34 tỉnh thành
- ✅ **Cấu hình tối ưu**: 600 epochs, learning rate 0.0002, confidence threshold 0.70

## 💻 Yêu cầu hệ thống

- **Python**: 3.10 trở lên
- **RAM**: Tối thiểu 12GB (khuyến nghị 16GB+ cho PhoBERT Large)
- **GPU**: Tùy chọn nhưng khuyến nghị (CUDA) để train nhanh hơn
- **Dung lượng**: Khoảng 5-6GB cho model và các thư viện

## 📦 Cài đặt

### Bước 1: Clone project

```bash
git clone <your-repo-url>
cd ciesta-asisstant
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv .venv

# Trên Linux/Mac:
source .venv/bin/activate

# Trên Windows:
.venv\Scripts\activate
```

### Bước 3: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

**Lưu ý:** Project đang dùng các phiên bản cụ thể để đảm bảo tương thích:
- `numpy==1.23.5` (phải < 1.24 cho TensorFlow 2.12)
- `transformers==4.35.2`
- `torch==2.1.2`
- `rasa==3.6.20`

### Bước 4: Tải PhoBERT Large (tự động)

Lần đầu train, Rasa sẽ tự động tải PhoBERT Large (~1.2GB) từ HuggingFace và cache vào `models_hub/phobert_cache/`.

Nếu muốn tải trước để dùng offline:

```bash
python scripts/training/download_model.py
```

**Lưu ý:** Script hiện tại tải PhoBERT Base. Nếu muốn tải Large, sửa trong script:
```python
repo_id = "vinai/phobert-large"
local_dir = "models_hub/phobert-large"
```

## 📁 Cấu trúc project

```
ciesta-asisstant/
├── config.yml              # Cấu hình chính (PhoBERT Large, pipeline tối ưu)
├── domain.yml              # Định nghĩa intents, entities, actions
├── endpoints.yml           # Cấu hình endpoints
├── credentials.yml         # Cấu hình channels (Telegram, Facebook...)
│
├── actions/                # Custom actions server
│   └── actions.py         # Logic xử lý các actions + RAG fallback
│
├── data/
│   ├── nlu.yml            # Training data cho NLU
│   ├── rules.yml          # Rules cho bot
│   ├── stories.yml         # Stories cho training
│   └── knowledge_base/
│       └── provinces/     # 34 file JSON - dữ liệu về các tỉnh
│           ├── ha_noi.json
│           ├── ho_chi_minh.json
│           ├── da_nang.json
│           └── ... (31 tỉnh khác)
│
├── custom_components/      # Components tùy chỉnh
│   ├── phobert_featurizer.py    # PhoBERT Large featurizer
│   └── vietnamese_preprocessor.py
│
├── rag/                   # RAG fallback system
│   └── retriever.py       # FAISS + PhoBERT embedding
│
├── models_hub/            # Models đã tải về
│   └── phobert_cache/     # Cache của PhoBERT Large
│
└── models/                # Models sau khi train
```

## 🎓 Training model

### Kiểm tra dữ liệu trước

```bash
python scripts/validation/validate_knowledge_base.py
```

Script này sẽ kiểm tra:
- Tất cả 34 tỉnh đã có file JSON chưa
- Cấu trúc dữ liệu có đúng không
- Các trường bắt buộc đã điền đầy đủ chưa (bao gồm `travel_tips`)

### Train model

```bash
# Train toàn bộ (NLU + Core)
rasa train

# Chỉ train NLU
rasa train nlu

# Chỉ train Core
rasa train core
```

**Lưu ý quan trọng:**
- Lần đầu train sẽ tự động tải PhoBERT Large (~1.2GB) nếu chưa có
- Training với PhoBERT Large mất nhiều thời gian hơn (có thể 1-2 giờ tùy máy)
- Với cấu hình hiện tại: **600 epochs**, learning rate **0.0002**, confidence threshold **0.70**
- Nếu thiếu RAM, có thể giảm `batch_size` trong `config.yml`

### Cấu hình training hiện tại

Project đang dùng cấu hình tối ưu trong `config.yml`:

```yaml
- name: custom_components.phobert_featurizer.PhoBERTFeaturizer
  model_name: "vinai/phobert-large"  # PhoBERT Large
  cache_dir: "models_hub/phobert_cache"
  max_length: 256
  pooling_strategy: "mean_max"  # Mean + Max pooling (1024*2 = 2048 dims)

- name: DIETClassifier
  epochs: 600                    # Tăng từ 500 lên 600
  learning_rate: 0.0002          # Giảm từ 0.0003 xuống 0.0002
  confidence_threshold: 0.70     # Tăng từ 0.60 lên 0.70
  embedding_dimension: 2048      # Khớp với PhoBERT-large mean_max
  batch_size: [16, 32]
```

## 🚀 Chạy bot

### Cách 1: Test trong shell (nhanh nhất)

Mở 2 terminal:

**Terminal 1** - Chạy action server:
```bash
rasa run actions
```

**Terminal 2** - Chạy shell để chat:
```bash
rasa shell
```

### Cách 2: Chạy REST API

**Terminal 1** - Action server:
```bash
rasa run actions
```

**Terminal 2** - Rasa server:
```bash
rasa run --enable-api --cors "*"
```

API sẽ chạy tại: `http://localhost:5005`

**Test API:**
```bash
curl -X POST http://localhost:5005/webhooks/rest/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test_user",
    "message": "Mẹo du lịch Hà Nội"
  }'
```

### Cách 3: Dùng giao diện desktop

```bash
python ciesta/main.py
```

### Cách 4: Kết nối từ xa với Ngrok

Xem hướng dẫn chi tiết: [NGROK_QUICK_GUIDE.md](NGROK_QUICK_GUIDE.md)

**Tóm tắt:**
1. Chạy action server: `rasa run actions`
2. Chạy rasa server: `rasa run --enable-api --cors "*"`
3. Chạy ngrok: `ngrok http 5005`
4. Lấy URL từ ngrok và cấu hình trong frontend

## 💬 Ví dụ sử dụng

### Hỏi về văn hóa
```
Bạn: Giới thiệu về Bắc Ninh
Bot: Bắc Ninh mới là sự hội tụ tinh hoa của cả vùng Kinh Bắc và vùng văn hóa trung du...
```

### Hỏi về địa điểm
```
Bạn: Đà Nẵng có địa điểm nào đẹp?
Bot: Đà Nẵng có nhiều điểm tham quan nổi tiếng như Phố cổ Hội An (Di sản thế giới)...
```

### Hỏi về ẩm thực
```
Bạn: Ăn gì ở Hội An?
Bot: Hội An nổi tiếng với cao lầu, mì Quảng, bánh mì Phượng...
```

### Hỏi về mẹo du lịch ⭐ (MỚI)
```
Bạn: Mẹo du lịch Hà Nội
Bot: 1. Nên dành ít nhất 3-4 ngày để khám phá đầy đủ...
     2. Di chuyển trong phố cổ nên đi bộ hoặc xe đạp...
     3. Thử các món đặc sản: phở Hà Nội, bún chả...
     ...
```

### Hỏi về lễ hội
```
Bạn: Bắc Ninh có lễ hội gì?
Bot: Bắc Ninh có nhiều lễ hội lớn như Hội Lim (13 tháng Giêng)...
```

### Hỏi về tỉnh sau sáp nhập
```
Bạn: Bắc Giang giờ thuộc tỉnh nào?
Bot: Bắc Giang đã được sáp nhập vào Bắc Ninh theo Nghị quyết...
```

## ⚙️ Cấu hình nâng cao

### Tùy chỉnh PhoBERT

**Hiện tại đang dùng PhoBERT Large** trong `config.yml`:
```yaml
- name: custom_components.phobert_featurizer.PhoBERTFeaturizer
  model_name: "vinai/phobert-large"  # PhoBERT Large
  cache_dir: "models_hub/phobert_cache"
  max_length: 256
  pooling_strategy: "mean_max"  # Mean + Max pooling
```

**Nếu muốn dùng PhoBERT Base** (tiết kiệm RAM):
1. Sửa trong `config.yml`:
```yaml
model_name: "vinai/phobert-base"
pooling_strategy: "mean_max"  # hoặc "mean"
```

2. Giảm `embedding_dimension` trong DIETClassifier:
```yaml
embedding_dimension: 1024  # Thay vì 2048
```

### Cấu hình RAG Fallback

RAG sẽ tự động kích hoạt khi:
- Bot không hiểu câu hỏi (`out_of_scope`)
- NLU không chắc chắn (`nlu_fallback`)

RAG sử dụng FAISS + PhoBERT embedding để tìm kiếm trong knowledge base.

**Tùy chọn:** Dùng LLM để tổng hợp câu trả lời (cần API key):
```bash
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini
```

Hoặc dùng Groq/Google Gemini (xem trong `rag/retriever.py`).

### Giảm RAM nếu máy yếu

Nếu thiếu RAM, có thể:

1. **Đổi sang PhoBERT Base** (giảm từ ~1.2GB xuống ~600MB)
2. **Giảm batch size** trong `config.yml`:
```yaml
- name: DIETClassifier
  batch_size: [8, 16]  # Giảm từ [16, 32]
```
3. **Giảm epochs**:
```yaml
epochs: 300  # Giảm từ 600
```
4. **Giảm embedding dimension** (nếu dùng Base):
```yaml
embedding_dimension: 1024  # Thay vì 2048
```

### Thêm channels (Telegram, Facebook...)

Chỉnh sửa `credentials.yml`:
```yaml
telegram:
  access_token: "your-bot-token"
  verify: "your-verify-token"
  webhook_url: "https://your-domain/webhooks/telegram/webhook"
```

## 📊 Dữ liệu hiện có

### 34 Tỉnh thành đã có đầy đủ dữ liệu:

**6 Thành phố trực thuộc TW:**
1. Hà Nội
2. Huế
3. Đà Nẵng (sáp nhập Quảng Nam)
4. Hải Phòng (sáp nhập Hải Dương)
5. Hồ Chí Minh (sáp nhập Bình Dương, Bà Rịa - Vũng Tàu)
6. Cần Thơ (sáp nhập Sóc Trăng, Hậu Giang)

**28 Tỉnh khác:**
- **Miền Bắc**: Bắc Ninh, Cao Bằng, Điện Biên, Hà Tĩnh, Hưng Yên, Lạng Sơn, Lai Châu, Lào Cai, Nghệ An, Ninh Bình, Phú Thọ, Quảng Ninh, Sơn La, Thái Nguyên, Thanh Hóa, Tuyên Quang
- **Miền Trung**: Khánh Hòa, Quảng Ngãi, Quảng Trị
- **Tây Nguyên**: Đắk Lắk, Gia Lai, Lâm Đồng
- **Miền Nam**: An Giang, Cà Mau, Đồng Nai, Đồng Tháp, Tây Ninh, Vĩnh Long

### Mỗi tỉnh có đầy đủ:
- ✅ Thông tin văn hóa chi tiết
- ✅ Danh sách địa điểm tham quan
- ✅ Món ăn đặc sản
- ✅ Lễ hội truyền thống
- ✅ Quà lưu niệm
- ✅ Thời gian du lịch tốt nhất
- ✅ **Hơn 10 travel tips thực tế** (mới bổ sung!)

## 🐛 Xử lý lỗi thường gặp

### Lỗi: `Can't load class for name 'HFTransformersNLP'`

**Nguyên nhân:** Component cũ đã bị loại bỏ  
**Giải pháp:** Đã thay bằng `PhoBERTFeaturizer` tùy chỉnh. Kiểm tra lại `config.yml`.

### Lỗi: Out of Memory

**Giải pháp:**
1. Đảm bảo có ít nhất 12GB RAM (khuyến nghị 16GB+)
2. Nếu thiếu RAM, đổi sang PhoBERT Base (xem phần "Giảm RAM")
3. Giảm `batch_size` trong `config.yml`
4. Giảm số `epochs`
5. Nâng cấp RAM nếu có thể

### Lỗi: Training quá lâu

**Giải pháp:**
1. Dùng GPU (CUDA) nếu có
2. Giảm số `epochs` xuống 300-400
3. Giảm `batch_size`
4. Dùng PhoBERT Base thay vì Large

### Bot không nhận diện được intent

**Giải pháp:**
1. Kiểm tra `domain.yml` có đầy đủ intent không
2. Thêm nhiều ví dụ hơn vào `nlu.yml`
3. Train lại model: `rasa train`
4. Kiểm tra confidence threshold (hiện tại 0.70 - có thể giảm xuống 0.60 nếu quá strict)

### Bot không tìm thấy tỉnh

**Giải pháp:**
1. Chạy `python scripts/validation/validate_knowledge_base.py` để kiểm tra
2. Kiểm tra file JSON có trong `data/knowledge_base/provinces/`
3. Kiểm tra `location_map.json` có mapping đúng không

## 📝 Bổ sung dữ liệu

### Thêm tỉnh mới

1. Tạo file `ten_tinh.json` trong `data/knowledge_base/provinces/`
2. Copy cấu trúc từ file tỉnh có sẵn (ví dụ: `bac_ninh.json`)
3. Điền đầy đủ thông tin:
   - `culture_details`: Thông tin văn hóa
   - `places_to_visit`: Địa điểm tham quan
   - `what_to_eat`: Món ăn đặc sản
   - `festivals`: Lễ hội
   - `specialties_as_gifts`: Quà lưu niệm
   - `best_time_to_visit`: Thời gian du lịch tốt nhất
   - `travel_tips`: **Mẹo du lịch thực tế** (10-12 tips)
4. Chạy validate: `python scripts/validation/validate_knowledge_base.py`

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
    - câu ví dụ 3
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

### Interactive learning (học tương tác)
```bash
rasa interactive
```

## 📈 Monitoring & Debug

### Xem logs chi tiết
```bash
rasa run --debug
```

### Lưu lịch sử conversation

Uncomment trong `endpoints.yml`:
```yaml
tracker_store:
  type: SQL
  dialect: "postgresql"
  url: "postgresql://user:password@localhost/rasa"
```

## 🤝 Đóng góp

Rất hoan nghênh mọi đóng góp! Các cách bạn có thể giúp:

1. **Báo lỗi**: Tạo issue trên GitHub
2. **Đề xuất tính năng**: Mở discussion
3. **Cải thiện dữ liệu**: Bổ sung thông tin về các tỉnh
4. **Dịch thuật**: Giúp bot hỗ trợ nhiều ngôn ngữ hơn
5. **Code**: Fork, tạo branch, commit và tạo Pull Request

**Quy trình:**
```bash
git checkout -b feature/new-feature
git commit -m 'Add new feature'
git push origin feature/new-feature
```

## 📄 License

MIT License - Tự do sử dụng cho mục đích cá nhân và thương mại.

## 👥 Liên hệ

- **Email**: phuchn0305@gmail.com
- **Issues**: [GitHub Issues](your-repo-url/issues)

## 🙏 Credits

- **Rasa**: Framework chatbot mã nguồn mở tuyệt vời
- **PhoBERT**: Model xử lý ngôn ngữ tiếng Việt từ VinAI Research
- **Dữ liệu**: Dựa trên Nghị quyết Quốc hội về sắp xếp đơn vị hành chính (12/6/2025)
- **Travel Tips**: Tổng hợp từ kinh nghiệm thực tế và nguồn tin cậy

---

**Made with ❤️ for Vietnam Tourism**

*Ciesta - Your smart travel companion for exploring Vietnam!*
