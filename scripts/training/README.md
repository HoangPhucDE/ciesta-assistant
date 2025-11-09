# Training Scripts

Thư mục này chứa các scripts và tài liệu liên quan đến training Rasa NLU model.

## 📁 Cấu Trúc Thư Mục

```
scripts/training/
├── train_on_colab.py          # Script chính để train trên Google Colab
├── sync_location_names.py      # Script đồng bộ location names với knowledge base
├── utils/                      # Utility scripts
│   ├── check_nlu_warnings.py  # Kiểm tra warnings trong nlu.yml
│   ├── check_entity_warnings.py
│   ├── check_training_setup.py
│   └── download_model.py
├── docs/                       # Tài liệu
│   ├── README_SYNC_LOCATIONS.md
│   ├── README_COLAB.md
│   ├── COLAB_COPY_PASTE.md
│   └── ...
└── archive/                    # Các script cũ (deprecated)
    ├── colab_setup_train.py
    ├── fix_entity_alignments.py
    └── ...
```

## 🚀 Quick Start

### 1. Đồng bộ Location Names

Trước khi train, đồng bộ location names với knowledge base:

```bash
python3 scripts/training/sync_location_names.py
```

### 2. Kiểm tra Warnings

Kiểm tra xem có warnings không:

```bash
python3 scripts/training/utils/check_nlu_warnings.py
```

### 3. Train trên Colab

Chạy script train trên Google Colab:

```bash
python3 scripts/training/train_on_colab.py
```

Hoặc copy-paste từ file `docs/COLAB_COPY_PASTE.md`

## 📚 Tài Liệu

- **README_SYNC_LOCATIONS.md**: Hướng dẫn đồng bộ location names
- **README_COLAB.md**: Hướng dẫn train trên Colab
- **COLAB_COPY_PASTE.md**: Copy-paste nhanh cho Colab
- **REPORT_NLU_CHECK.md**: Báo cáo kiểm tra nlu.yml

## 🔧 Utility Scripts

- **check_nlu_warnings.py**: Kiểm tra warnings trong nlu.yml
- **check_entity_warnings.py**: Kiểm tra entity warnings
- **check_training_setup.py**: Kiểm tra setup training
- **download_model.py**: Download model từ Colab

## 📦 Archive

Thư mục `archive/` chứa các script cũ đã được thay thế:
- `colab_setup_train.py` → đã merge vào `train_on_colab.py`
- `fix_entity_alignments.py` → đã thay bằng `sync_location_names.py`
- Các script khác đã deprecated

## 🔄 Workflow

1. **Sync location names**: `python3 scripts/training/sync_location_names.py`
2. **Check warnings**: `python3 scripts/training/utils/check_nlu_warnings.py`
3. **Train model**: `python3 scripts/training/train_on_colab.py`

## 📝 Lưu Ý

- Luôn chạy `sync_location_names.py` trước khi train
- Kiểm tra warnings sau khi sync
- Sử dụng `train_on_colab.py` làm script chính để train trên Colab
- Các script cũ đã được di chuyển vào `archive/` (deprecated)

## 📖 Xem Thêm

- **INDEX.md**: Index đầy đủ các file trong thư mục
- **STRUCTURE.md**: Cấu trúc chi tiết thư mục
- **archive/README.md**: Thông tin về các script deprecated
- **docs/**: Tất cả tài liệu hướng dẫn (13 files)

