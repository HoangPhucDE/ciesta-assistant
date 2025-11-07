# 🔧 Hướng dẫn Push Git

## Vấn đề

Lỗi: `fatal: could not read Username for 'https://github.com': No such device or address`

## Nguyên nhân

Remote đang dùng HTTPS và cần authentication, nhưng không có credential helper được cấu hình.

## Giải pháp

### Option 1: Chuyển sang SSH (Khuyến nghị)

1. **Kiểm tra SSH key:**
   ```bash
   ls -la ~/.ssh/id_rsa.pub
   ```

2. **Nếu chưa có SSH key, tạo mới:**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

3. **Thêm SSH key vào GitHub:**
   ```bash
   cat ~/.ssh/id_rsa.pub
   # Copy output và thêm vào GitHub Settings > SSH and GPG keys
   ```

4. **Chuyển remote sang SSH:**
   ```bash
   git remote set-url origin git@github.com:HoangPhucDE/ciesta-assistant.git
   ```

5. **Push lại:**
   ```bash
   git push -u origin develop
   ```

### Option 2: Dùng Personal Access Token (PAT)

1. **Tạo Personal Access Token trên GitHub:**
   - Settings > Developer settings > Personal access tokens > Tokens (classic)
   - Generate new token với quyền `repo`

2. **Push với token:**
   ```bash
   git push -u origin develop
   # Username: HoangPhucDE
   # Password: <paste your token here>
   ```

3. **Hoặc cấu hình credential helper:**
   ```bash
   git config --global credential.helper store
   git push -u origin develop
   # Nhập username và token một lần, sau đó sẽ được lưu
   ```

### Option 3: Dùng GitHub CLI

```bash
# Cài đặt GitHub CLI (nếu chưa có)
# Ubuntu/Debian:
sudo apt install gh

# Mac:
brew install gh

# Login
gh auth login

# Push
git push -u origin develop
```

## Trạng thái hiện tại

- ✅ Branch `develop` đã được tạo từ `main`
- ✅ Đang ở branch `develop`
- ❌ Chưa push được do authentication

## Lệnh nhanh

```bash
# Chuyển sang SSH (nếu có SSH key)
git remote set-url origin git@github.com:HoangPhucDE/ciesta-assistant.git

# Push branch develop
git push -u origin develop

# Hoặc push main nếu muốn
git checkout main
git push origin main
```

