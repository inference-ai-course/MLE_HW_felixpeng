#!/usr/bin/env python3
"""
RAG Chatbot using ChromaDB and OpenAI
Loads documents from txt_ocr and provides conversational access via terminal.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RAGChatbot:
    def __init__(self, 
                 collection_name: str = "ocr_documents",
                 embedding_model: str = "text-embedding-3-small",
                 chat_model: str = "gpt-3.5-turbo"):
        """
        Initialize the RAG chatbot.
        
        Args:
            collection_name: Name for the ChromaDB collection
            embedding_model: OpenAI embedding model to use
            chat_model: OpenAI chat model to use
        """
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.chat_model = chat_model
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path="./rag/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"description": "OCR documents for RAG chatbot"}
            )
            logger.info(f"Created new collection: {collection_name}")
        
        self.conversation_history = []
    
    def load_documents(self, docs_dir: str = "Class 2/ocr/txt_ocr") -> None:
        """
        Load documents from the specified directory into ChromaDB.
        
        Args:
            docs_dir: Directory containing text files to load
        """
        docs_path = Path(docs_dir)
        if not docs_path.exists():
            logger.error(f"Directory not found: {docs_dir}")
            return
        
        # Find all text files
        text_files = list(docs_path.rglob("*.txt"))
        logger.info(f"Found {len(text_files)} text files to process")
        
        documents = []
        metadatas = []
        ids = []
        
        for i, file_path in enumerate(text_files):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().strip()
                
                if not content:
                    continue
                
                # Create document ID
                doc_id = f"doc_{i:04d}"
                
                # Split content into chunks (simple splitting for now)
                chunks = self._split_text(content, chunk_size=1000, overlap=200)
                
                for j, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_chunk_{j:03d}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(file_path.relative_to(docs_path)),
                        "chunk_id": j,
                        "total_chunks": len(chunks),
                        "file_path": str(file_path)
                    })
                    ids.append(chunk_id)
                
                logger.info(f"Processed {file_path.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        if documents:
            # Add documents to ChromaDB
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} chunks to ChromaDB")
        else:
            logger.warning("No documents to add")
    
    def _split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the end
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def query(self, question: str, top_k: int = 5) -> str:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
            top_k: Number of relevant documents to retrieve
            
        Returns:
            Answer to the question
        """
        try:
            # Search for relevant documents
            results = self.collection.query(
                query_texts=[question],
                n_results=top_k
            )
            
            if not results['documents'] or not results['documents'][0]:
                return "I couldn't find any relevant information to answer your question."
            
            # Prepare context from retrieved documents
            context_parts = []
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i]
                source = metadata.get('source', 'Unknown')
                context_parts.append(f"Source: {source}\nContent: {doc}\n")
            
            context = "\n".join(context_parts)
            
            # Create system prompt
            system_prompt = f"""You are a helpful assistant that answers questions based on the provided context from technical documents. 

Context from documents:
{context}

Instructions:
1. Answer the question based ONLY on the provided context
2. If the context doesn't contain enough information, say so
3. Be concise but thorough
4. If relevant, mention the source document
5. Use a professional, technical tone

Question: {question}"""
            
            # Get response from OpenAI
            response = self.openai_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            answer = response.choices[0].message.content
            
            # Add to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": answer,
                "sources": [m.get('source', 'Unknown') for m in results['metadatas'][0]]
            })
            
            return answer
            
        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

def main():
    """Main function to run the RAG chatbot."""
    print("🤖 RAG Chatbot Initializing...")
    print("=" * 50)
    
    # Initialize chatbot
    chatbot = RAGChatbot()
    
    # Load documents if collection is empty
    collection_count = chatbot.collection.count()
    if collection_count == 0:
        print("📚 Loading documents into ChromaDB...")
        chatbot.load_documents()
        print(f"✅ Loaded {chatbot.collection.count()} document chunks")
    else:
        print(f"✅ Found {collection_count} existing document chunks")
    
    print("\n💬 RAG Chatbot Ready!")
    print("Type 'quit' to exit, 'history' to see conversation history, 'clear' to clear history")
    print("=" * 50)
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif question.lower() == 'history':
                history = chatbot.get_conversation_history()
                if history:
                    print("\n📜 Conversation History:")
                    for i, conv in enumerate(history, 1):
                        print(f"\n{i}. Q: {conv['question']}")
                        print(f"   A: {conv['answer'][:100]}...")
                        print(f"   Sources: {', '.join(conv['sources'])}")
                else:
                    print("No conversation history yet.")
                continue
            elif question.lower() == 'clear':
                chatbot.clear_history()
                print("🗑️  Conversation history cleared.")
                continue
            elif not question:
                continue
            
            print("\n🤔 Thinking...")
            answer = chatbot.query(question)
            print(f"\n💡 Answer: {answer}")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 