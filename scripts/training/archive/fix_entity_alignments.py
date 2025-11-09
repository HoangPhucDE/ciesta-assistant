#!/usr/bin/env python3
"""
Script để fix entity alignment trong training data
Điều chỉnh entity annotations để khớp với token boundaries của WhitespaceTokenizer

Vấn đề: Entity annotations trong format [value](type) có thể không khớp với token boundaries
sau khi tokenize, gây ra warnings "Misaligned entity annotation"

Giải pháp: 
1. Sử dụng Rasa's tokenizer để tokenize text
2. Điều chỉnh entity annotations để chỉ bao gồm các tokens hoàn chỉnh
3. Loại bỏ các ký tự thừa (whitespace, punctuation) khỏi entity boundaries
"""

import re
import yaml
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import sys


def tokenize_whitespace(text: str) -> List[Tuple[int, int, str]]:
    """
    Tokenize text theo whitespace (giống WhitespaceTokenizer của Rasa)
    Trả về list (start, end, token)
    """
    tokens = []
    words = text.split()
    current_pos = 0
    
    for word in words:
        # Tìm vị trí của word trong text (tính từ current_pos để tránh trùng)
        start = text.find(word, current_pos)
        if start == -1:
            # Fallback: skip whitespace từ current_pos
            start = current_pos
            while start < len(text) and text[start].isspace():
                start += 1
            if start >= len(text):
                break
        
        end = start + len(word)
        tokens.append((start, end, word))
        current_pos = end
    
    return tokens


def strip_punctuation(text: str) -> str:
    """Loại bỏ punctuation ở đầu và cuối text"""
    import string
    # Vietnamese punctuation + English punctuation
    punctuation = string.punctuation + '.,;:!?。，；：！？'
    return text.strip(punctuation)


def find_best_token_alignment(
    text: str,
    entity_value: str,
    tokens: List[Tuple[int, int, str]]
) -> Optional[Tuple[int, int, str]]:
    """
    Tìm alignment tốt nhất cho entity value với tokens
    Trả về (start, end, aligned_value) hoặc None
    
    Loại bỏ punctuation từ entity boundaries để tránh misalignment
    """
    # Normalize: loại bỏ spaces và punctuation thừa
    entity_value_clean = strip_punctuation(entity_value.strip())
    entity_words = entity_value_clean.split()
    
    if not entity_words:
        return None
    
    # Case 1: Single word entity
    if len(entity_words) == 1:
        entity_word = entity_words[0]
        for token_start, token_end, token_text in tokens:
            token_clean = strip_punctuation(token_text)
            # So sánh không phân biệt hoa thường, loại bỏ punctuation
            if token_clean.lower() == entity_word.lower():
                # Trả về token không có punctuation
                return (token_start, token_end, token_clean)
        # Không tìm thấy exact match, thử tìm partial match (không có punctuation)
        for token_start, token_end, token_text in tokens:
            token_clean = strip_punctuation(token_text)
            if entity_word.lower() in token_clean.lower() or token_clean.lower() in entity_word.lower():
                return (token_start, token_end, token_clean)
    
    # Case 2: Multi-word entity
    # Tìm sequence of tokens khớp với entity words (loại bỏ punctuation)
    token_texts_clean = [strip_punctuation(t[2]) for t in tokens]
    
    # Tìm vị trí bắt đầu của sequence
    for i in range(len(token_texts_clean) - len(entity_words) + 1):
        # Kiểm tra xem sequence từ i có khớp không
        match = True
        matching_tokens = []
        for j, entity_word in enumerate(entity_words):
            if i + j >= len(token_texts_clean):
                match = False
                break
            token_clean = token_texts_clean[i + j]
            # So sánh không phân biệt hoa thường
            if token_clean.lower() != entity_word.lower():
                match = False
                break
            matching_tokens.append(tokens[i + j])
        
        if match and matching_tokens:
            # Tìm thấy sequence khớp
            start_token = matching_tokens[0]
            end_token = matching_tokens[-1]
            aligned_start = start_token[0]
            aligned_end = end_token[1]
            # Extract value từ text, loại bỏ punctuation ở boundaries
            aligned_value_raw = text[aligned_start:aligned_end]
            aligned_value = ' '.join([strip_punctuation(t[2]) for t in matching_tokens])
            return (aligned_start, aligned_end, aligned_value)
    
    # Case 3: Tìm trong text (có thể có format khác)
    # Tìm vị trí của entity_value trong text (case insensitive, loại bỏ punctuation)
    text_lower = text.lower()
    entity_lower = entity_value_clean.lower()
    
    # Tìm các vị trí có thể khớp
    pos = text_lower.find(entity_lower)
    if pos != -1:
        # Tìm tokens nằm trong khoảng này
        entity_start = pos
        entity_end = pos + len(entity_value_clean)
        
        overlapping_tokens = []
        for token_start, token_end, token_text in tokens:
            # Token overlaps với entity (tính cả punctuation)
            if token_start < entity_end + 2 and token_end > entity_start - 2:
                overlapping_tokens.append((token_start, token_end, token_text))
        
        if overlapping_tokens:
            # Lọc tokens để chỉ lấy những token có text khớp
            matching_tokens = []
            for token_start, token_end, token_text in overlapping_tokens:
                token_clean = strip_punctuation(token_text).lower()
                if any(token_clean == ew.lower() for ew in entity_words):
                    matching_tokens.append((token_start, token_end, token_text))
            
            if matching_tokens:
                aligned_start = min(t[0] for t in matching_tokens)
                aligned_end = max(t[1] for t in matching_tokens)
                aligned_value = ' '.join([strip_punctuation(t[2]) for t in matching_tokens])
                return (aligned_start, aligned_end, aligned_value)
    
    return None


def fix_entity_in_example(example: str) -> str:
    """
    Fix entity annotations trong một example
    Format: "text with [entity](type)"
    """
    # Parse entities từ format [value](type)
    entity_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    entities = re.findall(entity_pattern, example)
    
    if not entities:
        return example  # Không có entities
    
    # Lấy text gốc (thay thế [entity](type) bằng entity value)
    text_only = re.sub(entity_pattern, r'\1', example)
    
    # Tokenize text
    tokens = tokenize_whitespace(text_only)
    
    if not tokens:
        return example
    
    # Fix từng entity (xử lý từ cuối lên để tránh offset issues)
    fixed_example = example
    
    for entity_value, entity_type in reversed(entities):
        # Clean entity value (loại bỏ punctuation)
        entity_clean = strip_punctuation(entity_value.strip())
        entity_words = entity_clean.split()
        
        if not entity_words:
            continue
        
        # Tìm entity trong tokens (không có punctuation)
        token_texts_clean = [strip_punctuation(t[2]) for t in tokens]
        
        # Tìm sequence khớp
        found_match = False
        for i in range(len(token_texts_clean) - len(entity_words) + 1):
            # Kiểm tra sequence
            match = True
            matching_tokens = []
            for j, ew in enumerate(entity_words):
                if i + j >= len(token_texts_clean):
                    match = False
                    break
                if token_texts_clean[i + j].lower() != ew.lower():
                    match = False
                    break
                matching_tokens.append(tokens[i + j])
            
            if match and matching_tokens:
                # Tìm thấy match - tạo aligned value từ tokens (không có punctuation)
                aligned_value = ' '.join([strip_punctuation(t[2]) for t in matching_tokens])
                
                # Chỉ fix nếu giá trị khác (không phân biệt hoa thường)
                if aligned_value.strip().lower() != entity_clean.strip().lower():
                    old_annotation = f'[{entity_value}]({entity_type})'
                    new_annotation = f'[{aligned_value}]({entity_type})'
                    fixed_example = fixed_example.replace(old_annotation, new_annotation, 1)
                    found_match = True
                    break
        
        # Nếu không tìm thấy match, thử với các aliases phổ biến
        if not found_match:
            # Map các aliases
            entity_aliases_map = {
                'TP.HCM': ['thành phố hcm', 'hcm'],
                'TP HCM': ['thành phố hcm', 'hcm'],
                'HCM': ['hcm', 'thành phố hcm'],
                'Sai Gon': ['sài gòn', 'sai gon'],
            }
            
            if entity_value in entity_aliases_map:
                for alias in entity_aliases_map[entity_value]:
                    alias_words = alias.split()
                    for i in range(len(token_texts_clean) - len(alias_words) + 1):
                        match = True
                        matching_tokens = []
                        for j, aw in enumerate(alias_words):
                            if i + j >= len(token_texts_clean):
                                match = False
                                break
                            if token_texts_clean[i + j].lower() != aw.lower():
                                match = False
                                break
                            matching_tokens.append(tokens[i + j])
                        
                        if match and matching_tokens:
                            aligned_value = ' '.join([strip_punctuation(t[2]) for t in matching_tokens])
                            old_annotation = f'[{entity_value}]({entity_type})'
                            new_annotation = f'[{aligned_value}]({entity_type})'
                            fixed_example = fixed_example.replace(old_annotation, new_annotation, 1)
                            found_match = True
                            break
                    
                    if found_match:
                        break
    
    return fixed_example


def fix_nlu_file(input_file: Path, output_file: Path = None):
    """
    Fix entity alignments trong file nlu.yml
    
    Cách tiếp cận:
    1. Đọc file YAML
    2. Với mỗi example có entity annotations, tokenize text
    3. Điều chỉnh entity annotations để khớp với token boundaries
    4. Ghi lại file
    """
    if output_file is None:
        output_file = input_file
    
    print(f"📖 Đọc file: {input_file}")
    
    # Backup file gốc
    backup_file = input_file.with_suffix('.yml.bak')
    if not backup_file.exists():
        print(f"💾 Backup file gốc: {backup_file}")
        import shutil
        shutil.copy2(input_file, backup_file)
    
    # Đọc file như text để giữ nguyên format
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"🔍 Đang xử lý {len(lines)} dòng...")
    
    fixed_lines = []
    fixed_count = 0
    total_examples = 0
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        
        # Chỉ xử lý các dòng có entity annotations (bắt đầu bằng '- ' và có '[entity](type)')
        if line.strip().startswith('- ') and '[' in line and '](' in line:
            # Extract example (bỏ '- ' ở đầu)
            example = line[2:].strip()
            total_examples += 1
            
            # Fix entity annotations
            fixed_example = fix_entity_in_example(example)
            
            if fixed_example != example:
                fixed_count += 1
                if fixed_count <= 10:  # Chỉ hiển thị 10 examples đầu tiên
                    print(f"   ✅ Line {line_num}: Fixed")
                    print(f"      Old: {example[:60]}...")
                    print(f"      New: {fixed_example[:60]}...")
                
                fixed_lines.append(f"      - {fixed_example}\n")
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    print(f"\n📊 Thống kê:")
    print(f"   - Tổng số examples có entities: {total_examples}")
    print(f"   - Đã fix: {fixed_count}")
    print(f"   - Không cần fix: {total_examples - fixed_count}")
    
    # Write to output file
    print(f"\n💾 Ghi file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ Hoàn tất!")
    print(f"💡 File backup được lưu tại: {backup_file}")
    print(f"💡 Bạn có thể so sánh để xem các thay đổi")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix entity alignments in NLU training data')
    parser.add_argument(
        'input_file',
        type=str,
        help='Input NLU YAML file (e.g., data/nlu.yml)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file (default: overwrite input file)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ File không tồn tại: {input_path}")
        sys.exit(1)
    
    output_path = Path(args.output) if args.output else input_path
    
    fix_nlu_file(input_path, output_path)


if __name__ == '__main__':
    main()

