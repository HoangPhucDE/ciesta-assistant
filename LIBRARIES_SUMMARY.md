# 📚 Tóm Tắt Thư Viện Sử Dụng

## 🎯 Thư Viện Chính (35+ packages)

### 1. Core Framework
- **rasa** `3.6.20` - Chatbot framework
- **rasa-sdk** `3.6.2` - Custom actions SDK

### 2. Machine Learning & NLP
- **transformers** `4.35.2` - Hugging Face Transformers (PhoBERT)
- **torch** `2.1.2` - PyTorch
- **numpy** `1.23.5` - Numerical computing
- **faiss-cpu** `1.8.0.post1` - Vector search (RAG)
- **tokenizers** `0.15.0` - Tokenization
- **sentencepiece** `0.1.99` - Tokenization
- **huggingface_hub** `0.25.2` - Model download

### 3. LLM APIs
- **openai** `1.48.0` - OpenAI API
- **groq** `0.9.0` - Groq API
- **google-generativeai** `0.8.3` - Gemini API

### 4. Desktop GUI
- **PySide6** `6.7.2` - Qt framework

### 5. Web Framework
- **flask** `3.0.3` - Web framework
- **flask-cors** `5.0.0` - CORS support
- **requests** `2.32.3` - HTTP client
- **gunicorn** `23.0.0` - Production server

### 6. Utilities
- **python-dotenv** `1.0.1` - Environment variables
- **rich** `13.8.1` - Terminal output
- **tqdm** `4.66.5` - Progress bars
- **regex** `2024.5.15` - Advanced regex
- **pandas** `1.5.3` - Data processing

### 7. Visualization
- **matplotlib** `3.5.3` - Plotting
- **seaborn** `0.12.2` - Statistical plots
- **plotly** `5.24.0` - Interactive plots

### 8. Development Tools
- **black** `22.12.0` - Code formatter
- **isort** `5.13.2` - Import sorter
- **ruff** `0.6.5` - Linter
- **jupyter** `1.1.1` - Notebooks
- **ipykernel** `6.29.5` - IPython kernel

### 9. Database & Validation
- **sqlalchemy** `1.4.52` - Database ORM
- **fastjsonschema** `2.20.0` - JSON validation

---

## 📋 Danh Sách Đầy Đủ

Xem file [LIBRARIES.md](LIBRARIES.md) để biết chi tiết đầy đủ về:
- Tất cả thư viện và mục đích sử dụng
- File nào sử dụng thư viện nào
- Dependencies tự động
- Standard library modules
- Hướng dẫn cài đặt

---

## 🚀 Cài Đặt Nhanh

```bash
pip install -r requirements.txt
```

---

## 📊 Thống Kê

- **Tổng số packages**: 35+ chính
- **Dependencies tự động**: 100+ (Rasa, PyTorch, etc.)
- **Python version**: 3.10
- **Dung lượng**: ~3-4GB (bao gồm models)

---

## 🔍 Kiểm Tra Thư Viện

```bash
# Xem tất cả packages
pip list

# Kiểm tra package cụ thể
pip show rasa

# Generate danh sách từ code
python scripts/generate_libraries_list.py
```

