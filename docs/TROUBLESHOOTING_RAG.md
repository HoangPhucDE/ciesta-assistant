# 🔧 Troubleshooting RAG Fallback

## ❌ Vấn đề: Fallback không dùng LLM, chỉ trả về intents

### Nguyên nhân có thể:

1. **Action server không load .env file**
2. **API key không đúng hoặc thiếu**
3. **LLM_PROVIDER không được set**
4. **Action server chưa restart sau khi thêm .env**

## ✅ Giải pháp

### Bước 1: Kiểm tra file .env

Đảm bảo file `.env` ở thư mục gốc của project với nội dung:

```bash
# Ví dụ với Groq
GROQ_API_KEY=your-actual-api-key-here
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-70b-versatile
```

**Lưu ý:**
- Không có khoảng trắng quanh dấu `=`
- Không có quotes (`"` hoặc `'`) quanh giá trị
- Mỗi biến một dòng

### Bước 2: Kiểm tra action server có load .env không

Action server sẽ tự động load `.env` khi khởi động. Kiểm tra logs:

```bash
# Khi start action server, tìm dòng:
[Actions] Loaded .env from /path/to/.env
```

Nếu không thấy, có thể:
- File .env không ở đúng vị trí
- python-dotenv chưa được cài

### Bước 3: Restart Action Server

**QUAN TRỌNG**: Sau khi thêm/sửa `.env`, **PHẢI restart action server**:

```bash
# Dừng action server (Ctrl+C)
# Sau đó start lại
rasa run actions
```

### Bước 4: Kiểm tra environment variables

Test xem action server có đọc được env vars không:

```python
# Tạo file test: test_env.py
import os
from dotenv import load_dotenv
load_dotenv()

print("GROQ_API_KEY:", "SET" if os.getenv("GROQ_API_KEY") else "NOT SET")
print("LLM_PROVIDER:", os.getenv("LLM_PROVIDER", "NOT SET"))
```

Chạy:
```bash
python test_env.py
```

### Bước 5: Kiểm tra logs

Khi RAG fallback được trigger, kiểm tra logs:

```bash
# Trong logs của action server, tìm:
[RAG] Provider: groq, API key set: True
```

Nếu thấy `API key set: False`, nghĩa là API key chưa được load.

## 🔍 Debug chi tiết

### Test RAG trực tiếp

```python
# test_rag.py
import os
from dotenv import load_dotenv
load_dotenv()

from rag.retriever import RAGRetriever

# Test
retriever = RAGRetriever('data/knowledge_base/provinces')
results = retriever.search("Đà Nẵng có gì đẹp?", top_k=3)
answer = retriever.synthesize("Đà Nẵng có gì đẹp?", results)
print("Answer:", answer)
```

### Kiểm tra intent có phải out_of_scope không

RAG chỉ chạy khi intent là `out_of_scope` hoặc `nlu_fallback`.

Kiểm tra trong Rasa shell:
```
Your input ->  một câu hỏi không liên quan
NLU classification:
  intent: out_of_scope  <-- Phải là intent này
```

Nếu không phải `out_of_scope`, RAG sẽ không chạy.

## 🎯 Checklist

- [ ] File `.env` ở thư mục gốc (cùng cấp với `actions/`, `rag/`)
- [ ] `.env` có format đúng (KEY=value, không có quotes)
- [ ] Đã set `LLM_PROVIDER` (groq, openai, etc.)
- [ ] Đã set API key tương ứng (GROQ_API_KEY, OPENAI_API_KEY, etc.)
- [ ] Đã **restart action server** sau khi thêm .env
- [ ] Action server logs hiển thị "Loaded .env"
- [ ] Intent là `out_of_scope` hoặc `nlu_fallback`
- [ ] RAG confidence score >= threshold (0.55)

## 🐛 Các lỗi thường gặp

### Lỗi: "API key not set"
**Nguyên nhân**: .env không được load hoặc key sai tên
**Giải pháp**: 
- Kiểm tra tên biến trong .env (phải đúng: GROQ_API_KEY, không phải GROQ_KEY)
- Restart action server

### Lỗi: "Provider not found"
**Nguyên nhân**: LLM_PROVIDER không đúng hoặc package chưa cài
**Giải pháp**:
- Kiểm tra LLM_PROVIDER trong .env (groq, openai, etc.)
- Cài package tương ứng: `pip install groq` hoặc `pip install openai`

### Lỗi: "Intent không phải out_of_scope"
**Nguyên nhân**: NLU classify sai intent
**Giải pháp**:
- Thêm examples vào `data/nlu.yml` cho intent `out_of_scope`
- Train lại model: `rasa train`

## 📝 Ví dụ .env đúng

```bash
# Groq (Khuyến nghị)
GROQ_API_KEY=gsk_your_actual_key_here
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-70b-versatile

# Hoặc OpenAI
OPENAI_API_KEY=sk-your_actual_key_here
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# RAG Settings
RAG_CONFIDENCE_THRESHOLD=0.55
```

## 🔄 Workflow đúng

1. Tạo/sửa file `.env`
2. **Restart action server**: `rasa run actions`
3. Test với câu hỏi out_of_scope
4. Kiểm tra logs để xem LLM có được gọi không

