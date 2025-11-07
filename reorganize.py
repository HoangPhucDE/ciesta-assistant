#!/usr/bin/env python3
"""
Script Python để cấu trúc lại thư mục dự án Ciesta
Chạy: python reorganize.py
"""

import os
import shutil
from pathlib import Path

def create_directories(base_path):
    """Tạo các thư mục mới"""
    dirs = [
        "scripts/training",
        "scripts/validation",
        "scripts/debug",
        "docs/guides",
        "docs/troubleshooting",
        "docs/api",
        "config/rasa",
    ]
    
    for dir_path in dirs:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {dir_path}")

def move_file(src, dst, base_path):
    """Di chuyển file nếu tồn tại"""
    src_path = base_path / src
    dst_path = base_path / dst
    
    if src_path.exists():
        if dst_path.exists():
            print(f"⚠️  Skipping {src} (destination exists)")
            return False
        shutil.move(str(src_path), str(dst_path))
        print(f"✅ Moved: {src} → {dst}")
        return True
    else:
        print(f"⚠️  Skipping {src} (not found)")
        return False

def create_symlink(src, dst, base_path):
    """Tạo symlink (hoặc copy nếu symlink không được hỗ trợ)"""
    src_path = base_path / src
    dst_path = base_path / dst
    
    if not src_path.exists():
        print(f"⚠️  Cannot create symlink: {src} not found")
        return False
    
    if dst_path.exists() or dst_path.is_symlink():
        print(f"⚠️  Symlink already exists: {dst}")
        return False
    
    try:
        dst_path.symlink_to(src_path)
        print(f"✅ Created symlink: {dst} → {src}")
        return True
    except OSError:
        # Nếu symlink không được hỗ trợ, copy file
        shutil.copy2(str(src_path), str(dst_path))
        print(f"✅ Copied (symlink not supported): {dst} → {src}")
        return True

def main():
    """Hàm chính"""
    base_path = Path(__file__).parent
    
    print("🔄 Bắt đầu cấu trúc lại thư mục...")
    print("=" * 60)
    
    # 1. Tạo các thư mục mới
    print("\n📁 Tạo các thư mục mới...")
    create_directories(base_path)
    
    # 2. Di chuyển các file markdown
    print("\n📄 Di chuyển các file markdown...")
    markdown_files = [
        ("TRAIN_MODEL.md", "docs/guides/TRAIN_MODEL.md"),
        ("DEBUG_RAG.md", "docs/troubleshooting/DEBUG_RAG.md"),
        ("QUICK_FIX_RAG.md", "docs/troubleshooting/QUICK_FIX_RAG.md"),
        ("CHECK_ACTION_SERVER.md", "docs/troubleshooting/CHECK_ACTION_SERVER.md"),
    ]
    
    for src, dst in markdown_files:
        move_file(src, dst, base_path)
    
    # 3. Di chuyển các script
    print("\n🔧 Di chuyển các script...")
    script_files = [
        ("debug_rag.py", "scripts/debug/debug_rag.py"),
        ("test_env_loading.py", "scripts/debug/test_env_loading.py"),
        ("validate_knowledge_base.py", "scripts/validation/validate_knowledge_base.py"),
        ("download_model.py", "scripts/training/download_model.py"),
    ]
    
    for src, dst in script_files:
        move_file(src, dst, base_path)
    
    # 4. Di chuyển config Rasa
    print("\n⚙️  Tổ chức config Rasa...")
    config_files = [
        ("config.yml", "config/rasa/config.yml"),
        ("domain.yml", "config/rasa/domain.yml"),
        ("endpoints.yml", "config/rasa/endpoints.yml"),
        ("credentials.yml", "config/rasa/credentials.yml"),
    ]
    
    for src, dst in config_files:
        if move_file(src, dst, base_path):
            # Tạo symlink về root
            create_symlink(dst, src, base_path)
    
    print("\n" + "=" * 60)
    print("✅ Hoàn tất cấu trúc lại thư mục!")
    print("\n📋 Cấu trúc mới:")
    print("  scripts/          - Các script tiện ích")
    print("    training/       - Script training model")
    print("    validation/     - Script validation")
    print("    debug/          - Script debug")
    print("  docs/             - Tài liệu")
    print("    guides/         - Hướng dẫn")
    print("    troubleshooting/ - Xử lý lỗi")
    print("    api/            - API docs")
    print("  config/rasa/      - Config Rasa (với symlink về root)")
    print("\n💡 Lưu ý:")
    print("  - Các file config Rasa đã được tạo symlink về root")
    print("  - Rasa vẫn có thể tìm thấy config ở root")
    print("  - Kiểm tra lại các import paths nếu cần")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Đã hủy bởi người dùng")
    except Exception as e:
        print(f"\n\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

