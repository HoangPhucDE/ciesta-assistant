#!/usr/bin/env python3
"""
Script test để kiểm tra .env có được load đúng không
Chạy: python test_env_loading.py
"""

import os
import sys

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("🔍 KIỂM TRA LOAD .ENV FILE")
print("=" * 60)

# Test 1: Load .env
print("\n1️⃣ Loading .env file...")
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"   ✅ Loaded .env from: {env_path}")
    else:
        load_dotenv()
        print(f"   ⚠️  .env file not found at {env_path}, trying current directory...")
        if os.path.exists('.env'):
            print(f"   ✅ Found .env in current directory")
        else:
            print(f"   ❌ .env file not found!")
except ImportError:
    print("   ❌ python-dotenv not installed!")
    print("   💡 Run: pip install python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"   ❌ Error loading .env: {e}")
    sys.exit(1)

# Test 2: Kiểm tra các biến môi trường
print("\n2️⃣ Checking environment variables...")

providers = {
    "GROQ_API_KEY": "groq",
    "OPENAI_API_KEY": "openai",
    "HUGGINGFACE_API_KEY": "huggingface",
    "TOGETHER_API_KEY": "together",
    "GOOGLE_API_KEY": "gemini",
}

found_keys = []
for key, provider in providers.items():
    value = os.getenv(key)
    if value:
        # Chỉ hiển thị 10 ký tự đầu để bảo mật
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"   ✅ {key}: {masked}")
        found_keys.append(provider)
    else:
        print(f"   ❌ {key}: NOT SET")

# Test 3: Kiểm tra LLM_PROVIDER
print("\n3️⃣ Checking LLM_PROVIDER...")
llm_provider = os.getenv("LLM_PROVIDER", "NOT SET")
print(f"   LLM_PROVIDER: {llm_provider}")

if llm_provider == "NOT SET":
    print("   ⚠️  LLM_PROVIDER not set! Default will be 'openai'")
elif llm_provider.lower() not in ["groq", "openai", "huggingface", "together", "gemini", "ollama", "auto"]:
    print(f"   ⚠️  Unknown provider: {llm_provider}")

# Test 4: Kiểm tra tương thích
print("\n4️⃣ Compatibility check...")
if llm_provider != "NOT SET":
    provider_lower = llm_provider.lower()
    if provider_lower == "groq":
        if "GROQ_API_KEY" not in [k for k in providers.keys() if os.getenv(k)]:
            print("   ❌ LLM_PROVIDER=groq but GROQ_API_KEY not set!")
        else:
            print("   ✅ Groq setup looks good!")
    elif provider_lower == "openai":
        if "OPENAI_API_KEY" not in [k for k in providers.keys() if os.getenv(k)]:
            print("   ❌ LLM_PROVIDER=openai but OPENAI_API_KEY not set!")
        else:
            print("   ✅ OpenAI setup looks good!")
    elif provider_lower == "huggingface":
        if "HUGGINGFACE_API_KEY" not in [k for k in providers.keys() if os.getenv(k)]:
            print("   ❌ LLM_PROVIDER=huggingface but HUGGINGFACE_API_KEY not set!")
        else:
            print("   ✅ Hugging Face setup looks good!")
    elif provider_lower == "together":
        if "TOGETHER_API_KEY" not in [k for k in providers.keys() if os.getenv(k)]:
            print("   ❌ LLM_PROVIDER=together but TOGETHER_API_KEY not set!")
        else:
            print("   ✅ Together AI setup looks good!")
    elif provider_lower == "gemini":
        if "GOOGLE_API_KEY" not in [k for k in providers.keys() if os.getenv(k)]:
            print("   ❌ LLM_PROVIDER=gemini but GOOGLE_API_KEY not set!")
        else:
            print("   ✅ Gemini setup looks good!")
    elif provider_lower == "ollama":
        print("   ✅ Ollama (local) - no API key needed")
    elif provider_lower == "auto":
        print("   ✅ Auto mode - will try all providers")

# Test 5: Test RAG synthesis
print("\n5️⃣ Testing RAG synthesis...")
try:
    from rag.retriever import RAGRetriever
    
    # Test với dummy data
    print("   Loading RAG retriever...")
    retriever = RAGRetriever('data/knowledge_base/provinces')
    print("   ✅ RAG retriever loaded")
    
    # Test search
    print("   Testing search...")
    results = retriever.search("Đà Nẵng", top_k=2)
    print(f"   ✅ Found {len(results)} results")
    
    # Test synthesis
    print("   Testing synthesis (this will call LLM if API key is set)...")
    if results:
        answer = retriever.synthesize("Đà Nẵng có gì đẹp?", results)
        if "Tôi chưa có câu trả lời trực tiếp" in answer:
            print("   ⚠️  LLM not used - falling back to simple extraction")
            print("   💡 Check: API key có đúng không? LLM_PROVIDER có đúng không?")
        else:
            print("   ✅ LLM synthesis successful!")
            print(f"   Preview: {answer[:100]}...")
    else:
        print("   ⚠️  No results to synthesize")
        
except Exception as e:
    print(f"   ❌ Error testing RAG: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)

if found_keys:
    print(f"✅ Found API keys for: {', '.join(found_keys)}")
else:
    print("❌ No API keys found in .env")

if llm_provider != "NOT SET":
    print(f"✅ LLM_PROVIDER: {llm_provider}")
else:
    print("⚠️  LLM_PROVIDER not set (will default to 'openai')")

print("\n💡 Next steps:")
if not found_keys:
    print("   1. Create .env file in project root")
    print("   2. Add your API key (e.g., GROQ_API_KEY=your-key)")
    print("   3. Set LLM_PROVIDER (e.g., LLM_PROVIDER=groq)")
    print("   4. Restart action server: rasa run actions")
else:
    print("   1. Restart action server: rasa run actions")
    print("   2. Test with out_of_scope message")
    print("   3. Check action server logs for '[RAG] Provider: ...'")

print("=" * 60)

