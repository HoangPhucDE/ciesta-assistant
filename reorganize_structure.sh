#!/bin/bash
# Script để cấu trúc lại thư mục dự án

set -e

echo "🔄 Bắt đầu cấu trúc lại thư mục..."

# Tạo các thư mục mới
echo "📁 Tạo các thư mục mới..."
mkdir -p scripts
mkdir -p scripts/training
mkdir -p scripts/validation
mkdir -p scripts/debug
mkdir -p docs/troubleshooting
mkdir -p docs/guides
mkdir -p docs/api

# Di chuyển các file markdown vào docs
echo "📄 Di chuyển các file markdown..."
mv TRAIN_MODEL.md docs/guides/ 2>/dev/null || true
mv DEBUG_RAG.md docs/troubleshooting/ 2>/dev/null || true
mv QUICK_FIX_RAG.md docs/troubleshooting/ 2>/dev/null || true
mv CHECK_ACTION_SERVER.md docs/troubleshooting/ 2>/dev/null || true

# Di chuyển các script vào scripts
echo "🔧 Di chuyển các script..."
mv debug_rag.py scripts/debug/ 2>/dev/null || true
mv test_env_loading.py scripts/debug/ 2>/dev/null || true
mv validate_knowledge_base.py scripts/validation/ 2>/dev/null || true
mv download_model.py scripts/training/ 2>/dev/null || true

# Di chuyển các file trong utils vào scripts nếu cần
echo "📦 Tổ chức utils..."
# Giữ nguyên utils/ vì có thể được import

# Di chuyển các file config Rasa vào thư mục config
echo "⚙️ Tổ chức config..."
mkdir -p config/rasa
mv config.yml config/rasa/ 2>/dev/null || true
mv domain.yml config/rasa/ 2>/dev/null || true
mv endpoints.yml config/rasa/ 2>/dev/null || true
mv credentials.yml config/rasa/ 2>/dev/null || true

# Tạo symlink hoặc copy lại vào root để Rasa vẫn tìm thấy
echo "🔗 Tạo symlink cho Rasa config..."
ln -sf config/rasa/config.yml config.yml 2>/dev/null || true
ln -sf config/rasa/domain.yml domain.yml 2>/dev/null || true
ln -sf config/rasa/endpoints.yml endpoints.yml 2>/dev/null || true
ln -sf config/rasa/credentials.yml credentials.yml 2>/dev/null || true

echo "✅ Hoàn tất cấu trúc lại thư mục!"
echo ""
echo "📋 Cấu trúc mới:"
echo "  scripts/          - Các script tiện ích"
echo "    training/       - Script training model"
echo "    validation/     - Script validation"
echo "    debug/          - Script debug"
echo "  docs/             - Tài liệu"
echo "    guides/         - Hướng dẫn"
echo "    troubleshooting/ - Xử lý lỗi"
echo "    api/            - API docs"
echo "  config/rasa/      - Config Rasa (với symlink về root)"

