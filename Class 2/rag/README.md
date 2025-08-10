# RAG Chatbot System

A Retrieval-Augmented Generation (RAG) chatbot that uses ChromaDB for document storage and OpenAI for question answering.

## 🚀 Features

- **Document Loading**: Automatically loads all text files from `txt_ocr`
- **ChromaDB Storage**: Local, open-source vector database for document storage
- **OpenAI Integration**: Uses OpenAI embeddings and chat models
- **Conversational Interface**: Terminal-based chat interface
- **Source Tracking**: Tracks which documents were used for answers
- **Conversation History**: Maintains chat history with source citations

## 📁 Files

- `rag_chatbot.py` - Main RAG chatbot implementation
- `test_rag.py` - Test script to verify setup
- `chroma_db/` - Local ChromaDB database (created automatically)
- `README.md` - This documentation

## 🛠️ Setup

### 1. Install Dependencies
```bash
pip install chromadb openai python-dotenv
```

### 2. Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Test Setup
```bash
cd rag
python test_rag.py
```

### 4. Run Chatbot
```bash
python rag_chatbot.py
```

## 💬 Usage

### Starting the Chatbot
```bash
python rag_chatbot.py
```

### Commands
- **Ask questions**: Type any question about the documents
- **`history`**: View conversation history with sources
- **`clear`**: Clear conversation history
- **`quit`**: Exit the chatbot

### Example Questions
- "What are the electric service requirements?"
- "How do I install underground conduit?"
- "What are the NEM guidelines?"
- "Tell me about smart inverter requirements"

## 🔧 Configuration

### Model Settings
You can modify these in `rag_chatbot.py`:

```python
chatbot = RAGChatbot(
    collection_name="ocr_documents",           # ChromaDB collection name
    embedding_model="text-embedding-3-small",  # OpenAI embedding model
    chat_model="gpt-3.5-turbo"                # OpenAI chat model
)
```

### Document Processing
- **Chunk Size**: 1000 characters (configurable)
- **Overlap**: 200 characters between chunks
- **Source Tracking**: Automatic metadata tracking

## 📊 How It Works

1. **Document Loading**: 
   - Scans `Class 2/ocr/txt_ocr/` for `.txt` files
   - Splits documents into overlapping chunks
   - Stores in ChromaDB with metadata

2. **Question Processing**:
   - Converts question to embeddings
   - Searches ChromaDB for similar document chunks
   - Retrieves top-k most relevant chunks

3. **Answer Generation**:
   - Sends question + retrieved context to OpenAI
   - Generates answer based on document content
   - Tracks sources used for transparency

## 🎯 Key Features

### Document Management
- **Automatic Loading**: No manual document preparation needed
- **Smart Chunking**: Splits at sentence boundaries when possible
- **Metadata Tracking**: Tracks source files and chunk information

### Conversation Features
- **History Management**: View and clear conversation history
- **Source Citations**: See which documents were used for answers
- **Error Handling**: Graceful handling of API errors and missing documents

### Performance
- **Local Storage**: ChromaDB runs locally, no external database needed
- **Caching**: Documents are stored locally after first load
- **Efficient Retrieval**: Vector similarity search for relevant content

## 🔍 Troubleshooting

### Common Issues

1. **OpenAI API Key Not Found**
   - Ensure `.env` file exists with `OPENAI_API_KEY`
   - Check that `python-dotenv` is installed

2. **ChromaDB Connection Issues**
   - Check write permissions in `rag/` directory
   - Delete `chroma_db/` folder to reset database

3. **No Documents Found**
   - Ensure `Class 2/ocr/txt_ocr/` contains `.txt` files
   - Check file permissions and encoding

### Testing
Run the test script to verify setup:
```bash
python test_rag.py
```

## 📈 Performance Notes

- **First Run**: Document loading may take time depending on file sizes
- **Subsequent Runs**: Fast startup as documents are cached in ChromaDB
- **Query Speed**: Depends on OpenAI API response time
- **Memory Usage**: ChromaDB stores embeddings locally

## 🔄 Updates

The system automatically:
- Loads new documents on first run
- Reuses existing ChromaDB collection
- Maintains conversation history during session
- Tracks document sources for transparency 