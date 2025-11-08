# ⚡ Copy-Paste Nhanh cho Google Colab

## 🚀 Setup và Train (Copy toàn bộ vào một cell)

```python
# ============================================
# SETUP VÀ TRAIN TỰ ĐỘNG - COPY TOÀN BỘ
# ============================================

import os

# Bước 1: Clone repository
if not os.path.exists("ciesta-assistant"):
    print("📦 Đang clone repository...")
    !git clone https://github.com/HoangPhucDE/ciesta-assistant.git
    print("✅ Đã clone repository thành công")
else:
    print("✅ Repository đã tồn tại")

# Bước 2: Chuyển vào thư mục (QUAN TRỌNG: tên là ciesta-assistant)
%cd ciesta-assistant
print(f"✅ Đã chuyển vào: {os.getcwd()}")

# Bước 3: Kiểm tra files
print("\n📋 Kiểm tra files:")
files_ok = True
for file in ["config.yml", "data/nlu.yml", "custom_components/phobert_featurizer.py", "requirements.txt"]:
    if os.path.exists(file):
        print(f"  ✅ {file}")
    else:
        print(f"  ❌ {file}")
        files_ok = False

if not files_ok:
    print("\n⚠ Thiếu files! Vui lòng kiểm tra lại.")
else:
    print("\n✅ Tất cả files OK!")
    print("\n🚀 Bắt đầu training...\n")
    
    # Chạy script training
    !python scripts/training/train_on_colab.py
```

---

## 📋 Chỉ Setup (Không train)

```python
# Setup repository
import os

if not os.path.exists("ciesta-assistant"):
    !git clone https://github.com/HoangPhucDE/ciesta-assistant.git

%cd ciesta-assistant
print(f"✅ Thư mục hiện tại: {os.getcwd()}")
```

---

## 🎯 Chỉ Train (Sau khi đã setup)

```python
# Train model
%cd ciesta-assistant
!python scripts/training/train_on_colab.py
```

---

## ⚠️ Lưu Ý

1. **Tên thư mục:** `ciesta-assistant` (không phải `ciesta-asisstant`)
2. **Nếu đã clone:** Chỉ cần `%cd ciesta-assistant`
3. **Nếu lỗi:** Xem [COLAB_SETUP.md](COLAB_SETUP.md) để troubleshooting

---

## 🔧 Troubleshooting Nhanh

### Lỗi: "No such file or directory: 'ciesta-asisstant'"
```python
# Sửa thành:
%cd ciesta-assistant  # Đúng (không có 's' thừa)
```

### Lỗi: "fatal: destination path 'ciesta-assistant' already exists"
```python
# Chỉ cần chuyển vào thư mục:
%cd ciesta-assistant
```

### Kiểm tra thư mục hiện tại
```python
import os
print(os.getcwd())
!ls -la
```

