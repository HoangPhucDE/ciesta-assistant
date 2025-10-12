#!/usr/bin/env python3
"""
Script kiểm tra và validate các file JSON trong knowledge base
Chạy: python validate_knowledge_base.py
"""

import json
import os
from pathlib import Path
from typing import Dict, List

# Danh sách 34 tỉnh thành theo nghị quyết 12/6/2025
EXPECTED_PROVINCES = [
    # 6 Thành phố
    "Hà Nội", "Huế", "Đà Nẵng", "Hải Phòng", "Hồ Chí Minh", "Cần Thơ",
    # 28 Tỉnh
    "Cao Bằng", "Điện Biên", "Lai Châu", "Lạng Sơn", "Nghệ An", "Quảng Ninh",
    "Sơn La", "Thanh Hóa", "Tuyên Quang", "Lào Cai", "Thái Nguyên", "Phú Thọ",
    "Bắc Ninh", "Hưng Yên", "Ninh Bình", "Hà Tĩnh", "Quảng Trị", "Quảng Ngãi",
    "Gia Lai", "Khánh Hòa", "Lâm Đồng", "Đắk Lắk", "Đồng Nai", "Tây Ninh",
    "Vĩnh Long", "Đồng Tháp", "Cà Mau", "An Giang"
]

# Các trường bắt buộc trong mỗi file JSON
REQUIRED_FIELDS = [
    "culture_details",
    "places_to_visit",
    "what_to_eat",
    "festivals",
    "specialties_as_gifts",
    "best_time_to_visit"
]

# Các trường con bắt buộc
PLACE_FIELDS = ["name", "category", "details"]
FOOD_FIELDS = ["name", "category", "details"]
FESTIVAL_FIELDS = ["name", "time", "details"]


class KnowledgeBaseValidator:
    def __init__(self, kb_dir: str = "data/knowledge_base/provinces"):
        self.kb_dir = Path(kb_dir)
        self.errors = []
        self.warnings = []
        self.provinces_found = []
    
    def validate(self):
        """Validate toàn bộ knowledge base"""
        print("=" * 60)
        print("🔍 BẮT ĐẦU KIỂM TRA KNOWLEDGE BASE")
        print("=" * 60)
        
        # Kiểm tra thư mục tồn tại
        if not self.kb_dir.exists():
            self.errors.append(f"❌ Thư mục {self.kb_dir} không tồn tại!")
            self._print_results()
            return
        
        # Lấy danh sách file JSON
        json_files = list(self.kb_dir.glob("*.json"))
        print(f"\n📁 Tìm thấy {len(json_files)} file JSON")
        
        if len(json_files) == 0:
            self.errors.append("❌ Không tìm thấy file JSON nào!")
            self._print_results()
            return
        
        # Validate từng file
        for json_file in sorted(json_files):
            self._validate_file(json_file)
        
        # Kiểm tra số lượng tỉnh
        self._check_province_count()
        
        # In kết quả
        self._print_results()
    
    def _validate_file(self, file_path: Path):
        """Validate một file JSON"""
        print(f"\n📄 Kiểm tra: {file_path.name}")
        
        try:
            # Đọc file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Kiểm tra cấu trúc
            if not isinstance(data, dict):
                self.errors.append(f"  ❌ {file_path.name}: Phải là object JSON")
                return
            
            if len(data) == 0:
                self.errors.append(f"  ❌ {file_path.name}: File rỗng")
                return
            
            # Lấy tên tỉnh (key đầu tiên)
            province_name = list(data.keys())[0]
            province_data = data[province_name]
            
            self.provinces_found.append(province_name)
            print(f"  ✓ Tỉnh: {province_name}")
            
            # Kiểm tra các trường bắt buộc
            missing_fields = []
            for field in REQUIRED_FIELDS:
                if field not in province_data:
                    missing_fields.append(field)
            
            if missing_fields:
                self.errors.append(
                    f"  ❌ {province_name}: Thiếu trường {', '.join(missing_fields)}"
                )
            
            # Validate chi tiết
            self._validate_places(province_name, province_data.get("places_to_visit", []))
            self._validate_foods(province_name, province_data.get("what_to_eat", []))
            self._validate_festivals(province_name, province_data.get("festivals", []))
            
            # Kiểm tra độ dài culture_details
            culture = province_data.get("culture_details", "")
            if len(culture) < 50:
                self.warnings.append(
                    f"  ⚠️  {province_name}: culture_details quá ngắn ({len(culture)} ký tự)"
                )
            
        except json.JSONDecodeError as e:
            self.errors.append(f"  ❌ {file_path.name}: Lỗi JSON - {e}")
        except Exception as e:
            self.errors.append(f"  ❌ {file_path.name}: Lỗi - {e}")
    
    def _validate_places(self, province: str, places: List[Dict]):
        """Validate danh sách địa điểm"""
        if not isinstance(places, list):
            self.errors.append(f"  ❌ {province}: places_to_visit phải là array")
            return
        
        if len(places) == 0:
            self.warnings.append(f"  ⚠️  {province}: Chưa có địa điểm tham quan")
            return
        
        for i, place in enumerate(places):
            for field in PLACE_FIELDS:
                if field not in place:
                    self.errors.append(
                        f"  ❌ {province}: Địa điểm #{i+1} thiếu trường '{field}'"
                    )
    
    def _validate_foods(self, province: str, foods: List[Dict]):
        """Validate danh sách món ăn"""
        if not isinstance(foods, list):
            self.errors.append(f"  ❌ {province}: what_to_eat phải là array")
            return
        
        if len(foods) == 0:
            self.warnings.append(f"  ⚠️  {province}: Chưa có món ăn đặc sản")
            return
        
        for i, food in enumerate(foods):
            for field in FOOD_FIELDS:
                if field not in food:
                    self.errors.append(
                        f"  ❌ {province}: Món ăn #{i+1} thiếu trường '{field}'"
                    )
    
    def _validate_festivals(self, province: str, festivals: List[Dict]):
        """Validate danh sách lễ hội"""
        if not isinstance(festivals, list):
            self.errors.append(f"  ❌ {province}: festivals phải là array")
            return
        
        if len(festivals) == 0:
            self.warnings.append(f"  ⚠️  {province}: Chưa có lễ hội")
    
    def _check_province_count(self):
        """Kiểm tra số lượng tỉnh"""
        print(f"\n\n{'=' * 60}")
        print("📊 TỔNG KẾT")
        print("=" * 60)
        
        total_found = len(self.provinces_found)
        total_expected = len(EXPECTED_PROVINCES)
        
        print(f"\n✓ Tìm thấy: {total_found}/{total_expected} tỉnh thành")
        
        if total_found < total_expected:
            missing = set(EXPECTED_PROVINCES) - set(self.provinces_found)
            print(f"\n❌ THIẾU {len(missing)} TỈNH:")
            for province in sorted(missing):
                print(f"   • {province}")
        
        if total_found > total_expected:
            extra = set(self.provinces_found) - set(EXPECTED_PROVINCES)
            print(f"\n⚠️  THỪA {len(extra)} TỈNH (không thuộc 34 tỉnh mới):")
            for province in sorted(extra):
                print(f"   • {province}")
        
        # Kiểm tra tên tỉnh không khớp
        unmatched = []
        for found in self.provinces_found:
            if found not in EXPECTED_PROVINCES:
                # Tìm tên gần giống
                similar = [exp for exp in EXPECTED_PROVINCES 
                          if exp.lower().replace(" ", "") == found.lower().replace(" ", "")]
                if similar:
                    unmatched.append((found, similar[0]))
        
        if unmatched:
            print(f"\n⚠️  TÊN TỈNH KHÔNG CHÍNH XÁC:")
            for wrong, correct in unmatched:
                print(f"   • '{wrong}' → nên đổi thành '{correct}'")
    
    def _print_results(self):
        """In kết quả kiểm tra"""
        print(f"\n\n{'=' * 60}")
        print("📋 KẾT QUẢ KIỂM TRA")
        print("=" * 60)
        
        if self.errors:
            print(f"\n❌ LỖI ({len(self.errors)}):")
            for error in self.errors:
                print(error)
        
        if self.warnings:
            print(f"\n⚠️  CẢNH BÁO ({len(self.warnings)}):")
            for warning in self.warnings:
                print(warning)
        
        if not self.errors and not self.warnings:
            print("\n✅ HOÀN HẢO! Tất cả các file đều hợp lệ.")
        
        print("\n" + "=" * 60)
        
        # Tổng kết
        if self.errors:
            print("❌ CÓ LỖI - Cần sửa trước khi train!")
            return False
        elif self.warnings:
            print("⚠️  CÓ CẢNH BÁO - Nên bổ sung thêm dữ liệu")
            return True
        else:
            print("✅ SẴN SÀNG TRAIN MODEL!")
            return True


def generate_template_json(province_name: str) -> str:
    """Tạo template JSON cho một tỉnh"""
    template = {
        province_name: {
            "culture_details": f"Thông tin văn hóa về {province_name}...",
            "sub_regions": [
                {
                    "name": f"Khu vực {province_name} (cũ)",
                    "highlights": "Các điểm nổi bật..."
                }
            ],
            "places_to_visit": [
                {
                    "name": "Tên địa điểm",
                    "category": "lịch sử",
                    "details": "Mô tả chi tiết..."
                }
            ],
            "what_to_eat": [
                {
                    "name": "Tên món ăn",
                    "category": "đặc sản",
                    "details": "Mô tả món ăn..."
                }
            ],
            "festivals": [
                {
                    "name": "Tên lễ hội",
                    "time": "Thời gian diễn ra",
                    "details": "Mô tả lễ hội..."
                }
            ],
            "specialties_as_gifts": [
                "Đặc sản 1",
                "Đặc sản 2"
            ],
            "best_time_to_visit": "Thời điểm tốt nhất để du lịch...",
            "transportation": "Thông tin phương tiện di chuyển..."
        }
    }
    return json.dumps(template, ensure_ascii=False, indent=4)


def create_missing_files(kb_dir: str = "data/knowledge_base"):
    """Tạo file template cho các tỉnh còn thiếu"""
    kb_path = Path(kb_dir)
    kb_path.mkdir(parents=True, exist_ok=True)
    
    existing_provinces = []
    for json_file in kb_path.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    province_name = list(data.keys())[0]
                    existing_provinces.append(province_name)
        except:
            pass
    
    missing = set(EXPECTED_PROVINCES) - set(existing_provinces)
    
    if not missing:
        print("✅ Đã có đủ 34 tỉnh thành!")
        return
    
    print(f"\n📝 Tạo file template cho {len(missing)} tỉnh còn thiếu...\n")
    
    for province in sorted(missing):
        # Chuyển tên tỉnh thành tên file
        filename = province.lower()
        filename = filename.replace("đ", "d").replace("ă", "a").replace("â", "a")
        filename = filename.replace("ê", "e").replace("ô", "o").replace("ơ", "o")
        filename = filename.replace("ư", "u").replace("à", "a").replace("á", "a")
        filename = filename.replace("ả", "a").replace("ã", "a").replace("ạ", "a")
        filename = filename.replace("è", "e").replace("é", "e").replace("ẻ", "e")
        filename = filename.replace("ẽ", "e").replace("ẹ", "e").replace("ì", "i")
        filename = filename.replace("í", "i").replace("ỉ", "i").replace("ĩ", "i")
        filename = filename.replace("ị", "i").replace("ò", "o").replace("ó", "o")
        filename = filename.replace("ỏ", "o").replace("õ", "o").replace("ọ", "o")
        filename = filename.replace("ù", "u").replace("ú", "u").replace("ủ", "u")
        filename = filename.replace("ũ", "u").replace("ụ", "u").replace("ỳ", "y")
        filename = filename.replace("ý", "y").replace("ỷ", "y").replace("ỹ", "y")
        filename = filename.replace("ỵ", "y").replace(" ", "_")
        filename = f"{filename}.json"
        
        file_path = kb_path / filename
        
        # Tạo file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(generate_template_json(province))
        
        print(f"✓ Tạo: {filename}")
    
    print(f"\n✅ Đã tạo {len(missing)} file template. Hãy điền thông tin vào!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--create-missing":
        # Tạo file template cho tỉnh thiếu
        create_missing_files()
    else:
        # Validate knowledge base
        validator = KnowledgeBaseValidator()
        success = validator.validate()
        sys.exit(0 if success else 1)