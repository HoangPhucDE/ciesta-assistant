#!/usr/bin/env python3
"""
Script đơn giản để kiểm tra entity alignment warnings trong training data
"""

import sys
from pathlib import Path

try:
    from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
    from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
    from rasa.nlu.config import RasaNLUModelConfig
    RASA_AVAILABLE = True
except ImportError:
    print("⚠️ Rasa không được cài đặt")
    RASA_AVAILABLE = False
    sys.exit(1)


def check_entity_alignments(nlu_file: Path):
    """Kiểm tra entity alignments trong file NLU"""
    print(f"📖 Đọc file: {nlu_file}")
    
    # Load training data
    reader = RasaYAMLReader()
    training_data = reader.read(nlu_file)
    
    print(f"🔍 Đang kiểm tra {len(training_data.training_examples)} examples...")
    
    # Tokenizer config
    config = {"intent_tokenization_flag": True, "intent_split_symbol": "+"}
    tokenizer = WhitespaceTokenizer(config)
    
    issues = []
    total_entities = 0
    
    for example in training_data.training_examples:
        text = example.get("text")
        entities = example.get("entities", [])
        
        if not entities:
            continue
        
        total_entities += len(entities)
        
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
                # Entity không overlap với tokens
                issues.append({
                    "text": text,
                    "entity": entity_value,
                    "type": "no_overlap",
                    "entity_start": entity_start,
                    "entity_end": entity_end,
                    "tokens": [(t.start, t.end, t.text) for t in tokens]
                })
                continue
            
            # Kiểm tra xem entity có bắt đầu/ kết thúc ở token boundaries không
            aligned_start = min(t.start for t in entity_tokens)
            aligned_end = max(t.end for t in entity_tokens)
            
            if aligned_start != entity_start or aligned_end != entity_end:
                # Entity không align với token boundaries
                aligned_value = text[aligned_start:aligned_end]
                issues.append({
                    "text": text,
                    "entity": entity_value,
                    "type": "misaligned",
                    "entity_start": entity_start,
                    "entity_end": entity_end,
                    "aligned_start": aligned_start,
                    "aligned_end": aligned_end,
                    "aligned_value": aligned_value,
                    "tokens": [(t.start, t.end, t.text) for t in entity_tokens]
                })
    
    print(f"\n📊 Kết quả:")
    print(f"   - Tổng số entities: {total_entities}")
    print(f"   - Issues found: {len(issues)}")
    
    if issues:
        print(f"\n⚠️ Các issues tìm thấy:")
        for i, issue in enumerate(issues[:20], 1):  # Chỉ hiển thị 20 đầu tiên
            print(f"\n   {i}. Type: {issue['type']}")
            print(f"      Text: {issue['text'][:80]}...")
            print(f"      Entity: '{issue['entity']}'")
            if issue['type'] == 'misaligned':
                print(f"      Current: ({issue['entity_start']}, {issue['entity_end']})")
                print(f"      Should be: ({issue['aligned_start']}, {issue['aligned_end']}) = '{issue['aligned_value']}'")
            print(f"      Tokens: {issue.get('tokens', [])[:5]}...")
    else:
        print(f"\n✅ Không tìm thấy issues! Tất cả entities đã align đúng.")
    
    return len(issues)


def main():
    """Main function"""
    nlu_file = Path("data/nlu.yml")
    
    if not nlu_file.exists():
        print(f"❌ File không tồn tại: {nlu_file}")
        sys.exit(1)
    
    issue_count = check_entity_alignments(nlu_file)
    
    if issue_count > 0:
        print(f"\n💡 Để fix các issues, chạy:")
        print(f"   python scripts/training/fix_entity_alignments.py data/nlu.yml")
        sys.exit(1)
    else:
        print(f"\n✅ Training data đã sẵn sàng!")
        sys.exit(0)


if __name__ == '__main__':
    main()

