#!/usr/bin/env python3
"""
Test script for RAG chatbot setup and functionality.
"""

import os
from dotenv import load_dotenv
from rag_chatbot import RAGChatbot

def test_setup():
    """Test the RAG chatbot setup."""
    print("🧪 Testing RAG Chatbot Setup...")
    print("=" * 40)
    
    # Test 1: Environment variables
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print("✅ OPENAI_API_KEY found")
    else:
        print("❌ OPENAI_API_KEY not found")
        return False
    
    # Test 2: Initialize chatbot
    try:
        chatbot = RAGChatbot()
        print("✅ RAGChatbot initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAGChatbot: {e}")
        return False
    
    # Test 3: Check ChromaDB connection
    try:
        count = chatbot.collection.count()
        print(f"✅ ChromaDB connection successful (collection has {count} items)")
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False
    
    # Test 4: Test document loading
    try:
        chatbot.load_documents()
        new_count = chatbot.collection.count()
        print(f"✅ Document loading successful (now {new_count} items)")
    except Exception as e:
        print(f"❌ Document loading failed: {e}")
        return False
    
    # Test 5: Test simple query
    try:
        test_question = "What is this document about?"
        answer = chatbot.query(test_question)
        print(f"✅ Query test successful")
        print(f"   Q: {test_question}")
        print(f"   A: {answer[:100]}...")
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False
    
    print("\n🎉 All tests passed! RAG chatbot is ready to use.")
    return True

if __name__ == "__main__":
    test_setup() 