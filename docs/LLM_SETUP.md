# 🚀 Hướng dẫn setup LLM cho RAG

## ⚡ Quick Start - Groq (Khuyến nghị - Nhanh & Miễn phí)

### Bước 1: Lấy API key
1. Đăng ký tại: https://console.groq.com
2. Tạo API key
3. Copy key

### Bước 2: Setup environment

**⚠️ QUAN TRỌNG: Không commit API key vào git!**

**Cách 1: Dùng file .env (Khuyến nghị)**
```bash
# Tạo file .env trong thư mục gốc
echo "GROQ_API_KEY=your-actual-api-key-here" > .env
echo "LLM_PROVIDER=groq" >> .env
echo "GROQ_MODEL=llama-3.1-70b-versatile" >> .env
```

**Cách 2: Export trực tiếp (chỉ cho session hiện tại)**
```bash
export GROQ_API_KEY=your-actual-api-key-here
export LLM_PROVIDER=groq
export GROQ_MODEL=llama-3.1-70b-versatile
```

### Bước 3: Test
```bash
# Test RAG với Groq
python -c "from rag.retriever import RAGRetriever; r = RAGRetriever('data/knowledge_base/provinces'); print(r.synthesize('test', []))"
```

## 📝 Các providers khác

### OpenAI
```bash
export OPENAI_API_KEY=sk-...
export LLM_PROVIDER=openai
export OPENAI_MODEL=gpt-4o-mini
```

### Hugging Face
```bash
export HUGGINGFACE_API_KEY=hf_...
export LLM_PROVIDER=huggingface
export HUGGINGFACE_MODEL=mistralai/Mistral-7B-Instruct-v0.2
```

### Together AI
```bash
export TOGETHER_API_KEY=...
export LLM_PROVIDER=together
export TOGETHER_MODEL=meta-llama/Llama-3-8b-chat-hf
```

### Google Gemini
```bash
export GOOGLE_API_KEY=...
export LLM_PROVIDER=gemini
export GEMINI_MODEL=gemini-pro
```

### Ollama (Local - Hoàn toàn miễn phí)
```bash
# Cài Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download model
ollama pull llama3.2

# Setup env
export LLM_PROVIDER=ollama
export OLLAMA_MODEL=llama3.2
export OLLAMA_BASE_URL=http://localhost:11434
```

## 🔄 Auto-detect (thử tất cả providers)
```bash
export LLM_PROVIDER=auto
# Sẽ thử theo thứ tự: groq → openai → huggingface → together → gemini → ollama
```

## 📊 So sánh

| Provider | Setup | Tốc độ | Free Tier | Khuyến nghị |
|----------|-------|--------|-----------|-------------|
| Groq | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | 14,400 req/day | ✅ Tốt nhất |
| Ollama | ⭐⭐⭐ | ⚡⚡ | Unlimited | ✅ Privacy |
| Hugging Face | ⭐⭐⭐⭐ | ⚡⚡⚡ | 1,000 req/month | ✅ OK |
| Together | ⭐⭐⭐⭐ | ⚡⚡⚡ | $25 credits | ✅ OK |
| OpenAI | ⭐⭐⭐ | ⚡⚡⚡ | $5 credits | ⚠️ Có phí |

## 🎯 Khuyến nghị

**Cho production**: Groq (nhanh, free tier tốt)
**Cho privacy**: Ollama (local, hoàn toàn offline)
**Cho testing**: Bất kỳ provider nào có free tier

