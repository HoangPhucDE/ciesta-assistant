from transformers import AutoTokenizer, AutoModel
import os

cache_dir = "/ciesta-asisstant/.cache"
os.makedirs(cache_dir, exist_ok=True)

tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", cache_dir=cache_dir)
model = AutoModel.from_pretrained("vinai/phobert-base", cache_dir=cache_dir)

print("PhoBERT đã được tải và lưu vào", cache_dir)