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
        # Fix format issues (thiếu dấu)
        'Hai Phong': 'Hải Phòng',  # Fix typo
        'Thua Thien Hue': 'Thừa Thiên Huế',  # Fix typo
        'ThuaThienHue': 'Thừa Thiên Huế',
    })
    
    return mapping

def sync_nlu_entities(nlu_file: Path, alias_mapping: Dict[str, str], backup: bool = True) -> int:
    """
    Đồng bộ entity annotations trong nlu.yml với tên chính thức
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
    
    # Pattern để tìm entity annotations
    entity_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    for line_num, line in enumerate(lines, 1):
        # Chỉ xử lý các dòng có entity annotations
        if line.strip().startswith('- ') and '[' in line and '](' in line:
            example = line[2:].strip()
            total_examples += 1
            
            # Tìm tất cả entities
            entities = re.findall(entity_pattern, example)
            
            if entities:
                fixed_example = example
                
                # Fix từng entity (xử lý từ cuối lên để tránh offset issues)
                for entity_value, entity_type in reversed(entities):
                    # Chỉ fix location entities
                    if entity_type == 'location':
                        # Tìm tên chính thức từ mapping
                        canonical_name = None
                        
                        # Thử exact match trước
                        if entity_value in alias_mapping:
                            canonical_name = alias_mapping[entity_value]
                        else:
                            # Thử case-insensitive match
                            entity_lower = entity_value.lower().strip()
                            for alias, canonical in alias_mapping.items():
                                if alias.lower().strip() == entity_lower:
                                    canonical_name = canonical
                                    break
                        
                        # Nếu tìm thấy tên chính thức và khác với entity value
                        if canonical_name and canonical_name != entity_value:
                            old_annotation = f'[{entity_value}]({entity_type})'
                            new_annotation = f'[{canonical_name}]({entity_type})'
                            
                            # Replace từ cuối lên
                            last_pos = fixed_example.rfind(old_annotation)
                            if last_pos != -1:
                                fixed_example = fixed_example[:last_pos] + new_annotation + fixed_example[last_pos + len(old_annotation):]
                                fixed_count += 1
                                print(f"  ✓ Line {line_num}: '{entity_value}' -> '{canonical_name}'")
                
                # Cập nhật dòng
                if fixed_example != example:
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
        print(f"📊 Tổng số examples: {total_examples}")
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

