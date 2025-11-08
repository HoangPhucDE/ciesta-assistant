#!/bin/bash
# Quick Push Script - Copy và chạy script này

echo "=========================================="
echo "🚀 Quick Push to GitHub"
echo "=========================================="
echo ""

# Kiểm tra branch
BRANCH=$(git branch --show-current)
echo "📌 Branch hiện tại: $BRANCH"
echo ""

# Kiểm tra status
echo "📊 Git Status:"
git status --short
echo ""

# Kiểm tra commits chưa push
echo "📝 Commits chưa push:"
git log origin/$BRANCH..$BRANCH --oneline 2>/dev/null || echo "Không có commits mới hoặc branch remote chưa tồn tại"
echo ""

# Hỏi xác nhận
read -p "Bạn có muốn push lên origin/$BRANCH? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Hủy bỏ."
    exit 1
fi

echo ""
echo "🔄 Đang push..."
echo ""

# Thử push
if git push origin $BRANCH; then
    echo ""
    echo "✅ Push thành công!"
    echo ""
    echo "🔗 Xem trên GitHub:"
    echo "   https://github.com/HoangPhucDE/ciesta-assistant/tree/$BRANCH"
else
    echo ""
    echo "❌ Push thất bại!"
    echo ""
    echo "💡 Các cách giải quyết:"
    echo "   1. Sử dụng Personal Access Token:"
    echo "      - Tạo token tại: https://github.com/settings/tokens"
    echo "      - Dùng token làm password khi push"
    echo ""
    echo "   2. Setup SSH:"
    echo "      git remote set-url origin git@github.com:HoangPhucDE/ciesta-assistant.git"
    echo "      git push origin $BRANCH"
    echo ""
    echo "   3. Xem hướng dẫn chi tiết: cat PUSH_TO_GITHUB.md"
fi


