# Đồng Bộ Location Names trong NLU Training Data

## Mục đích

Script `sync_location_names.py` được tạo để đồng bộ tất cả location entity names trong `data/nlu.yml` với tên chính thức từ knowledge base (`data/knowledge_base/provinces/`).

## Vì sao cần đồng bộ?

- **Tên chính thức**: Knowledge base sử dụng tên chính thức của các tỉnh thành (ví dụ: "Hồ Chí Minh", "Hà Nội", "Đà Nẵng")
- **Alias trong training data**: Training data có thể sử dụng các alias (ví dụ: "TP.HCM", "HCM", "Sài Gòn", "Sai Gon")
- **Vấn đề**: Rasa sẽ báo warning về misaligned entities nếu entity value không khớp với text thực tế
- **Giải pháp**: Đồng bộ tất cả location entities về tên chính thức, alias sẽ được xử lý ở action layer

## Cách sử dụng

### 1. Chạy script để đồng bộ

```bash
python3 scripts/training/sync_location_names.py
```

### 2. Script sẽ:

1. **Load provinces** từ `data/knowledge_base/provinces/*.json`
   - Đọc tên chính thức từ key của JSON object
   - Ví dụ: `{"Hồ Chí Minh": {...}}` → tên chính thức: "Hồ Chí Minh"

2. **Tạo alias mapping**
   - Map các alias về tên chính thức
   - Ví dụ:
     - `TP.HCM` → `Hồ Chí Minh`
     - `HCM` → `Hồ Chí Minh`
     - `Sài Gòn` → `Hồ Chí Minh`
     - `Sai Gon` → `Hồ Chí Minh`
     - `Hanoi` → `Hà Nội`
     - `Da Nang` → `Đà Nẵng`
     - etc.

3. **Đồng bộ nlu.yml**
   - Tìm tất cả entity annotations `[alias](location)` trong `data/nlu.yml`
   - Thay thế bằng `[tên_chính_thức](location)`
   - Tự động backup file gốc thành `data/nlu.yml.bak`

### 3. Kết quả

- File `data/nlu.yml` được cập nhật với tên chính thức
- File backup `data/nlu.yml.bak` được tạo tự động
- Tất cả location entities đã được đồng bộ

## Ví dụ

### Trước khi đồng bộ:
```yaml
- văn hóa [TP.HCM](location) có gì đặc sắc
- hãy kể về văn hóa [Sài Gòn](location)
- giới thiệu về văn hóa [TP.HCM](location)
```

### Sau khi đồng bộ:
```yaml
- văn hóa [Hồ Chí Minh](location) có gì đặc sắc
- hãy kể về văn hóa [Hồ Chí Minh](location)
- giới thiệu về văn hóa [Hồ Chí Minh](location)
```

## Alias Handling

- **Training data**: Chỉ sử dụng tên chính thức
- **Action layer**: Xử lý alias mapping
  - Ví dụ: Khi user nhập "TP.HCM" hoặc "HCM", action sẽ map về "Hồ Chí Minh" để query knowledge base

## Lưu ý

1. **Chạy script trước khi train**: Luôn chạy script này trước khi train model để đảm bảo training data đúng
2. **Backup tự động**: Script tự động tạo backup file, không cần lo về việc mất dữ liệu
3. **Chỉ fix location entities**: Script chỉ fix các entities có type là `location`
4. **Case-insensitive matching**: Script hỗ trợ case-insensitive matching (ví dụ: "hcm" → "Hồ Chí Minh")

## Workflow

1. **Thêm training data mới** với location entities (có thể dùng alias)
2. **Chạy sync script** để đồng bộ về tên chính thức
3. **Train model** với `train_on_colab.py`
4. **Action layer** xử lý alias mapping khi user query

## Kiểm tra sau khi sync

Sau khi chạy `sync_location_names.py`, chạy script kiểm tra:

```bash
python3 scripts/training/check_nlu_warnings.py
```

Script này sẽ:
- Kiểm tra entities có trong knowledge base không
- Kiểm tra entities có format đúng không
- Kiểm tra entities có thể gây warning không
- Báo cáo các vấn đề cần fix

## Troubleshooting

### Script không tìm thấy provinces
- Kiểm tra `data/knowledge_base/provinces/` có tồn tại không
- Đảm bảo các file JSON có format đúng: `{"Tên Tỉnh": {...}}`

### Một số alias không được map
- Thêm alias vào hàm `create_alias_mapping()` trong script
- Đảm bảo alias mapping đúng với tên chính thức trong knowledge base

### File nlu.yml không được cập nhật
- Kiểm tra quyền ghi file
- Kiểm tra đường dẫn file đúng không
- Xem log để biết lỗi cụ thể

### Entities không có trong knowledge base
- Một số entities như "Đà Lạt", "Phú Quốc", "Hội An", "Nha Trang", "Sapa", "Hạ Long" là tên thành phố/địa danh con, không phải tỉnh
- Các entities này vẫn có thể được sử dụng trong training data
- Action layer sẽ xử lý mapping đến tỉnh tương ứng (ví dụ: "Đà Lạt" → "Lâm Đồng")

