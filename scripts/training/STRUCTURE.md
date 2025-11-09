# Cấu Trúc Thư Mục Training

## 📁 Tổng Quan

```
scripts/training/
├── README.md                    # Tài liệu chính
├── INDEX.md                     # Index đầy đủ các file
├── STRUCTURE.md                 # File này
│
├── train_on_colab.py            # ⭐ Script chính để train trên Colab
├── sync_location_names.py       # ⭐ Đồng bộ location names với KB
│
├── utils/                       # Utility scripts
│   ├── check_nlu_warnings.py   # Kiểm tra warnings trong nlu.yml
│   ├── check_entity_warnings.py
│   ├── check_training_setup.py
│   └── download_model.py
│
├── docs/                        # Tài liệu
│   ├── README_SYNC_LOCATIONS.md
│   ├── README_COLAB.md
│   ├── COLAB_COPY_PASTE.md
│   ├── FIX_COLAB.md
│   ├── FIX_GPU_ISSUE.md
│   └── ... (10 files khác)
│
└── archive/                     # Scripts cũ (deprecated)
    ├── README.md
    ├── colab_setup_train.py
    ├── fix_entity_alignments.py
    └── ... (8 files khác)
```

## 🎯 Scripts Chính

### train_on_colab.py
- **Mục đích**: Script chính để train Rasa NLU model trên Google Colab
- **Tính năng**:
  - Tự động setup môi trường (Python 3.10, dependencies)
  - Download PhoBERT model
  - Tối ưu config cho GPU
  - Train NLU model với progress display
  - Download model về máy local

### sync_location_names.py
- **Mục đích**: Đồng bộ location names trong nlu.yml với knowledge base
- **Tính năng**:
  - Load provinces từ KB
  - Map alias về tên chính thức
  - Fix format issues (typo, thiếu dấu)
  - Backup file gốc

## 🔧 Utility Scripts

### check_nlu_warnings.py
- Kiểm tra warnings trong nlu.yml
- Kiểm tra entities có trong KB không
- Kiểm tra format issues
- Báo cáo potential warnings

### check_entity_warnings.py
- Kiểm tra entity warnings chi tiết

### check_training_setup.py
- Kiểm tra setup training environment

### download_model.py
- Download model từ Colab về máy local

## 📚 Documentation

### Hướng Dẫn Chính
- **README_SYNC_LOCATIONS.md**: Hướng dẫn đồng bộ location names
- **README_COLAB.md**: Hướng dẫn train trên Colab
- **COLAB_COPY_PASTE.md**: Copy-paste nhanh cho Colab

### Troubleshooting
- **FIX_COLAB.md**: Fix các lỗi trên Colab
- **FIX_GPU_ISSUE.md**: Fix các lỗi GPU
- **COLAB_FIX_INSTALL.md**: Fix lỗi cài đặt

### Guides
- **COLAB_SETUP.md**: Setup Colab
- **COLAB_SIMPLE_GUIDE.md**: Hướng dẫn đơn giản
- **QUICK_START_COLAB.md**: Quick start
- **README_LOCAL_TRAINING.md**: Train local

### Reports
- **REPORT_NLU_CHECK.md**: Báo cáo kiểm tra nlu.yml

## 📦 Archive

Thư mục `archive/` chứa các script cũ đã deprecated:
- Các script đã được thay thế bởi script mới
- Không được maintain
- Chỉ để tham khảo

Xem chi tiết trong `archive/README.md`

## 🔄 Workflow

1. **Sync location names**: `python3 scripts/training/sync_location_names.py`
2. **Check warnings**: `python3 scripts/training/utils/check_nlu_warnings.py`
3. **Train model**: `python3 scripts/training/train_on_colab.py`

## 📊 Thống Kê

- **Main scripts**: 2
- **Utility scripts**: 4
- **Documentation files**: 13
- **Archive files**: 10
- **Tổng cộng**: 29 files
