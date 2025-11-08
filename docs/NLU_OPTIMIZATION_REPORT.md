# 📊 Báo Cáo Tối Ưu NLU - Ciesta Assistant

## 📈 Thống Kê Hiện Tại

- **Tổng số dòng**: 1,750
- **Tổng số examples**: 1,696
- **Số intent**: 16
- **Số tỉnh được bao phủ**: 34 tỉnh thành

## ⚠️ Các Vấn Đề Cần Tối Ưu

### 1. 🔴 **Examples Trùng Lặp** (Ưu tiên cao)

**Vấn đề**: Tìm thấy **16 examples bị trùng lặp hoàn toàn**

**Các examples trùng lặp:**
- `ẩm thực [Hà Nội](location)` - xuất hiện 2 lần
- `ẩm thực [Đà Nẵng](location)` - xuất hiện 2 lần
- `ẩm thực [Huế](location)` - xuất hiện 2 lần
- `ẩm thực [Hải Phòng](location)` - xuất hiện 2 lần
- `ẩm thực [Cần Thơ](location)` - xuất hiện 2 lần
- `thôi` - xuất hiện 2 lần (trong `deny` và `goodbye`)
- `dừng lại` - xuất hiện 2 lần (trong `deny` và `goodbye`)
- `bạn là gì vậy` - xuất hiện 2 lần
- `bạn là ai vậy` - xuất hiện 2 lần
- `[Huế](location) có lễ hội gì` - xuất hiện 2 lần

**Tác động**: 
- Lãng phí tài nguyên training
- Có thể gây overfitting
- Không cải thiện độ chính xác

**Giải pháp**: 
- Xóa các examples trùng lặp
- Giữ lại 1 bản duy nhất cho mỗi example

### 2. 🟡 **Phân Bố Examples Không Đều** (Ưu tiên trung bình)

**Vấn đề**: Phân bố examples giữa các intent không cân bằng

**Phân bố hiện tại:**
- `ask_culture`: 308 examples (18.2%)
- `ask_new_province`: 243 examples (14.3%)
- `ask_cuisine`: 225 examples (13.3%)
- `ask_travel_tips`: 223 examples (13.2%)
- `ask_attractions`: 219 examples (12.9%)
- `ask_transportation`: 145 examples (8.6%)
- `ask_festival`: 105 examples (6.2%) ⚠️ **Thiếu**
- `out_of_scope`: 66 examples (3.9%)
- `goodbye`: 42 examples (2.5%)
- `inform_location`: 33 examples (1.9%)
- `greet`: 24 examples (1.4%)
- `bot_challenge`: 22 examples (1.3%)
- `affirm`: 12 examples (0.7%)
- `deny`: 10 examples (0.6%)
- `mood_great`: 9 examples (0.5%)
- `mood_unhappy`: 9 examples (0.5%)

**Tác động**:
- Intent có ít examples có thể bị nhận diện kém
- Model có thể bias về các intent có nhiều examples

**Giải pháp**:
- Thêm examples cho `ask_festival` (mục tiêu: 150-180 examples)
- Thêm examples cho `ask_transportation` (mục tiêu: 180-200 examples)
- Cân bằng các intent chính (mục tiêu: 200-250 examples/intent)

### 3. 🟡 **Patterns Có Thể Gây Nhầm Lẫn** (Ưu tiên trung bình)

**Vấn đề**: Một số patterns xuất hiện ở nhiều intent khác nhau

**Các patterns gây nhầm lẫn:**
1. `thôi` - xuất hiện ở `deny` và `goodbye`
2. `dừng lại` - xuất hiện ở `deny` và `goodbye`
3. `địa điểm [LOCATION]` - xuất hiện ở `ask_attractions` và `inform_location`

**Tác động**:
- Model có thể nhầm lẫn giữa các intent
- Cần thêm context để phân biệt

**Giải pháp**:
- Thêm examples với context rõ ràng hơn
- Ví dụ: "thôi, không cần" → `deny`, "thôi, tạm biệt" → `goodbye`
- Ví dụ: "địa điểm tham quan [LOCATION]" → `ask_attractions`, "địa điểm [LOCATION]" → `inform_location`

### 4. 🟢 **Thiếu Examples Cho Các Tỉnh Còn Lại** (Ưu tiên thấp)

**Vấn đề**: Một số tỉnh chỉ có examples cơ bản, chưa có đủ biến thể

**Các tỉnh cần bổ sung:**
- Cao Bằng, Điện Biên, Lai Châu, Sơn La, Tuyên Quang
- Hà Tĩnh, Quảng Trị, Đồng Nai, Tây Ninh, Đồng Tháp
- Cà Mau, Gia Lai, Đắk Lắk, Lâm Đồng, Quảng Ngãi
- Nghệ An, Thanh Hóa, Phú Thọ, Hưng Yên, Thái Nguyên

**Giải pháp**:
- Thêm các biến thể ngôn ngữ cho các tỉnh này
- Thêm các câu hỏi tự nhiên tương tự như các tỉnh chính

### 5. 🟢 **Thiếu Examples Với Context Phức Tạp** (Ưu tiên thấp)

**Vấn đề**: Hầu hết examples là câu hỏi đơn giản, thiếu context

**Ví dụ thiếu:**
- "Tôi đang lên kế hoạch du lịch Hà Nội, bạn có thể gợi ý địa điểm không?"
- "Mình sắp đi Đà Nẵng vào tháng 6, mùa đó có gì đặc biệt không?"
- "Cho tôi hỏi, nếu đi Huế thì nên ăn món gì và đi đâu?"

**Giải pháp**:
- Thêm các câu hỏi có context dài hơn
- Thêm các câu hỏi kết hợp nhiều chủ đề

## 🎯 Kế Hoạch Tối Ưu

### Giai Đoạn 1: Sửa Lỗi Nghiêm Trọng (Ưu tiên cao)
1. ✅ Xóa các examples trùng lặp
2. ✅ Thêm examples cho `ask_festival` (tăng từ 105 lên 150+)
3. ✅ Thêm examples cho `ask_transportation` (tăng từ 145 lên 180+)

### Giai Đoạn 2: Cải Thiện Chất Lượng (Ưu tiên trung bình)
1. ✅ Thêm context rõ ràng cho các patterns gây nhầm lẫn
2. ✅ Cân bằng phân bố examples giữa các intent chính
3. ✅ Thêm examples với context phức tạp hơn

### Giai Đoạn 3: Mở Rộng (Ưu tiên thấp)
1. ✅ Thêm examples cho các tỉnh còn lại
2. ✅ Thêm các biến thể ngôn ngữ mới
3. ✅ Thêm các câu hỏi kết hợp nhiều chủ đề

## 📊 Metrics Đề Xuất

### Phân Bố Examples Lý Tưởng:
- **Intent chính** (ask_*): 180-250 examples/intent
- **Intent phụ** (greet, goodbye, etc.): 30-50 examples/intent
- **Intent đặc biệt** (out_of_scope): 50-80 examples

### Tỷ Lệ Phân Bố:
- Intent chính: ~70% tổng examples
- Intent phụ: ~20% tổng examples
- Intent đặc biệt: ~10% tổng examples

## ✅ Checklist Tối Ưu

- [ ] Xóa examples trùng lặp
- [ ] Thêm examples cho `ask_festival` (+45 examples)
- [ ] Thêm examples cho `ask_transportation` (+35 examples)
- [ ] Thêm context cho patterns gây nhầm lẫn
- [ ] Cân bằng phân bố examples
- [ ] Thêm examples cho các tỉnh còn lại
- [ ] Thêm examples với context phức tạp
- [ ] Test lại model sau khi tối ưu

## 🔍 Lưu Ý

1. **Không xóa examples trùng lặp** nếu chúng xuất hiện ở các intent khác nhau (ví dụ: "thôi" trong `deny` và `goodbye` là hợp lý)
2. **Ưu tiên chất lượng hơn số lượng** - examples đa dạng quan trọng hơn số lượng lớn
3. **Test thường xuyên** sau mỗi lần thay đổi để đảm bảo không làm giảm độ chính xác

