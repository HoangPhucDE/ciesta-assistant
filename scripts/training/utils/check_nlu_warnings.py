#!/usr/bin/env python3
"""
Script để kiểm tra nlu.yml sau khi sync_location_names.py
- Kiểm tra entities có trong knowledge base không
- Kiểm tra entities có format đúng không
- Kiểm tra entities có thể gây warning
"""

import json
import re
from pathlib import Path
from typing import Dict, Set, List

def load_provinces_from_kb(kb_dir: Path) -> Set[str]:
    """Load tên tỉnh chính thức từ knowledge base"""
    provinces = set()
    
    if not kb_dir.exists():
        return provinces
    
    for json_file in kb_dir.glob("*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    canonical_name = list(data.keys())[0]
                    provinces.add(canonical_name)
        except Exception:
            pass
    
    return provinces

def check_entity_in_text(entity_value: str, text: str) -> bool:
    """
    Kiểm tra xem entity value có xuất hiện trong text không
    (sau khi thay thế annotation bằng value)
    """
    # Loại bỏ các ký tự đặc biệt ở đầu/cuối text (như dấu phẩy, dấu chấm)
    import string
    punctuation = string.punctuation + '.,;:!?。，；：！？'
    
    # Tokenize text
    tokens = text.split()
    entity_tokens = entity_value.split()
    
    # Kiểm tra exact match (case insensitive, không tính punctuation)
    entity_clean = entity_value.lower().strip(punctuation).strip()
    text_lower = text.lower()
    
    # Tìm entity trong text (có thể có punctuation xung quanh)
    if entity_clean in text_lower:
        # Kiểm tra xem có khớp với token boundaries không
        for i in range(len(tokens) - len(entity_tokens) + 1):
            token_slice = ' '.join(tokens[i:i+len(entity_tokens)])
            token_slice_clean = token_slice.lower().strip(punctuation).strip()
            if token_slice_clean == entity_clean:
                return True
    
    # Nếu không tìm thấy exact match, kiểm tra với các biến thể
    # (ví dụ: "Đà Nẵng" có thể xuất hiện trong text như "đà nẵng")
    entity_words = entity_clean.split()
    if len(entity_words) > 0:
        # Tìm từng từ của entity trong text
        all_words_found = True
        for word in entity_words:
            if word not in text_lower:
                all_words_found = False
                break
        
        if all_words_found:
            # Kiểm tra xem các từ có xuất hiện liên tiếp không
            text_words = text_lower.split()
            for i in range(len(text_words) - len(entity_words) + 1):
                text_slice = text_words[i:i+len(entity_words)]
                if ' '.join(text_slice).strip(punctuation).strip() == entity_clean:
                    return True
    
    return False

def check_nlu_file(nlu_file: Path, kb_dir: Path) -> Dict:
    """Kiểm tra nlu.yml file"""
    results = {
        'total_examples': 0,
        'total_entities': 0,
        'entities_in_kb': 0,
        'entities_not_in_kb': set(),
        'potential_warnings': [],
        'format_issues': [],
    }
    
    # Load provinces từ KB
    provinces = load_provinces_from_kb(kb_dir)
    print(f"✅ Loaded {len(provinces)} provinces from knowledge base")
    
    # Đọc nlu.yml
    if not nlu_file.exists():
        print(f"✗ Không tìm thấy file: {nlu_file}")
        return results
    
    with open(nlu_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    entity_pattern = r'\[([^\]]+)\]\(location\)'
    
    # Tìm tất cả entities
    all_entities = re.findall(entity_pattern, content)
    results['total_entities'] = len(all_entities)
    unique_entities = set(all_entities)
    
    # Kiểm tra từng entity
    for entity_value in unique_entities:
        if entity_value in provinces:
            results['entities_in_kb'] += all_entities.count(entity_value)
        else:
            results['entities_not_in_kb'].add(entity_value)
            results['total_entities'] -= all_entities.count(entity_value)  # Đã đếm rồi, không trừ lại
    
    # Kiểm tra từng dòng để tìm potential warnings
    for line_num, line in enumerate(lines, 1):
        if line.strip().startswith('- ') and '[' in line and '](' in line:
            example = line[2:].strip()
            results['total_examples'] += 1
            
            # Tìm entities
            entities = re.findall(entity_pattern, example)
            
            if entities:
                # Thay thế annotations bằng values để có text thuần
                text_with_values = example
                for match in entities:
                    if isinstance(match, tuple):
                        entity_value, entity_type = match
                    else:
                        entity_value = match
                        entity_type = 'location'
                    
                    text_with_values = re.sub(
                        rf'\[{re.escape(entity_value)}\]\(location\)',
                        entity_value,
                        text_with_values,
                        count=1
                    )
                
                # Kiểm tra từng entity
                # entities là list of tuples (entity_value, entity_type) từ re.findall
                for match in entities:
                    if isinstance(match, tuple):
                        entity_value, entity_type = match
                    else:
                        entity_value = match
                        entity_type = 'location'
                    
                    # Kiểm tra xem entity value có trong text không
                    if not check_entity_in_text(entity_value, text_with_values):
                        results['potential_warnings'].append({
                            'line': line_num,
                            'example': example[:80],
                            'entity_value': entity_value,
                            'text_with_values': text_with_values[:80],
                        })
    
    return results

def check_format_issues(entities: Set[str]) -> List[str]:
    """Kiểm tra các vấn đề về format"""
    issues = []
    
    # Kiểm tra entities không có dấu (có thể là typo)
    common_typos = {
        'Hai Phong': 'Hải Phòng',
        'Thua Thien Hue': 'Thừa Thiên Huế',
    }
    
    for entity in entities:
        if entity in common_typos:
            issues.append(f"⚠️  '{entity}' có thể là typo của '{common_typos[entity]}'")
    
    return issues

def main():
    """Main function"""
    print("=" * 60)
    print("KIỂM TRA NLU.YML SAU KHI SYNC LOCATION NAMES")
    print("=" * 60)
    print()
    
    # Tìm project root (có thể chạy từ project root hoặc từ scripts/training/utils)
    current_dir = Path.cwd()
    project_root = None
    
    # Thử các vị trí có thể
    possible_roots = [
        current_dir,  # Đang ở project root
        current_dir.parent.parent.parent,  # Đang ở scripts/training/utils
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
    
    # Kiểm tra nlu.yml
    nlu_file = project_root / "data" / "nlu.yml"
    kb_dir = project_root / "data" / "knowledge_base" / "provinces"
    
    print(f"\n🔍 Kiểm tra: {nlu_file}")
    results = check_nlu_file(nlu_file, kb_dir)
    
    # In kết quả
    print(f"\n📊 KẾT QUẢ KIỂM TRA:")
    print(f"   Tổng số examples: {results['total_examples']}")
    print(f"   Tổng số location entities: {results['total_entities']}")
    print(f"   Entities có trong KB: {results['entities_in_kb']}")
    print(f"   Entities không có trong KB: {len(results['entities_not_in_kb'])}")
    
    # Kiểm tra format issues
    format_issues = check_format_issues(results['entities_not_in_kb'])
    if format_issues:
        print(f"\n⚠️  FORMAT ISSUES:")
        for issue in format_issues:
            print(f"   {issue}")
    
    # Entities không có trong KB
    if results['entities_not_in_kb']:
        print(f"\n⚠️  ENTITIES KHÔNG CÓ TRONG KNOWLEDGE BASE:")
        print("   (Có thể là tên thành phố/địa danh con, không phải tỉnh)")
        
        # Đếm số lần xuất hiện
        entity_counts = {}
        with open(nlu_file, 'r', encoding='utf-8') as f:
            content = f.read()
            entity_pattern = r'\[([^\]]+)\]\(location\)'
            all_entities = re.findall(entity_pattern, content)
            for entity in results['entities_not_in_kb']:
                entity_counts[entity] = all_entities.count(entity)
        
        # Sắp xếp theo số lần xuất hiện
        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
        
        for entity, count in sorted_entities[:20]:  # Chỉ hiển thị 20 đầu tiên
            print(f"   - {entity}: {count} lần")
        
        if len(sorted_entities) > 20:
            print(f"   ... và {len(sorted_entities) - 20} entities khác")
    
    # Potential warnings
    if results['potential_warnings']:
        print(f"\n⚠️  POTENTIAL WARNINGS ({len(results['potential_warnings'])}):")
        print("   (Entity value không khớp với text thực tế)")
        
        for i, warning in enumerate(results['potential_warnings'][:10], 1):
            print(f"\n   {i}. Line {warning['line']}:")
            print(f"      Example: {warning['example']}")
            print(f"      Entity: '{warning['entity_value']}'")
            print(f"      Text: {warning['text_with_values']}")
    else:
        print(f"\n✅ KHÔNG CÓ POTENTIAL WARNINGS!")
        print("   Tất cả entity values khớp với text thực tế")
    
    # Kết luận
    print("\n" + "=" * 60)
    if results['potential_warnings']:
        print("⚠️  CÓ THỂ CÓ WARNINGS KHI TRAIN")
        print("   Vui lòng kiểm tra các entities không khớp với text")
    else:
        print("✅ KHÔNG CÓ WARNINGS!")
        print("   Tất cả entities đều khớp với text thực tế")
    print("=" * 60)
    
    return len(results['potential_warnings']) == 0

if __name__ == "__main__":
    import sys
    
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

