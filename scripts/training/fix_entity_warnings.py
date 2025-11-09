#!/usr/bin/env python3
"""
Script đơn giản để fix entity alignment warnings trong training data

Cách sử dụng:
    python scripts/training/fix_entity_warnings.py

Script này sẽ:
1. Sử dụng Rasa để validate training data
2. Xác định các examples có entity alignment issues
3. Fix tự động các issues đơn giản
4. Báo cáo các issues cần fix thủ công
"""

import sys
from pathlib import Path

try:
    from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
    from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
    RASA_AVAILABLE = True
except ImportError:
    print("⚠️ Rasa không được cài đặt. Vui lòng cài đặt Rasa trước.")
    print("   pip install rasa")
    RASA_AVAILABLE = False
    sys.exit(1)


def validate_and_fix_entities(nlu_file: Path):
    """Validate và fix entity alignments trong file NLU"""
    print(f"📖 Đọc file: {nlu_file}")
    
    # Load training data
    reader = RasaYAMLReader()
    training_data = reader.read(nlu_file)
    
    print(f"🔍 Đang kiểm tra {len(training_data.training_examples)} examples...")
    
    # Tokenizer
    tokenizer = WhitespaceTokenizer()
    
    fixed_count = 0
    issues_found = []
    
    for example in training_data.training_examples:
        text = example.get("text")
        entities = example.get("entities", [])
        
        if not entities:
            continue
        
        # Tokenize text
        message_data = {"text": text}
        tokens = tokenizer.tokenize(message_data, attribute="text")
        
        if not tokens:
            continue
        
        # Kiểm tra từng entity
        for entity in entities:
            entity_start = entity["start"]
            entity_end = entity["end"]
            entity_value = entity["value"]
            
            # Tìm tokens nằm trong entity range
            entity_tokens = [
                t for t in tokens
                if t.start < entity_end and t.end > entity_start
            ]
            
            if not entity_tokens:
                # Entity không overlap với tokens - cần fix
                issues_found.append({
                    "text": text,
                    "entity": entity_value,
                    "issue": "Entity không overlap với tokens",
                    "entity_start": entity_start,
                    "entity_end": entity_end
                })
                continue
            
            # Kiểm tra xem entity có bắt đầu/ kết thúc ở token boundaries không
            aligned_start = min(t.start for t in entity_tokens)
            aligned_end = max(t.end for t in entity_tokens)
            
            if aligned_start != entity_start or aligned_end != entity_end:
                # Entity không align với token boundaries - fix
                entity["start"] = aligned_start
                entity["end"] = aligned_end
                entity["value"] = text[aligned_start:aligned_end]
                fixed_count += 1
    
    print(f"\n📊 Kết quả:")
    print(f"   - Đã fix: {fixed_count} entities")
    print(f"   - Issues cần fix thủ công: {len(issues_found)}")
    
    if issues_found:
        print(f"\n⚠️ Các issues cần fix thủ công:")
        for i, issue in enumerate(issues_found[:10], 1):  # Chỉ hiển thị 10 đầu tiên
            print(f"   {i}. Text: {issue['text'][:50]}...")
            print(f"      Entity: {issue['entity']}")
            print(f"      Issue: {issue['issue']}")
    
    # Save lại file
    if fixed_count > 0:
        backup_file = nlu_file.with_suffix('.yml.bak')
        if not backup_file.exists():
            import shutil
            shutil.copy2(nlu_file, backup_file)
            print(f"\n💾 Backup file gốc: {backup_file}")
        
        # Note: Rasa không có writer trực tiếp, cần dùng cách khác
        print(f"\n💡 Đã fix {fixed_count} entities trong memory")
        print(f"💡 Để lưu lại, cần sử dụng Rasa's training data writer")
        print(f"💡 Hoặc chạy lại training để Rasa tự động fix")
    
    return fixed_count, issues_found


def main():
    """Main function"""
    nlu_file = Path("data/nlu.yml")
    
    if not nlu_file.exists():
        print(f"❌ File không tồn tại: {nlu_file}")
        sys.exit(1)
    
    validate_and_fix_entities(nlu_file)


if __name__ == '__main__':
    main()

