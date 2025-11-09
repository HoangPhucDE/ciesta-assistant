#!/usr/bin/env python3
"""
Script để đồng bộ location names trong nlu.yml với tên chính thức từ knowledge base
- Đọc các tỉnh từ data/knowledge_base/provinces/*.json
- Map các alias (TP.HCM, HCM, Sài Gòn, etc.) về tên chính thức (Hồ Chí Minh)
- Thay thế tất cả entity annotations trong nlu.yml
"""

import json
import re
from pathlib import Path
from typing import Dict

def load_provinces_from_kb(kb_dir: Path) -> Dict[str, str]:
    """
    Load tên tỉnh chính thức từ knowledge base
    Returns: Dict mapping từ file name (normalized) -> tên chính thức
    """
    provinces = {}
    
    if not kb_dir.exists():
        print(f"⚠️  Không tìm thấy thư mục: {kb_dir}")
        return provinces
    
    # Load từng file JSON
    for json_file in kb_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Tên chính thức là key đầu tiên trong JSON object
            if data:
                canonical_name = list(data.keys())[0]
                provinces[canonical_name] = canonical_name
                print(f"  ✓ Loaded: {canonical_name} ({json_file.name})")
        except Exception as e:
            print(f"  ✗ Lỗi khi đọc {json_file.name}: {e}")
    
    return provinces

def create_alias_mapping(provinces: Dict[str, str]) -> Dict[str, str]:
    """
    Tạo mapping từ alias -> tên chính thức
    """
    mapping = {}
    
    # Map tên chính thức về chính nó
    for canonical_name in provinces.keys():
        mapping[canonical_name] = canonical_name
        mapping[canonical_name.lower()] = canonical_name
    
    # Hồ Chí Minh và các alias
    mapping.update({
        'TP.HCM': 'Hồ Chí Minh',
        'TP HCM': 'Hồ Chí Minh',
        'TPHCM': 'Hồ Chí Minh',
        'HCM': 'Hồ Chí Minh',
        'Sài Gòn': 'Hồ Chí Minh',
        'Sai Gon': 'Hồ Chí Minh',
        'Sài gòn': 'Hồ Chí Minh',
        'TP Hồ Chí Minh': 'Hồ Chí Minh',
        'TP.Hồ Chí Minh': 'Hồ Chí Minh',
        'Thành phố Hồ Chí Minh': 'Hồ Chí Minh',
        'thành phố hcm': 'Hồ Chí Minh',
        'thành phố hồ chí minh': 'Hồ Chí Minh',
    })
    
    # Hà Nội và các alias
    mapping.update({
        'Hanoi': 'Hà Nội',
        'Ha Noi': 'Hà Nội',
        'HaNoi': 'Hà Nội',
        'Thủ đô Hà Nội': 'Hà Nội',
        'thủ đô hà nội': 'Hà Nội',
    })
    
    # Đà Nẵng và các alias
    mapping.update({
        'Da Nang': 'Đà Nẵng',
        'DaNang': 'Đà Nẵng',
        'TP.Đà Nẵng': 'Đà Nẵng',
        'TP Đà Nẵng': 'Đà Nẵng',
        'Thành phố Đà Nẵng': 'Đà Nẵng',
        'thành phố đà nẵng': 'Đà Nẵng',
    })
    
    # Huế và các alias
    mapping.update({
        'Hue': 'Huế',
        'Huế': 'Huế',
        'hue': 'Huế',
    })
    
    # Cần Thơ và các alias
    mapping.update({
        'Can Tho': 'Cần Thơ',
        'CanTho': 'Cần Thơ',
        'Thành phố Cần Thơ': 'Cần Thơ',
        'thành phố cần thơ': 'Cần Thơ',
    })
    
    # Các tỉnh thành khác
    mapping.update({
        'Vung Tau': 'Vũng Tàu',
        'VungTau': 'Vũng Tàu',
        'Thai Nguyen': 'Thái Nguyên',
        'ThaiNguyen': 'Thái Nguyên',
        'Quang Ngai': 'Quảng Ngãi',
        'QuangNgai': 'Quảng Ngãi',
        'Phu Quoc': 'Phú Quốc',
        'PhuQuoc': 'Phú Quốc',
        'Ca Mau': 'Cà Mau',
        'CaMau': 'Cà Mau',
        'Da Lat': 'Đà Lạt',
        'DaLat': 'Đà Lạt',
        'Hoi An': 'Hội An',
        'HoiAn': 'Hội An',
        'Sapa': 'Sapa',
        'Sapa,': 'Sapa',
        # Fix format issues (thiếu dấu)
        'Hai Phong': 'Hải Phòng',  # Fix typo
        'Thua Thien Hue': 'Thừa Thiên Huế',  # Fix typo
        'ThuaThienHue': 'Thừa Thiên Huế',
        # Bắc Ninh
        'Bắc Ninh': 'Bắc Ninh',
        'Bắc Ninh,': 'Bắc Ninh',
        # An Giang
        'An Giang': 'An Giang',
        'An Giang,': 'An Giang',
        # Cần Thơ
        'Cần Thơ': 'Cần Thơ',
        'Cần Thơ,': 'Cần Thơ',
        # Gia Lai
        'Gia Lai': 'Gia Lai',
        'Gia Lai,': 'Gia Lai',
        # Quảng Ngãi
        'Quảng Ngãi': 'Quảng Ngãi',
        'Quảng Ngãi,': 'Quảng Ngãi',
        # Thái Nguyên
        'Thái Nguyên': 'Thái Nguyên',
        'Thái Nguyên,': 'Thái Nguyên',
        # Vũng Tàu
        'Vũng Tàu': 'Vũng Tàu',
        'Vũng Tàu,': 'Vũng Tàu',
        # Phú Quốc
        'Phú Quốc': 'Phú Quốc',
        'Phú Quốc,': 'Phú Quốc',
        # Cà Mau
        'Cà Mau': 'Cà Mau',
        'Cà Mau,': 'Cà Mau',
        # Hội An
        'Hội An': 'Hội An',
        'Hội An,': 'Hội An',
    })
    
    return mapping

def extract_text_from_example(example_text: str) -> str:
    """
    Trích xuất text thuần từ example (loại bỏ entity annotations)
    """
    # Thay thế entity annotations bằng giá trị của chúng
    text_only = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', example_text)
    return text_only

def find_actual_text_in_example(example_text: str, entity_value: str) -> str:
    """
    Tìm text thực tế trong example text tương ứng với entity value
    Returns: actual_text trong example hoặc entity_value nếu không tìm thấy
    """
    # Loại bỏ dấu phẩy cuối trong entity value
    entity_clean = entity_value.rstrip(', ').strip()
    
    # Trích xuất text thuần từ example
    text_only = extract_text_from_example(example_text)
    
    # Tìm entity trong text (case-insensitive)
    entity_lower = entity_clean.lower()
    text_lower = text_only.lower()
    
    # Tìm exact match (case-insensitive)
    pos = text_lower.find(entity_lower)
    if pos != -1:
        # Lấy text thực tế từ example (giữ nguyên case và format)
        actual_text = text_only[pos:pos + len(entity_clean)]
        return actual_text
    
    # Nếu không tìm thấy exact match, thử tìm với normalized (loại bỏ dấu cách, dấu câu)
    entity_normalized = re.sub(r'[^\w]', '', entity_lower)
    text_normalized = re.sub(r'[^\w]', '', text_lower)
    
    pos_norm = text_normalized.find(entity_normalized)
    if pos_norm != -1:
        # Tìm lại vị trí trong text gốc (phức tạp hơn, nhưng đơn giản hóa)
        # Nếu không tìm thấy chính xác, trả về entity_clean
        return entity_clean
    
    # Nếu không tìm thấy, trả về entity_clean (đã loại bỏ dấu phẩy)
    return entity_clean

def sync_nlu_entities(nlu_file: Path, alias_mapping: Dict[str, str], backup: bool = True) -> int:
    """
    Đồng bộ entity annotations trong nlu.yml với tên chính thức
    - Loại bỏ dấu phẩy cuối trong entity value (nếu có)
    - Map aliases về tên chính thức (chỉ khi text có từ đó)
    - Đảm bảo entity value khớp với text thực tế trong câu
    Returns: Số lượng entities đã được fix
    """
    if not nlu_file.exists():
        print(f"✗ Không tìm thấy file: {nlu_file}")
        return 0
    
    # Backup file
    if backup:
        backup_file = nlu_file.with_suffix('.yml.bak')
        if not backup_file.exists():
            import shutil
            shutil.copy2(nlu_file, backup_file)
            print(f"  💾 Backup: {backup_file}")
    
    # Đọc file
    with open(nlu_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    fixed_lines = []
    fixed_count = 0
    total_examples = 0
    
    # Pattern để tìm entity annotations: [entity_value](entity_type)
    entity_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    for line_num, line in enumerate(lines, 1):
        # Chỉ xử lý các dòng có entity annotations (dòng example)
        if line.strip().startswith('- ') and '[' in line and '](' in line:
            example = line[2:].strip()  # Loại bỏ "- " ở đầu
            total_examples += 1
            
            # Tìm tất cả entities trong dòng
            entities = re.findall(entity_pattern, example)
            
            if entities:
                fixed_example = example
                example_changed = False
                
                # Fix từng entity (xử lý từ cuối lên để tránh offset issues)
                for entity_value, entity_type in reversed(entities):
                    # Chỉ fix location entities
                    if entity_type == 'location':
                        # Loại bỏ dấu phẩy cuối trong entity value
                        entity_clean = entity_value.rstrip(', ').strip()
                        has_comma_in_value = entity_value != entity_clean
                        
                        # Trích xuất text thuần từ example (loại bỏ entity annotations)
                        text_only = extract_text_from_example(example)
                        
                        # Tìm tên chính thức từ mapping
                        canonical_name = None
                        entity_lower = entity_clean.lower().strip()
                        
                        # Thử match với entity value (đã loại bỏ dấu phẩy)
                        if entity_clean in alias_mapping:
                            canonical_name = alias_mapping[entity_clean]
                        else:
                            # Thử case-insensitive match
                            for alias, canonical in alias_mapping.items():
                                if alias.lower().strip() == entity_lower:
                                    canonical_name = canonical
                                    break
                        
                        # Xác định entity value cuối cùng
                        final_entity_value = None
                        
                        if canonical_name:
                            # Kiểm tra xem canonical name có trong text không (case-insensitive)
                            text_lower = text_only.lower()
                            
                            # Tìm vị trí của canonical name trong text
                            canonical_lower = canonical_name.lower()
                            if canonical_lower in text_lower:
                                # Canonical name có trong text, lấy text thực tế (giữ nguyên case)
                                pos = text_lower.find(canonical_lower)
                                if pos != -1:
                                    # Lấy text thực tế từ example (có thể có case khác)
                                    # Tìm trong text_only với case-insensitive nhưng lấy exact text
                                    for i in range(len(text_only) - len(canonical_name) + 1):
                                        if text_only[i:i+len(canonical_name)].lower() == canonical_lower:
                                            final_entity_value = text_only[i:i+len(canonical_name)]
                                            break
                                    
                                    if not final_entity_value:
                                        final_entity_value = canonical_name
                            else:
                                # Canonical name không có trong text
                                # Kiểm tra xem có alias nào của canonical name trong text không
                                found_alias = None
                                for alias, canonical in alias_mapping.items():
                                    if canonical == canonical_name and alias.lower() in text_lower:
                                        # Tìm text thực tế của alias
                                        alias_pos = text_lower.find(alias.lower())
                                        if alias_pos != -1:
                                            # Lấy text thực tế (giữ nguyên case)
                                            for i in range(len(text_only) - len(alias) + 1):
                                                if text_only[i:i+len(alias)].lower() == alias.lower():
                                                    found_alias = text_only[i:i+len(alias)]
                                                    break
                                            
                                            if found_alias:
                                                # Map alias về canonical name
                                                final_entity_value = canonical_name
                                                break
                                
                                # Nếu không tìm thấy alias, dùng entity_clean (đã loại bỏ dấu phẩy)
                                if not final_entity_value:
                                    # Kiểm tra xem entity_clean có trong text không
                                    if entity_lower in text_lower:
                                        # Tìm text thực tế của entity_clean
                                        pos = text_lower.find(entity_lower)
                                        if pos != -1:
                                            for i in range(len(text_only) - len(entity_clean) + 1):
                                                if text_only[i:i+len(entity_clean)].lower() == entity_lower:
                                                    final_entity_value = text_only[i:i+len(entity_clean)]
                                                    break
                                    
                                    if not final_entity_value:
                                        final_entity_value = entity_clean
                        elif has_comma_in_value:
                            # Nếu không tìm thấy mapping nhưng có dấu phẩy trong entity value, loại bỏ dấu phẩy
                            final_entity_value = entity_clean
                        else:
                            # Không có thay đổi
                            continue
                        
                        # Đảm bảo final_entity_value không có dấu phẩy cuối
                        if final_entity_value:
                            final_entity_value = final_entity_value.rstrip(', ').strip()
                        
                        # Chỉ fix nếu có thay đổi
                        if final_entity_value and final_entity_value != entity_value:
                            old_annotation = f'[{entity_value}]({entity_type})'
                            new_annotation = f'[{final_entity_value}]({entity_type})'
                            
                            # Replace từ cuối lên (để tránh replace nhầm nếu có nhiều entity giống nhau)
                            last_pos = fixed_example.rfind(old_annotation)
                            if last_pos != -1:
                                fixed_example = fixed_example[:last_pos] + new_annotation + fixed_example[last_pos + len(old_annotation):]
                                fixed_count += 1
                                example_changed = True
                                
                                change_desc = f"'{entity_value}' -> '{final_entity_value}'"
                                if has_comma_in_value:
                                    change_desc += " (removed comma)"
                                print(f"  ✓ Line {line_num}: {change_desc}")
                
                # Cập nhật dòng
                if example_changed:
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * indent + '- ' + fixed_example + '\n')
                else:
                    fixed_lines.append(line + '\n')
            else:
                fixed_lines.append(line + '\n')
        else:
            fixed_lines.append(line + '\n')
    
    # Ghi lại file nếu có thay đổi
    if fixed_count > 0:
        with open(nlu_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"\n✅ Đã fix {fixed_count} entity annotations")
        print(f"📊 Tổng số examples đã xử lý: {total_examples}")
        return fixed_count
    else:
        print("ℹ️  Không có entity nào cần fix")
        return 0

def main():
    """Main function"""
    print("=" * 60)
    print("ĐỒNG BỘ LOCATION NAMES TRONG NLU.YML")
    print("=" * 60)
    print()
    
    # Tìm project root (có thể chạy từ project root hoặc từ scripts/training)
    current_dir = Path.cwd()
    project_root = None
    
    # Thử các vị trí có thể
    possible_roots = [
        current_dir,  # Đang ở project root
        current_dir.parent.parent,  # Đang ở scripts/training
        current_dir.parent,  # Đang ở scripts
    ]
    
    for possible_root in possible_roots:
        kb_dir = possible_root / "data" / "knowledge_base" / "provinces"
        if kb_dir.exists():
            project_root = possible_root
            break
    
    if not project_root:
        print("✗ Không tìm thấy project root (cần data/knowledge_base/provinces)")
        return False
    
    print(f"📁 Project root: {project_root}")
    os.chdir(project_root)
    
    # Load provinces từ knowledge base
    kb_dir = project_root / "data" / "knowledge_base" / "provinces"
    print(f"\n📂 Loading provinces từ: {kb_dir}")
    provinces = load_provinces_from_kb(kb_dir)
    
    if not provinces:
        print("✗ Không tìm thấy provinces trong knowledge base")
        return False
    
    print(f"✅ Đã load {len(provinces)} provinces")
    
    # Tạo alias mapping
    print("\n🔗 Tạo alias mapping...")
    alias_mapping = create_alias_mapping(provinces)
    print(f"✅ Đã tạo {len(alias_mapping)} alias mappings")
    
    # Sync nlu.yml
    nlu_file = project_root / "data" / "nlu.yml"
    print(f"\n📝 Đồng bộ entities trong: {nlu_file}")
    fixed_count = sync_nlu_entities(nlu_file, alias_mapping)
    
    if fixed_count > 0:
        print("\n" + "=" * 60)
        print("✅ HOÀN TẤT!")
        print(f"   Đã fix {fixed_count} entity annotations")
        print("   Tất cả location names đã được đồng bộ với knowledge base")
        print("=" * 60)
        return True
    else:
        print("\n" + "=" * 60)
        print("ℹ️  KHÔNG CÓ THAY ĐỔI")
        print("   Tất cả location names đã đúng")
        print("=" * 60)
        return True

if __name__ == "__main__":
    import os
    import sys
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

