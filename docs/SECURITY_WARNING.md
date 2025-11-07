# ⚠️ CẢNH BÁO BẢO MẬT

## 🚨 API Key đã bị lộ!

Nếu bạn đã vô tình commit API key vào git hoặc chia sẻ công khai, **HÀNH ĐỘNG NGAY**:

### Bước 1: Revoke API key cũ
1. **Groq**: Vào https://console.groq.com → API Keys → Xóa key cũ
2. **OpenAI**: Vào https://platform.openai.com → API Keys → Revoke key cũ
3. **Các providers khác**: Tương tự, vào dashboard và xóa key cũ

### Bước 2: Tạo API key mới
Tạo key mới từ dashboard của provider

### Bước 3: Lưu key an toàn
**KHÔNG BAO GIỜ commit API key vào git!**

Sử dụng file `.env`:
```bash
# Tạo file .env (đã có trong .gitignore)
echo "GROQ_API_KEY=your-new-key-here" > .env
```

### Bước 4: Xóa key khỏi git history (nếu đã commit)
```bash
# Xóa key khỏi file
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch docs/LLM_SETUP.md" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (cẩn thận!)
git push origin --force --all
```

## ✅ Best Practices

1. **Luôn dùng .env file** cho API keys
2. **Thêm .env vào .gitignore** (đã có)
3. **Dùng .env.example** làm template (không có key thật)
4. **Không paste key vào chat, email, hoặc file công khai**
5. **Rotate keys định kỳ** (đổi key mỗi vài tháng)

## 📝 Cách load .env trong Python

Code đã tự động load từ environment variables. Để load từ .env file:

```bash
# Cài python-dotenv (đã có trong requirements.txt)
pip install python-dotenv

# Load trong code
from dotenv import load_dotenv
load_dotenv()  # Load từ .env file
```

Hoặc chạy với:
```bash
# Linux/Mac
export $(cat .env | xargs)
python your_script.py

# Hoặc dùng python-dotenv
python -c "from dotenv import load_dotenv; load_dotenv(); import your_script"
```

