# 🆓 Hướng dẫn lấy API LLM miễn phí

## 📋 Danh sách API miễn phí (2024-2025)

### 1. **Groq** ⭐ (Khuyến nghị - Nhanh nhất)
- **Website**: https://console.groq.com
- **Free tier**: 
  - 14,400 requests/day
  - Không giới hạn tokens
  - Rất nhanh (GPU inference)
- **Models**: Llama 3.1 70B, Mixtral 8x7B, Gemma 7B
- **Cách lấy**:
  1. Đăng ký tại https://console.groq.com
  2. Tạo API key
  3. Copy API key
- **Setup**:
  ```bash
  export GROQ_API_KEY=your-key-here
  export LLM_PROVIDER=groq
  export LLM_MODEL=llama-3.1-70b-versatile
  ```

### 2. **Hugging Face Inference API** ⭐ (Miễn phí, nhiều models)
- **Website**: https://huggingface.co
- **Free tier**: 
  - 1,000 requests/month (free)
  - Nhiều models miễn phí
- **Models**: Mistral, Llama, Gemma, v.v.
- **Cách lấy**:
  1. Đăng ký tại https://huggingface.co
  2. Vào Settings → Access Tokens
  3. Tạo token mới
- **Setup**:
  ```bash
  export HUGGINGFACE_API_KEY=your-token-here
  export LLM_PROVIDER=huggingface
  export LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.2
  ```

### 3. **Together AI** (Free tier tốt)
- **Website**: https://together.ai
- **Free tier**: 
  - $25 credits miễn phí cho new users
  - Nhiều models
- **Cách lấy**:
  1. Đăng ký tại https://together.ai
  2. Nhận $25 credits
  3. Tạo API key
- **Setup**:
  ```bash
  export TOGETHER_API_KEY=your-key-here
  export LLM_PROVIDER=together
  export LLM_MODEL=meta-llama/Llama-3-8b-chat-hf
  ```

### 4. **Google Gemini** (Free tier)
- **Website**: https://aistudio.google.com
- **Free tier**: 
  - 60 requests/minute
  - 1,500 requests/day
- **Models**: gemini-pro, gemini-pro-vision
- **Cách lấy**:
  1. Đăng ký tại https://aistudio.google.com
  2. Tạo API key
- **Setup**:
  ```bash
  export GOOGLE_API_KEY=your-key-here
  export LLM_PROVIDER=gemini
  export LLM_MODEL=gemini-pro
  ```

### 5. **OpenAI** (Free credits cho new users)
- **Website**: https://platform.openai.com
- **Free tier**: 
  - $5 credits cho new users (có thể hết)
  - Sau đó phải trả phí
- **Cách lấy**:
  1. Đăng ký tại https://platform.openai.com
  2. Nhận $5 credits
  3. Tạo API key
- **Setup**:
  ```bash
  export OPENAI_API_KEY=sk-...
  export LLM_PROVIDER=openai
  export LLM_MODEL=gpt-4o-mini
  ```

### 6. **Anthropic Claude** (Free tier hạn chế)
- **Website**: https://console.anthropic.com
- **Free tier**: 
  - Có free tier nhưng hạn chế
- **Cách lấy**:
  1. Đăng ký tại https://console.anthropic.com
  2. Tạo API key
- **Setup**:
  ```bash
  export ANTHROPIC_API_KEY=your-key-here
  export LLM_PROVIDER=claude
  export LLM_MODEL=claude-3-haiku-20240307
  ```

### 7. **Local LLM** (Hoàn toàn miễn phí - Không cần API)
- **Ollama**: https://ollama.ai
- **Cách setup**:
  ```bash
  # Cài Ollama
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Download model
  ollama pull llama3.2
  
  # Chạy local
  ollama serve
  ```
- **Setup trong code**:
  ```bash
  export LLM_PROVIDER=ollama
  export LLM_MODEL=llama3.2
  export OLLAMA_BASE_URL=http://localhost:11434
  ```

## 🎯 So sánh nhanh

| Provider | Free Tier | Tốc độ | Chất lượng | Khuyến nghị |
|----------|-----------|--------|------------|-------------|
| **Groq** | ⭐⭐⭐⭐⭐ | ⚡⚡⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ Tốt nhất |
| Hugging Face | ⭐⭐⭐⭐ | ⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ Tốt |
| Together AI | ⭐⭐⭐⭐ | ⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ Tốt |
| Gemini | ⭐⭐⭐ | ⚡⚡⚡ | ⭐⭐⭐⭐ | ✅ OK |
| OpenAI | ⭐⭐ | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | ⚠️ Có phí sau free |
| Local (Ollama) | ⭐⭐⭐⭐⭐ | ⚡⚡ | ⭐⭐⭐ | ✅ Miễn phí 100% |

## 🚀 Khuyến nghị

**Cho production/test nhanh**: **Groq** (nhanh, free tier tốt)
**Cho privacy**: **Local LLM (Ollama)** (hoàn toàn offline)
**Cho nhiều models**: **Hugging Face** (nhiều lựa chọn)

## 📝 Lưu ý

- Các free tier có thể thay đổi theo thời gian
- Luôn kiểm tra terms of service
- Không share API keys công khai
- Monitor usage để tránh vượt quota

