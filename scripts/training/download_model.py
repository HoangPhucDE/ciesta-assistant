# FILE: download_model.py

from huggingface_hub import snapshot_download

# Tên model trên Hugging Face Hub
repo_id = "vinai/phobert-base"
# Thư mục trên máy bạn để lưu model
local_dir = "models_hub/phobert-base"

print(f"Bắt đầu tải về mô hình '{repo_id}'...")
print(f"Lưu vào thư mục: '{local_dir}'")
print("Quá trình này có thể mất RẤT NHIỀU thời gian tùy vào tốc độ mạng, vui lòng kiên nhẫn.")

# Lệnh chính để tải toàn bộ model
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False, # Quan trọng: để copy file thay vì tạo symlink
    resume_download=True # Tự động tải tiếp nếu bị ngắt kết nối
)

print("\n🎉 Tải về hoàn tất! Thư mục 'models_hub/phobert-base' đã sẵn sàng.")