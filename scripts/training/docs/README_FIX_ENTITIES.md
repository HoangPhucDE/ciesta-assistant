# Hướng dẫn Fix Entity Alignment Warnings

## Vấn đề

Khi train Rasa NLU model, bạn có thể gặp warnings về entity alignment:
```
Misaligned entity annotation in message '...'. 
Make sure the start and end values of entities in the training data match the token boundaries (e.g. start and end are set to 0 and 4 if the entity is the first token and has 4 characters).
```

## Nguyên nhân

Entity annotations không khớp với token boundaries sau khi tokenize:
- Entity value có thể không match với text thực tế (ví dụ: "TP.HCM" vs "thành phố hcm")
- Entity boundaries không khớp với token boundaries (ví dụ: entity bắt đầu ở giữa token)
- Punctuation trong entity annotations (ví dụ: "Đà Nẵng," thay vì "Đà Nẵng")

## Giải pháp

### Cách 1: Sử dụng Rasa's validation tool

```bash
# Validate training data
rasa data validate

# Hoặc chỉ validate NLU
rasa data validate nlu
```

Rasa sẽ báo các warnings về entity alignment. Sau đó bạn có thể fix thủ công.

### Cách 2: Sử dụng script tự động fix

```bash
# Chạy script fix entity alignments
python scripts/training/fix_entity_alignments.py data/nlu.yml

# Script sẽ:
# 1. Backup file gốc (data/nlu.yml.bak)
# 2. Fix entity alignments để khớp với token boundaries
# 3. Loại bỏ punctuation từ entity annotations
# 4. Ghi lại file đã fix
```

### Cách 3: Fix thủ công

1. **Tìm examples có vấn đề:**
   - Chạy `rasa data validate` để xem warnings
   - Tìm các examples có entity value không match với text

2. **Fix entity annotations:**
   - Đảm bảo entity value khớp với text thực tế
   - Loại bỏ punctuation từ entity annotations
   - Đảm bảo entity boundaries khớp với token boundaries

3. **Ví dụ fix:**

   **Trước:**
   ```yaml
   - văn hóa [TP.HCM](location) có gì đặc sắc
   ```

   **Sau (nếu text thực tế là "thành phố hcm"):**
   ```yaml
   - văn hóa thành phố [hcm](location) có gì đặc sắc
   ```

   **Hoặc nếu text thực tế là "TP.HCM":**
   ```yaml
   - văn hóa [TP.HCM](location) có gì đặc sắc
   ```

## Lưu ý

1. **Backup file trước khi fix:**
   - Script tự động backup file gốc
   - Nếu có vấn đề, có thể restore từ backup

2. **Kiểm tra lại sau khi fix:**
   ```bash
   rasa data validate nlu
   ```

3. **Train lại model:**
   ```bash
   rasa train nlu
   ```

## Scripts có sẵn

1. **fix_entity_alignments.py**: Script chính để fix entity alignments
2. **fix_entity_warnings.py**: Script sử dụng Rasa API để validate và fix
3. **fix_entity_alignments_rasa.py**: Script sử dụng Rasa tokenizer

## Troubleshooting

### Script không fix được gì

- Có thể entity annotations đã đúng format
- Hoặc logic của script chưa cover được các cases
- Thử sử dụng `rasa data validate` để xem warnings cụ thể

### Entity value không match với text

- Đây là vấn đề về data quality
- Cần fix thủ công hoặc cập nhật training data
- Đảm bảo entity value khớp với text thực tế trong examples

### Warnings vẫn còn sau khi fix

- Có thể cần train lại model để Rasa tự động fix
- Hoặc có các cases đặc biệt cần fix thủ công
- Kiểm tra lại bằng `rasa data validate`

