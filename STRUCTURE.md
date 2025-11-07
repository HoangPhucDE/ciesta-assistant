# 📁 Cấu trúc thư mục dự án Ciesta

## Cấu trúc đề xuất

```
ciesta-asisstant/
├── README.md                    # Tài liệu chính
├── LICENSE                      # License
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (không commit)
│
├── config/                      # Cấu hình
│   └── rasa/                    # Rasa configuration
│       ├── config.yml           # Pipeline config
│       ├── domain.yml           # Domain definition
│       ├── endpoints.yml        # Endpoints config
│       └── credentials.yml     # Channel credentials
│
├── data/                        # Dữ liệu training và knowledge base
│   ├── nlu.yml                  # NLU training data
│   ├── rules.yml                # Rules
│   ├── stories.yml              # Stories
│   ├── location_map.json        # Location alias mapping
│   ├── knowledge_base/          # Knowledge base
│   │   └── provinces/          # 34 tỉnh thành JSON files
│   └── lookup/                 # Lookup tables
│       ├── locations.yml
│       └── lookup.yml
│
├── actions/                     # Custom actions
│   ├── __init__.py
│   └── actions.py              # Main actions file
│
├── custom_components/          # Custom Rasa components
│   ├── __init__.py
│   ├── entity_filter.py
│   ├── phobert_featurizer.py
│   └── vietnamese_preprocessor.py
│
├── rag/                        # RAG system
│   ├── __init__.py
│   └── retriever.py           # FAISS + LLM retriever
│
├── ciesta/                     # Desktop application
│   ├── main.py                # Entry point
│   ├── utils.py               # Utilities
│   ├── controllers/           # API client
│   │   └── api_client.py
│   ├── views/                 # UI views
│   │   ├── login_view.py
│   │   ├── chat_view.py
│   │   ├── home.py
│   │   └── settings_view.py
│   ├── styles/                # QSS stylesheets
│   │   └── styles.qss
│   └── core/                  # Core logic (nếu có)
│
├── scripts/                    # Utility scripts
│   ├── training/              # Training scripts
│   │   └── download_model.py
│   ├── validation/           # Validation scripts
│   │   └── validate_knowledge_base.py
│   └── debug/                # Debug scripts
│       ├── debug_rag.py
│       └── test_env_loading.py
│
├── utils/                      # Shared utilities (có thể được import)
│   ├── config_PhoBERT.yml
│   ├── config-pipeline.yml
│   ├── docker-compose.yml
│   ├── Dockerfile.rasa
│   └── ...
│
├── docs/                       # Documentation
│   ├── guides/                # Hướng dẫn
│   │   ├── TRAIN_MODEL.md
│   │   ├── LLM_SETUP.md
│   │   ├── NGROK_SETUP.md
│   │   └── FREE_LLM_API_GUIDE.md
│   ├── troubleshooting/       # Xử lý lỗi
│   │   ├── DEBUG_RAG.md
│   │   ├── QUICK_FIX_RAG.md
│   │   ├── CHECK_ACTION_SERVER.md
│   │   └── TROUBLESHOOTING_RAG.md
│   └── api/                   # API documentation
│
├── models/                     # Trained models
│   └── *.tar.gz
│
├── models_hub/                # Downloaded models
│   ├── phobert-large/
│   └── phobert_cache/
│
├── tests/                      # Tests
│   └── test_stories.yml
│
├── .venv/                     # Virtual environment (không commit)
├── .rasa/                     # Rasa cache (không commit)
└── .git/                      # Git repository
```

## Lợi ích của cấu trúc mới

### 1. Tổ chức rõ ràng
- **scripts/**: Tất cả script tiện ích ở một nơi
- **docs/**: Tài liệu được phân loại theo mục đích
- **config/**: Config Rasa được tập trung

### 2. Dễ bảo trì
- Dễ tìm file cần thiết
- Dễ thêm file mới vào đúng chỗ
- Dễ quản lý version

### 3. Tuân thủ best practices
- Tách biệt code, config, docs
- Dễ deploy và chia sẻ

## Cách sử dụng

### Chạy script cấu trúc lại:
```bash
chmod +x reorganize_structure.sh
./reorganize_structure.sh
```

### Hoặc thủ công:
1. Tạo các thư mục mới
2. Di chuyển file theo cấu trúc trên
3. Tạo symlink cho Rasa config (nếu cần)

## Lưu ý

- **Symlink cho Rasa config**: Rasa tìm config ở root, nên cần symlink từ `config/rasa/` về root
- **Import paths**: Đảm bảo các import vẫn hoạt động sau khi di chuyển
- **Git**: Commit sau khi cấu trúc lại để tránh mất file

## Migration checklist

- [ ] Backup project trước khi cấu trúc lại
- [ ] Chạy script hoặc di chuyển file thủ công
- [ ] Kiểm tra các import vẫn hoạt động
- [ ] Test Rasa vẫn chạy được
- [ ] Test action server vẫn chạy được
- [ ] Test desktop app vẫn chạy được
- [ ] Update README với cấu trúc mới
- [ ] Commit changes

