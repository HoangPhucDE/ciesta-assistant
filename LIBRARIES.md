# 📚 Danh Sách Toàn Bộ Thư Viện Sử Dụng Trong Dự Án

Tài liệu này liệt kê tất cả các thư viện Python được sử dụng trong dự án Ciesta Assistant.

---

## 📋 Tổng Quan

- **Tổng số thư viện**: 35+ thư viện chính
- **Python version**: 3.10
- **Package manager**: pip (requirements.txt)

---

## 🎯 1. Core Rasa Framework

### Rasa Core
- **rasa** `==3.6.20`
  - Framework chính cho chatbot
  - NLU và Core dialogue management
  - **Sử dụng trong**: Toàn bộ dự án
  
- **rasa-sdk** `==3.6.2`
  - SDK để viết custom actions
  - **Sử dụng trong**: `actions/actions.py`

### Rasa Dependencies (Tự động cài)
- **spacy** - NLP library (Rasa tự động cài)
- Các thư viện khác của Rasa ecosystem

---

## 🤖 2. Machine Learning & NLP

### Transformers & PhoBERT
- **transformers** `==4.35.2`
  - Hugging Face Transformers
  - **Sử dụng trong**: 
    - `custom_components/phobert_featurizer.py`
    - `rag/retriever.py`
    - `utils/download-phobert.py`

- **torch** `==2.1.2`
  - PyTorch deep learning framework
  - **Sử dụng trong**:
    - `custom_components/phobert_featurizer.py`
    - `rag/retriever.py`

- **tokenizers** `==0.15.0`
  - Fast tokenization library
  - **Sử dụng trong**: Transformers pipeline

- **sentencepiece** `==0.1.99`
  - Text tokenization
  - **Sử dụng trong**: PhoBERT tokenization

- **huggingface_hub** `==0.25.2`
  - Download models từ Hugging Face
  - **Sử dụng trong**:
    - `scripts/training/download_model.py`
    - `scripts/training/train_on_colab.py`
    - `scripts/training/colab_quick_train.py`

### Vector Search & Similarity
- **faiss-cpu** `==1.8.0.post1`
  - Facebook AI Similarity Search
  - **Sử dụng trong**: `rag/retriever.py` (RAG system)

### Numerical Computing
- **numpy** `==1.23.5`
  - **CRITICAL**: Must be < 1.24 for TensorFlow 2.12
  - **Sử dụng trong**:
    - `custom_components/phobert_featurizer.py`
    - `rag/retriever.py`
    - Rasa framework

---

## 🌐 3. LLM APIs & AI Services

### OpenAI
- **openai** `==1.48.0`
  - OpenAI API client
  - **Sử dụng trong**: `rag/retriever.py` (RAG synthesis)

### Groq
- **groq** `==0.9.0`
  - Groq API client (miễn phí, nhanh)
  - **Sử dụng trong**: `rag/retriever.py` (RAG synthesis)

### Google Gemini
- **google-generativeai** `==0.8.3`
  - Google Gemini API
  - **Sử dụng trong**: `rag/retriever.py` (RAG synthesis)

---

## 🖥️ 4. Desktop GUI (PySide6)

- **PySide6** `==6.7.2`
  - Qt framework cho desktop app
  - **Sử dụng trong**:
    - `ciesta/main.py`
    - `ciesta/views/login_view.py`
    - `ciesta/views/chat_view.py`
    - `ciesta/views/settings_view.py`
    - `ciesta/views/home.py`

---

## 🌍 5. Web Framework & API

### Flask
- **flask** `==3.0.3`
  - Web framework
  - **Sử dụng trong**: Rasa action server

- **flask-cors** `==5.0.0`
  - CORS support cho Flask
  - **Sử dụng trong**: Rasa action server

### HTTP Client
- **requests** `==2.32.3`
  - HTTP library
  - **Sử dụng trong**:
    - `ciesta/controllers/api_client.py`
    - `rag/retriever.py` (Hugging Face, Ollama APIs)
    - `utils/parse_test.py`

### Production Server
- **gunicorn** `==23.0.0`
  - WSGI HTTP Server
  - **Sử dụng trong**: Production deployment

---

## 📊 6. Data Processing

- **pandas** `==1.5.3`
  - Data manipulation và analysis
  - **Sử dụng trong**: 
    - Rasa framework
    - `utils/requirements-actions.txt`

---

## 🎨 7. Visualization

- **matplotlib** `==3.5.3`
  - Plotting library
  - **Sử dụng trong**: Data visualization (nếu cần)

- **seaborn** `==0.12.2`
  - Statistical data visualization
  - **Sử dụng trong**: Data visualization (nếu cần)

- **plotly** `==5.24.0`
  - Interactive plotting
  - **Sử dụng trong**: Data visualization (nếu cần)

---

## 🛠️ 8. Utilities

### Environment & Config
- **python-dotenv** `==1.0.1`
  - Load environment variables từ .env
  - **Sử dụng trong**:
    - `actions/actions.py`
    - `rag/retriever.py`

### Progress & Display
- **rich** `==13.8.1`
  - Rich text và beautiful terminal output
  - **Sử dụng trong**: Scripts và utilities

- **tqdm** `==4.66.5`
  - Progress bars
  - **Sử dụng trong**: Training scripts

### Text Processing
- **regex** `==2024.5.15`
  - Advanced regex
  - **Sử dụng trong**: 
    - `custom_components/vietnamese_preprocessor.py`
    - Rasa framework

---

## 🗄️ 9. Database

- **sqlalchemy** `==1.4.52`
  - SQL toolkit và ORM
  - **Sử dụng trong**: Rasa framework (nếu cần database)

---

## ✅ 10. Code Quality & Development

### Linting & Formatting
- **black** `==22.12.0`
  - Code formatter
  - **Sử dụng trong**: Development

- **isort** `==5.13.2`
  - Import sorter
  - **Sử dụng trong**: Development

- **ruff** `==0.6.5`
  - Fast Python linter
  - **Sử dụng trong**: Development

### Notebooks
- **jupyter** `==1.1.1`
  - Jupyter notebooks
  - **Sử dụng trong**: Development và analysis

- **ipykernel** `==6.29.5`
  - IPython kernel
  - **Sử dụng trong**: Jupyter notebooks

---

## 📝 11. JSON & Schema Validation

- **fastjsonschema** `==2.20.0`
  - Fast JSON schema validation
  - **Sử dụng trong**: Rasa framework

---

## 📦 12. Standard Library (Built-in)

Các thư viện Python standard library được sử dụng:

### File & System
- `os` - Operating system interface
- `sys` - System-specific parameters
- `pathlib` - Object-oriented filesystem paths
- `shutil` - High-level file operations
- `json` - JSON encoder/decoder
- `logging` - Logging facility

### Data Types & Utilities
- `typing` - Type hints
- `datetime` - Date và time utilities
- `time` - Time-related functions
- `subprocess` - Subprocess management
- `asyncio` - Asynchronous I/O
- `tempfile` - Temporary files
- `tarfile` - Tar archive support
- `re` - Regular expressions
- `unicodedata` - Unicode database
- `collections` - Specialized container datatypes

### Networking
- `urllib` - URL handling modules
- `http` - HTTP modules

---

## 🎯 13. Thư Viện Được Import Nhưng Không Có Trong requirements.txt

Các thư viện này được Rasa hoặc các thư viện khác tự động cài:

### Rasa Dependencies
- `spacy` - Được Rasa tự động cài
- `tensorflow` - Được Rasa tự động cài (version 2.12)
- `scikit-learn` - Được Rasa tự động cài
- `networkx` - Được Rasa tự động cài
- `pydantic` - Được Rasa tự động cài
- `pyyaml` - Được Rasa tự động cài
- `questionary` - Được Rasa tự động cài
- `ruamel.yaml` - Được Rasa tự động cài
- `boto3` - Được Rasa tự động cài (nếu cần AWS)
- `aiohttp` - Được Rasa tự động cài
- `sanic` - Được Rasa tự động cài
- `rocketchat_API` - Được Rasa tự động cài (nếu cần RocketChat)
- `python-telegram-bot` - Được Rasa tự động cài (nếu cần Telegram)

### Transformers Dependencies
- `safetensors` - Được Transformers tự động cài
- `packaging` - Được Transformers tự động cài
- `filelock` - Được Transformers tự động cài
- `huggingface-hub` - Đã có trong requirements.txt

### PyTorch Dependencies
- `filelock` - Được PyTorch tự động cài
- `networkx` - Được PyTorch tự động cài

---

## 📊 14. Phân Loại Theo Mục Đích Sử Dụng

### Core Dependencies (Bắt buộc)
1. `rasa` - Framework chính
2. `rasa-sdk` - Custom actions
3. `transformers` - PhoBERT model
4. `torch` - Deep learning
5. `numpy` - Numerical computing
6. `python-dotenv` - Environment variables

### ML/NLP Dependencies
1. `transformers` - Hugging Face models
2. `torch` - PyTorch
3. `tokenizers` - Tokenization
4. `sentencepiece` - Tokenization
5. `huggingface_hub` - Model download
6. `faiss-cpu` - Vector search
7. `numpy` - Numerical operations

### LLM API Dependencies (Optional)
1. `openai` - OpenAI API
2. `groq` - Groq API
3. `google-generativeai` - Gemini API
4. `requests` - HTTP requests (cho Ollama, Hugging Face)

### GUI Dependencies (Optional)
1. `PySide6` - Desktop GUI

### Web Dependencies
1. `flask` - Web framework
2. `flask-cors` - CORS support
3. `gunicorn` - Production server
4. `requests` - HTTP client

### Development Dependencies (Optional)
1. `black` - Code formatter
2. `isort` - Import sorter
3. `ruff` - Linter
4. `jupyter` - Notebooks
5. `ipykernel` - IPython kernel

### Utility Dependencies
1. `rich` - Terminal output
2. `tqdm` - Progress bars
3. `regex` - Advanced regex
4. `pandas` - Data processing
5. `matplotlib` - Visualization
6. `seaborn` - Visualization
7. `plotly` - Visualization

---

## 🔍 15. Cách Kiểm Tra Thư Viện Đã Cài

```bash
# Xem tất cả packages đã cài
pip list

# Xem packages từ requirements.txt
pip freeze

# Kiểm tra package cụ thể
pip show rasa
pip show transformers
pip show torch

# Kiểm tra dependencies của package
pip show rasa | grep -A 20 "Requires:"
```

---

## 📦 16. Cài Đặt Tất Cả Dependencies

```bash
# Cài đặt từ requirements.txt
pip install -r requirements.txt

# Hoặc cài đặt từng nhóm
pip install rasa rasa-sdk
pip install transformers torch tokenizers sentencepiece huggingface_hub
pip install faiss-cpu
pip install openai groq google-generativeai
pip install PySide6
pip install flask flask-cors gunicorn requests
pip install python-dotenv rich tqdm regex pandas
```

---

## ⚠️ 17. Lưu Ý Quan Trọng

### Version Constraints
- **numpy < 1.24**: Bắt buộc cho TensorFlow 2.12 (Rasa dependency)
- **Python 3.10**: Yêu cầu Python version
- **rasa 3.6.20**: Version đã test và hoạt động tốt

### Optional Dependencies
- **GUI (PySide6)**: Chỉ cần nếu chạy desktop app
- **LLM APIs**: Chỉ cần nếu sử dụng RAG synthesis
- **Development tools**: Chỉ cần trong development

### Size Considerations
- **PhoBERT-large**: ~1.5GB (được tải tự động)
- **PyTorch**: ~500MB
- **Rasa**: ~200MB
- **Tổng dung lượng**: ~3-4GB

---

## 📝 18. Thêm Thư Viện Mới

Khi thêm thư viện mới:

1. Cài đặt: `pip install package-name`
2. Thêm vào `requirements.txt`: `package-name==version`
3. Cập nhật file này với thông tin về thư viện mới
4. Test để đảm bảo không conflict với dependencies hiện tại

---

## 🔗 19. Links Hữu Ích

- [Rasa Documentation](https://rasa.com/docs/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)

---

**Cập nhật lần cuối**: 2025-11-08
**Python Version**: 3.10
**Total Packages**: 35+ chính + dependencies tự động

