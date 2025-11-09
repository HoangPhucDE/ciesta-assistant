# Archive - Deprecated Scripts

Thư mục này chứa các script cũ đã được thay thế hoặc deprecated.

## 📦 Các Script Đã Deprecated

### colab_setup_train.py
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py`
- **Lý do**: Đã merge tất cả tính năng vào `train_on_colab.py`

### fix_entity_alignments.py
- **Status**: Deprecated
- **Thay thế bởi**: `sync_location_names.py`
- **Lý do**: Phương pháp mới đơn giản hơn, chỉ đồng bộ với knowledge base

### fix_entity_alignments_rasa.py
- **Status**: Deprecated
- **Thay thế bởi**: `sync_location_names.py`
- **Lý do**: Phương pháp mới đơn giản hơn

### fix_entity_warnings.py
- **Status**: Deprecated
- **Thay thế bởi**: `utils/check_nlu_warnings.py`
- **Lý do**: Tích hợp vào script kiểm tra tổng quát

### colab_optimize_gpu.py
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py` (có hàm `optimize_config_for_gpu()`)
- **Lý do**: Đã tích hợp vào script chính

### colab_quick_train.py
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py`
- **Lý do**: Đã tích hợp vào script chính

### colab_train_simple.py
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py`
- **Lý do**: Đã tích hợp vào script chính

### fix_pytorch_cuda.py / fix_pytorch_cuda.sh
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py` (tự động xử lý)
- **Lý do**: Đã tích hợp vào script chính

### colab_notebook.ipynb
- **Status**: Deprecated
- **Thay thế bởi**: `train_on_colab.py` + `docs/COLAB_COPY_PASTE.md`
- **Lý do**: Script Python dễ maintain hơn notebook

## 🔄 Migration Guide

Nếu bạn đang sử dụng các script cũ, vui lòng migrate sang:

1. **colab_setup_train.py** → `train_on_colab.py`
2. **fix_entity_alignments.py** → `sync_location_names.py`
3. **check_entity_warnings.py** → `utils/check_nlu_warnings.py`
4. **colab_optimize_gpu.py** → `train_on_colab.py` (tự động)

## 📝 Lưu Ý

- Các script trong thư mục này **KHÔNG được maintain**
- Không sử dụng các script này cho production
- Sử dụng các script mới trong thư mục gốc và `utils/`

