# 🚀 Setup Google Colab - Hướng Dẫn Nhanh

## ⚠️ Lưu ý Quan Trọng

**Tên thư mục sau khi clone là `ciesta-assistant` (không phải `ciesta-asisstant`)**

---

## 📋 Các Bước Setup

### Bước 1: Clone Repository

```python
# Clone repo
!git clone https://github.com/HoangPhucDE/ciesta-assistant.git
```

### Bước 2: Chuyển vào thư mục

```python
# Chuyển vào thư mục project
%cd ciesta-assistant

# Kiểm tra đã vào đúng thư mục chưa
!pwd
!ls -la
```

### Bước 3: Chạy Training

```python
# Chạy script training tự động
!python scripts/training/train_on_colab.py
```

---

## 🔧 Setup Tự Động (Copy toàn bộ)

```python
# ============================================
# SETUP TỰ ĐỘNG CHO GOOGLE COLAB
# ============================================

# Bước 1: Clone repository
import os
if not os.path.exists("ciesta-assistant"):
    !git clone https://github.com/HoangPhucDE/ciesta-assistant.git
    print("✅ Đã clone repository")
else:
    print("✅ Repository đã tồn tại")

# Bước 2: Chuyển vào thư mục
%cd ciesta-assistant
print(f"✅ Đã chuyển vào: {os.getcwd()}")

# Bước 3: Kiểm tra files
import os
required_files = [
    "config.yml",
    "data/nlu.yml",
    "custom_components/phobert_featurizer.py",
    "requirements.txt"
]

missing = []
for file in required_files:
    if os.path.exists(file):
        print(f"✅ {file}")
    else:
        print(f"❌ {file} - KHÔNG TÌM THẤY")
        missing.append(file)

if missing:
    print(f"\n⚠ Thiếu các file: {', '.join(missing)}")
else:
    print("\n✅ Tất cả files cần thiết đã có!")
    print("\nBước tiếp theo: Chạy script training")
    print("!python scripts/training/train_on_colab.py")
```

---

## 🐛 Troubleshooting

### Lỗi: "No such file or directory: 'ciesta-asisstant'"

**Nguyên nhân:** Tên thư mục sai (có chữ 's' thừa)

**Giải pháp:**
```python
# Sửa lại tên thư mục đúng
%cd ciesta-assistant  # Đúng (không có 's' thừa)
```

### Lỗi: "fatal: destination path 'ciesta-assistant' already exists"

**Nguyên nhân:** Đã clone rồi

**Giải pháp:**
```python
# Chỉ cần chuyển vào thư mục
%cd ciesta-assistant
```

### Kiểm tra thư mục hiện tại

```python
# Xem thư mục hiện tại
import os
print(f"Thư mục hiện tại: {os.getcwd()}")

# Xem các thư mục có sẵn
!ls -la
```

---

## ✅ Checklist

- [ ] Đã clone repository thành công
- [ ] Đã chuyển vào thư mục `ciesta-assistant`
- [ ] Đã kiểm tra files cần thiết
- [ ] Đã chạy script training

---

## 🔗 Xem thêm

- [QUICK_START_COLAB.md](QUICK_START_COLAB.md) - Hướng dẫn nhanh
- [README_COLAB.md](README_COLAB.md) - Hướng dẫn chi tiết
- [colab_notebook.ipynb](colab_notebook.ipynb) - Notebook sẵn

