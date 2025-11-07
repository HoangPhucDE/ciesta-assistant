#!/usr/bin/env python3
"""
Script debug để kiểm tra tại sao RAG fallback không gọi được
Chạy: python debug_rag.py
"""

import os
import sys

# Load .env
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ Loaded .env from: {env_path}")
    else:
        load_dotenv()
        if os.path.exists('.env'):
            print(f"✅ Found .env in current directory")
        else:
            print(f"❌ .env file not found!")
except ImportError:
    print("❌ python-dotenv not installed!")
    sys.exit(1)

print("\n" + "=" * 60)
print("🔍 DEBUG RAG FALLBACK")
print("=" * 60)

# 1. Kiểm tra API key
print("\n1️⃣ Checking API Keys...")
groq_key = os.getenv("GROQ_API_KEY")
llm_provider = os.getenv("LLM_PROVIDER", "openai")

if groq_key:
    masked = groq_key[:10] + "..." if len(groq_key) > 10 else groq_key
    print(f"   ✅ GROQ_API_KEY: {masked}")
else:
    print(f"   ❌ GROQ_API_KEY: NOT SET")

print(f"   LLM_PROVIDER: {llm_provider}")

if llm_provider.lower() == "groq" and not groq_key:
    print("   ❌ LLM_PROVIDER=groq but GROQ_API_KEY not set!")
elif llm_provider.lower() != "groq":
    print(f"   ⚠️  LLM_PROVIDER={llm_provider}, not 'groq'")

# 2. Kiểm tra RAG retriever
print("\n2️⃣ Checking RAG Retriever...")
try:
    from rag.retriever import RAGRetriever
    kb_dir = os.path.join(os.getcwd(), "data/knowledge_base/provinces")
    if os.path.exists(kb_dir):
        print(f"   ✅ KB directory exists: {kb_dir}")
        json_files = [f for f in os.listdir(kb_dir) if f.endswith('.json')]
        print(f"   ✅ Found {len(json_files)} JSON files")
        
        try:
            retriever = RAGRetriever(kb_dir=kb_dir)
            print("   ✅ RAG retriever initialized successfully")
        except Exception as e:
            print(f"   ❌ Failed to initialize retriever: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ❌ KB directory not found: {kb_dir}")
except ImportError as e:
    print(f"   ❌ Failed to import RAGRetriever: {e}")

# 3. Test RAG synthesis
print("\n3️⃣ Testing RAG Synthesis...")
if groq_key and llm_provider.lower() == "groq":
    try:
        from rag.retriever import RAGRetriever
        kb_dir = os.path.join(os.getcwd(), "data/knowledge_base/provinces")
        retriever = RAGRetriever(kb_dir=kb_dir)
        
        # Test search
        print("   Testing search...")
        results = retriever.search("Đà Nẵng có gì đẹp?", top_k=3)
        print(f"   ✅ Found {len(results)} results")
        if results:
            print(f"   Top score: {results[0][0]:.3f}")
            
            # Test synthesis
            print("   Testing synthesis with Groq...")
            answer = retriever.synthesize("Đà Nẵng có gì đẹp?", results)
            if "Tôi chưa có câu trả lời trực tiếp" in answer:
                print("   ⚠️  LLM not used - falling back to simple extraction")
                print("   💡 Check: API key có đúng không? Groq package có cài không?")
            else:
                print("   ✅ LLM synthesis successful!")
                print(f"   Preview: {answer[:100]}...")
    except Exception as e:
        print(f"   ❌ Error testing RAG: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ⚠️  Skipping synthesis test (API key or provider not set)")

# 4. Kiểm tra action server
print("\n4️⃣ Action Server Check...")
print("   💡 Để RAG fallback hoạt động:")
print("   1. Đảm bảo .env có GROQ_API_KEY và LLM_PROVIDER=groq")
print("   2. Restart action server: rasa run actions")
print("   3. Test với message có intent out_of_scope hoặc nlu_fallback")
print("   4. Check action server logs để xem '[RAG] Provider: ...'")

# 5. Kiểm tra intent
print("\n5️⃣ Intent Check...")
print("   💡 RAG fallback chỉ chạy khi intent là:")
print("   • out_of_scope")
print("   • nlu_fallback")
print("   ")
print("   Nếu intent khác, action sẽ return sớm.")
print("   Check rules.yml để xem rule nào gọi action_rag_fallback")

# 6. Kiểm tra confidence threshold
print("\n6️⃣ Confidence Threshold...")
rag_threshold = float(os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.55"))
print(f"   RAG_CONFIDENCE_THRESHOLD: {rag_threshold}")
print("   💡 Nếu confidence score < threshold, RAG sẽ không gọi LLM")

print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)

if groq_key and llm_provider.lower() == "groq":
    print("✅ API key và provider đã được set đúng")
    print("💡 Next steps:")
    print("   1. Restart action server: rasa run actions")
    print("   2. Test với message out_of_scope (ví dụ: 'giá vàng hôm nay')")
    print("   3. Check action server logs")
else:
    print("❌ API key hoặc provider chưa đúng")
    print("💡 Fix:")
    print("   1. Tạo/update .env file với:")
    print("      GROQ_API_KEY=your-key-here")
    print("      LLM_PROVIDER=groq")
    print("   2. Restart action server")

print("=" * 60)

