#!/usr/bin/env python3
"""
Script để fix entity alignment trong training data sử dụng Rasa's tokenizer
Điều chỉnh entity annotations để khớp với token boundaries

Cách sử dụng:
    python scripts/training/fix_entity_alignments_rasa.py data/nlu.yml

Hoặc trên Colab:
    !python scripts/training/fix_entity_alignments_rasa.py data/nlu.yml
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional

# Try to import Rasa components
try:
    from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
    from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
    from rasa.shared.nlu.training_data.training_data import TrainingData
    RASA_AVAILABLE = True
except ImportError:
    RASA_AVAILABLE = False
    print("⚠️ Rasa không được cài đặt, sẽ sử dụng tokenizer đơn giản")


def simple_tokenize(text: str) -> List[Tuple[int, int, str]]:
    """
    Simple whitespace tokenizer (fallback nếu không có Rasa)
    """
    tokens = []
    words = text.split()
    current_pos = 0
    
    for word in words:
        start = text.find(word, current_pos)
        if start == -1:
            start = current_pos
            while start < len(text) and text[start].isspace():
                start += 1
            if start >= len(text):
                break
        end = start + len(word)
        tokens.append((start, end, word))
        current_pos = end
    
    return tokens


def fix_entity_alignment_rasa(text: str, entity_value: str, entity_type: str) -> Optional[str]:
    """
    Fix entity alignment sử dụng Rasa tokenizer nếu có
    """
    if not RASA_AVAILABLE:
        # Fallback: sử dụng simple tokenizer
        tokens = simple_tokenize(text)
        
        # Tìm entity value trong text
        entity_words = entity_value.split()
        token_texts = [t[2] for t in tokens]
        
        # Tìm sequence khớp
        for i in range(len(token_texts) - len(entity_words) + 1):
            match = True
            for j, ew in enumerate(entity_words):
                if i + j >= len(token_texts):
                    match = False
                    break
                if token_texts[i + j].lower() != ew.lower():
                    match = False
                    break
            
            if match:
                start_token = tokens[i]
                end_token = tokens[i + len(entity_words) - 1]
                aligned_value = text[start_token[0]:end_token[1]]
                if aligned_value != entity_value:
                    return aligned_value
        
        return None
    
    # Sử dụng Rasa tokenizer
    tokenizer = WhitespaceTokenizer()
    message_data = {"text": text}
    
    # Tokenize
    tokens = tokenizer.tokenize(message_data, attribute="text")
    
    # Tìm tokens khớp với entity
    entity_words = entity_value.split()
    token_texts = [t.text for t in tokens]
    
    # Tìm sequence
    for i in range(len(token_texts) - len(entity_words) + 1):
        match = True
        for j, ew in enumerate(entity_words):
            if i + j >= len(token_texts):
                match = False
                break
            if token_texts[i + j].lower() != ew.lower():
                match = False
                break
        
        if match:
            start_token = tokens[i]
            end_token = tokens[i + len(entity_words) - 1]
            aligned_value = text[start_token.start:end_token.end]
            if aligned_value != entity_value:
                return aligned_value
    
    return None


def fix_example_line(line: str) -> str:
    """
    Fix một dòng example
    """
    # Parse entity pattern: [value](type)
    entity_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    entities = re.findall(entity_pattern, line)
    
    if not entities:
        return line
    
    # Lấy text gốc (thay [entity](type) bằng entity value)
    text_only = re.sub(entity_pattern, r'\1', line)
    
    fixed_line = line
    
    # Fix từng entity
    for entity_value, entity_type in entities:
        # Tìm alignment tốt hơn
        aligned_value = fix_entity_alignment_rasa(text_only, entity_value, entity_type)
        
        if aligned_value and aligned_value != entity_value:
            # Thay thế annotation
            old_annotation = f'[{entity_value}]({entity_type})'
            new_annotation = f'[{aligned_value}]({entity_type})'
            fixed_line = fixed_line.replace(old_annotation, new_annotation, 1)
    
    return fixed_line


def fix_nlu_file_rasa(input_file: Path, output_file: Path = None):
    """
    Fix entity alignments sử dụng Rasa nếu có thể
    """
    if output_file is None:
        output_file = input_file
    
    print(f"📖 Đọc file: {input_file}")
    
    if RASA_AVAILABLE:
        # Sử dụng Rasa's training data reader
        try:
            reader = RasaYAMLReader()
            training_data = reader.read(input_file)
            
            print(f"🔍 Đang xử lý {len(training_data.training_examples)} examples...")
            
            # Fix từng example
            fixed_count = 0
            for example in training_data.training_examples:
                original_text = example.get("text")
                entities = example.get("entities", [])
                
                if not entities:
                    continue
                
                # Tokenize với WhitespaceTokenizer
                tokenizer = WhitespaceTokenizer()
                message_data = {"text": original_text}
                tokens = tokenizer.tokenize(message_data, attribute="text")
                
                # Fix từng entity
                fixed_entities = []
                for entity in entities:
                    entity_start = entity["start"]
                    entity_end = entity["end"]
                    entity_value = entity["value"]
                    
                    # Tìm tokens nằm trong entity
                    entity_tokens = [
                        t for t in tokens
                        if t.start < entity_end and t.end > entity_start
                    ]
                    
                    if entity_tokens:
                        # Align với token boundaries
                        aligned_start = min(t.start for t in entity_tokens)
                        aligned_end = max(t.end for t in entity_tokens)
                        aligned_value = original_text[aligned_start:aligned_end]
                        
                        if aligned_value != entity_value:
                            entity["start"] = aligned_start
                            entity["end"] = aligned_end
                            entity["value"] = aligned_value
                            fixed_count += 1
                    
                    fixed_entities.append(entity)
                
                example.set("entities", fixed_entities)
            
            print(f"✅ Đã fix {fixed_count} entities")
            
            # Save lại file
            # Note: Rasa không có writer trực tiếp cho YAML, nên sẽ dùng cách khác
            print("💾 Đang ghi file...")
            # Tạm thời sẽ dùng cách đọc và sửa file YAML trực tiếp
            
        except Exception as e:
            print(f"❌ Lỗi khi sử dụng Rasa: {e}")
            print("   Sử dụng phương pháp đơn giản hơn...")
            RASA_AVAILABLE = False
    
    if not RASA_AVAILABLE:
        # Phương pháp đơn giản: đọc file YAML và sửa từng dòng
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        fixed_count = 0
        
        for line in lines:
            original_line = line
            # Chỉ fix các dòng có entity annotations
            if '[' in line and '](' in line:
                fixed_line = fix_example_line(line.rstrip('\n'))
                if fixed_line != line.rstrip('\n'):
                    fixed_count += 1
                fixed_lines.append(fixed_line + '\n')
            else:
                fixed_lines.append(line)
        
        print(f"✅ Đã fix {fixed_count} examples")
        
        # Backup file gốc
        backup_file = input_file.with_suffix('.yml.bak')
        print(f"💾 Backup file gốc: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Ghi file mới
        print(f"💾 Ghi file mới: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
    
    print("✅ Hoàn tất!")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix entity alignments in NLU training data')
    parser.add_argument('input_file', type=str, help='Input NLU YAML file')
    parser.add_argument('-o', '--output', type=str, default=None, help='Output file')
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ File không tồn tại: {input_path}")
        sys.exit(1)
    
    output_path = Path(args.output) if args.output else input_path
    
    fix_nlu_file_rasa(input_path, output_path)


if __name__ == '__main__':
    main()

