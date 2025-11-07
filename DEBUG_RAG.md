# 🔍 Debug RAG Fallback - Tại sao không gọi được?

## Vấn đề

Bạn đã nhập API key của Groq nhưng RAG fallback vẫn không gọi được.

## Các nguyên nhân có thể

### 1. ❌ Action Server chưa restart sau khi thêm .env

**Vấn đề:** Action server chỉ load .env khi khởi động. Nếu bạn thêm API key sau khi action server đã chạy, nó sẽ không nhận được.

**Giải pháp:**
```bash
# 1. Dừng action server (Ctrl+C)
# 2. Khởi động lại
rasa run actions
```

### 2. ❌ Intent không phải `out_of_scope` hoặc `nlu_fallback`

**Vấn đề:** `ActionRAGFallback` chỉ chạy khi intent là:
- `out_of_scope`
- `nlu_fallback`

Nếu intent khác, action sẽ return sớm và không gọi RAG.

**Kiểm tra:**
- Xem action server logs để biết intent được nhận diện là gì
- Test với message rõ ràng là out_of_scope: "giá vàng hôm nay", "thời tiết mai", "kể chuyện cười"

### 3. ❌ Message quá ngắn

**Vấn đề:** Nếu message có < 2 từ, action sẽ return sớm và không gọi RAG.

**Giải pháp:** Hỏi câu dài hơn, ví dụ:
- ❌ "xin chào" (2 từ) → sẽ bị detect là greet và return sớm
- ✅ "giá vàng hôm nay bao nhiêu" (5 từ) → sẽ gọi RAG

### 4. ❌ Confidence score quá thấp

**Vấn đề:** Nếu confidence score từ RAG search < threshold (0.55), action sẽ return sớm và không gọi LLM.

**Kiểm tra:**
- Xem action server logs: `RAG top score: ...`
- Nếu score < 0.55, sẽ thấy message: "Xin lỗi, tôi chưa chắc chắn câu trả lời..."

**Giải pháp:**
- Hỏi câu cụ thể hơn về du lịch Việt Nam
- Giảm threshold trong .env: `RAG_CONFIDENCE_THRESHOLD=0.45`

### 5. ❌ API key không đúng format

**Vấn đề:** Groq API key phải bắt đầu bằng `gsk_`

**Kiểm tra:**
```bash
python debug_rag.py
```

**Giải pháp:**
- Kiểm tra API key trong .env có đúng format không
- Đảm bảo không có khoảng trắng thừa

### 6. ❌ LLM_PROVIDER không đúng

**Vấn đề:** Nếu `LLM_PROVIDER` không phải `groq`, code sẽ không gọi Groq API.

**Kiểm tra:**
```bash
python debug_rag.py
```

**Giải pháp:**
- Đảm bảo .env có: `LLM_PROVIDER=groq`
- Restart action server

### 7. ❌ Package `groq` chưa được cài

**Vấn đề:** Nếu package `groq` chưa được cài, code sẽ báo lỗi khi gọi API.

**Kiểm tra:**
```bash
pip list | grep groq
```

**Giải pháp:**
```bash
pip install groq
```

## 🔧 Các bước debug

### Bước 1: Chạy script debug

```bash
python debug_rag.py
```

Script này sẽ kiểm tra:
- ✅ API key có được load không
- ✅ LLM_PROVIDER có đúng không
- ✅ RAG retriever có khởi tạo được không
- ✅ Synthesis có hoạt động không

### Bước 2: Kiểm tra action server logs

Khi test với message out_of_scope, xem logs:

```bash
rasa run actions --debug
```

Tìm các dòng:
- `[RAG_FALLBACK] invoked; intent=...`
- `[RAG] Provider: groq, API key set: True`
- `RAG top score: ...`
- `RAG synthesis failed: ...` (nếu có lỗi)

### Bước 3: Test với message rõ ràng

Test với các message này để đảm bảo intent là `out_of_scope`:

```
giá vàng hôm nay
thời tiết mai
kể chuyện cười
làm thế nào để nấu phở
bóng đá hôm nay
```

### Bước 4: Kiểm tra .env file

Đảm bảo .env có format đúng:

```bash
# .env
GROQ_API_KEY=gsk_your_actual_key_here
LLM_PROVIDER=groq
RAG_CONFIDENCE_THRESHOLD=0.55
```

**Lưu ý:**
- Không có khoảng trắng thừa
- Không có dấu ngoặc kép
- API key phải bắt đầu bằng `gsk_`

## ✅ Checklist

Trước khi báo lỗi, đảm bảo:

- [ ] Đã tạo .env file trong thư mục gốc của project
- [ ] Đã set `GROQ_API_KEY` (bắt đầu bằng `gsk_`)
- [ ] Đã set `LLM_PROVIDER=groq`
- [ ] Đã restart action server sau khi thêm .env
- [ ] Đã cài package `groq`: `pip install groq`
- [ ] Đã test với message có intent `out_of_scope` hoặc `nlu_fallback`
- [ ] Đã check action server logs để xem có lỗi gì không
- [ ] Message có >= 2 từ
- [ ] Confidence score >= threshold (0.55)

## 🐛 Common Issues

### Issue 1: "GROQ_API_KEY not set"

**Nguyên nhân:** API key không được load từ .env

**Giải pháp:**
1. Kiểm tra .env có đúng tên file không (`.env`, không phải `.env.txt`)
2. Kiểm tra .env có trong thư mục gốc của project không
3. Restart action server

### Issue 2: "RAG synthesis failed: ..."

**Nguyên nhân:** Có lỗi khi gọi Groq API

**Giải pháp:**
1. Kiểm tra API key có đúng không
2. Kiểm tra package `groq` có được cài không
3. Kiểm tra internet connection
4. Xem full error message trong logs

### Issue 3: "Xin lỗi, tôi chưa chắc chắn câu trả lời..."

**Nguyên nhân:** Confidence score < threshold

**Giải pháp:**
1. Hỏi câu cụ thể hơn về du lịch Việt Nam
2. Giảm threshold: `RAG_CONFIDENCE_THRESHOLD=0.45`

### Issue 4: Action không được gọi

**Nguyên nhân:** Intent không phải `out_of_scope` hoặc `nlu_fallback`

**Giải pháp:**
1. Test với message rõ ràng là out_of_scope
2. Check rules.yml có rule gọi `action_rag_fallback` không
3. Train lại model nếu cần

## 📞 Liên hệ

Nếu vẫn không giải quyết được, cung cấp:
1. Output của `python debug_rag.py`
2. Action server logs khi test
3. Nội dung .env (ẩn API key)
4. Message bạn đã test

