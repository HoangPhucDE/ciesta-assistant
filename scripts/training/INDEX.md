# Training Scripts Index

## 📋 Quick Reference

### Main Scripts (Root)
- **train_on_colab.py** - Script chính để train trên Google Colab
- **sync_location_names.py** - Đồng bộ location names với knowledge base

### Utility Scripts (utils/)
- **check_nlu_warnings.py** - Kiểm tra warnings trong nlu.yml
- **check_entity_warnings.py** - Kiểm tra entity warnings
- **check_training_setup.py** - Kiểm tra setup training
- **download_model.py** - Download model từ Colab

### Documentation (docs/)

#### Hướng Dẫn Chính
- **README_SYNC_LOCATIONS.md** - Hướng dẫn đồng bộ location names
- **README_COLAB.md** - Hướng dẫn train trên Colab
- **COLAB_COPY_PASTE.md** - Copy-paste nhanh cho Colab

#### Troubleshooting
- **FIX_COLAB.md** - Fix các lỗi trên Colab
- **FIX_GPU_ISSUE.md** - Fix các lỗi GPU
- **COLAB_FIX_INSTALL.md** - Fix lỗi cài đặt

#### Guides
- **COLAB_SETUP.md** - Setup Colab
- **COLAB_SIMPLE_GUIDE.md** - Hướng dẫn đơn giản
- **QUICK_START_COLAB.md** - Quick start
- **README_LOCAL_TRAINING.md** - Train local
- **README_FIX_ENTITIES.md** - Fix entities (deprecated, xem README_SYNC_LOCATIONS.md)

#### Reports
- **REPORT_NLU_CHECK.md** - Báo cáo kiểm tra nlu.yml

### Archive (archive/)
Các script cũ đã deprecated:
- **colab_setup_train.py** → `train_on_colab.py`
- **fix_entity_alignments.py** → `sync_location_names.py`
- **fix_entity_alignments_rasa.py** → `sync_location_names.py`
- **fix_entity_warnings.py** → `utils/check_nlu_warnings.py`
- **colab_optimize_gpu.py** → `train_on_colab.py`
- **colab_quick_train.py** → `train_on_colab.py`
- **colab_train_simple.py** → `train_on_colab.py`
- **fix_pytorch_cuda.py** → `train_on_colab.py`
- **fix_pytorch_cuda.sh** → `train_on_colab.py`
- **colab_notebook.ipynb** → `train_on_colab.py` + `docs/COLAB_COPY_PASTE.md`

## 🔍 Tìm Kiếm Nhanh

### Train trên Colab
→ `train_on_colab.py` hoặc `docs/COLAB_COPY_PASTE.md`

### Đồng bộ location names
→ `sync_location_names.py` hoặc `docs/README_SYNC_LOCATIONS.md`

### Kiểm tra warnings
→ `utils/check_nlu_warnings.py`

### Fix lỗi Colab
→ `docs/FIX_COLAB.md` hoặc `docs/FIX_GPU_ISSUE.md`

### Download model
→ `utils/download_model.py`

## 📊 Thống Kê

- **Main scripts**: 2
- **Utility scripts**: 4
- **Documentation files**: 13
- **Archive files**: 10

