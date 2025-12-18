# PaperPilot - AI Research Paper Explainer Bot

A production-ready, domain-specific AI Research Paper Explainer Bot that allows users to upload research paper PDFs and ask questions about them. The system uses Retrieval Augmented Generation (RAG) with Groq LLaMA-3, ChromaDB vector store, and Sentence-Transformers embeddings to provide accurate, context-aware explanations at multiple complexity levels.

![PaperPilot](https://img.shields.io/badge/AI-PaperLens-purple) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green) ![React](https://img.shields.io/badge/React-18.2-blue) ![Groq](https://img.shields.io/badge/Groq-LLaMA--3-orange)

## Features

- 📄 **PDF Upload & Processing**: Upload research papers (up to 50MB) with automatic text extraction
- 🤖 **RAG-Powered Q&A**: Ask questions about papers with Retrieval Augmented Generation
- 🎓 **Multiple Explanation Levels**:
  - **Beginner**: Simple language, analogies, no jargon
  - **Student**: Academic terminology with definitions, suitable for students
  - **Researcher**: Technical details, implementation insights, for experts
- 🔍 **Context-Aware Responses**: Answers based only on the uploaded paper content
- 💾 **Persistent Storage**: ChromaDB vector store for efficient document retrieval
- 🚀 **Production-Ready**: Clean architecture, error handling, CORS, file validation

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **PyMuPDF**: PDF text extraction
- **ChromaDB**: Vector database for embeddings storage
- **Sentence-Transformers**: Text embeddings (all-MiniLM-L6-v2)
- **Groq SDK**: LLaMA-3 inference (llama3-70b-8192 with 8B fallback)

### Frontend
- **React 18**: UI library
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **Modern CSS**: Responsive, gradient-based design

## Project Structure

```
PaperLens/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints.py      # FastAPI route handlers
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   ├── schemas.py        # Pydantic models
│   │   │   └── __init__.py
│   │   ├── rag/
│   │   │   ├── vector_store.py   # ChromaDB integration
│   │   │   ├── groq_service.py   # Groq LLaMA-3 integration
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── pdf_processor.py  # PDF extraction & chunking
│   │   │   ├── rag_service.py    # RAG orchestration
│   │   │   └── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   └── __init__.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx
│   │   │   ├── PDFUpload.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   └── ExplanationLevelSelector.jsx
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm/yarn
- Groq API key ([Get one here](https://console.groq.com/))

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

5. **Run the backend server:**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   The API will be available at `http://localhost:8000`
   API docs: `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables (optional):**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` if your backend runs on a different URL:
   ```env
   VITE_API_URL=http://localhost:8000/api/v1
   ```

4. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:5173`

## Usage

1. **Upload a PDF**: Drag and drop or click to upload a research paper PDF
2. **Wait for Processing**: The system extracts text and creates embeddings
3. **Select Explanation Level**: Choose Beginner, Student, or Researcher
4. **Ask Questions**: Type questions about the paper
5. **Get Answers**: Receive context-aware explanations based on the paper content

### Example Questions

- "What is the main contribution of this paper?"
- "Explain the methodology in simple terms"
- "What are the key equations and how do they work?"
- "Summarize the results and conclusions"
- "How can I implement the approach described?"

## API Endpoints

### `POST /api/v1/upload`
Upload a PDF file for processing.

**Request:** Multipart form data with `file` field

**Response:**
```json
{
  "document_id": "uuid",
  "filename": "paper.pdf",
  "pages": 10,
  "chunks": 45,
  "message": "Document processed successfully"
}
```

### `POST /api/v1/chat`
Ask a question about an uploaded document.

**Request:**
```json
{
  "document_id": "uuid",
  "question": "What is the main contribution?",
  "explanation_level": "student",
  "chat_history": []
}
```

**Response:**
```json
{
  "answer": "The main contribution is...",
  "sources": ["[Context 1]...", "[Context 2]..."],
  "document_id": "uuid"
}
```

### `DELETE /api/v1/documents/{document_id}`
Delete a document from the system.

### `GET /api/v1/health`
Health check endpoint.

## Environment Variables

### Backend (.env)
- `GROQ_API_KEY` (required): Your Groq API key
- `CHROMA_PERSIST_DIR`: ChromaDB persistence directory (default: `./chroma_db`)
- `RAG_TOP_K`: Number of chunks to retrieve (default: `5`)
- `CORS_ORIGINS`: Comma-separated allowed origins

### Frontend (.env)
- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000/api/v1`)

## Deployment

### Deploy Backend to Render

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your repository**
3. **Configure:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`
   - **Environment Variables**:
     - `GROQ_API_KEY`: Your Groq API key
     - `CHROMA_PERSIST_DIR`: `/opt/render/project/src/chroma_db`
     - `CORS_ORIGINS`: Your frontend URL

4. **Deploy**

### Deploy Frontend to Vercel

1. **Import your repository** to [Vercel](https://vercel.com)
2. **Configure:**
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Environment Variables**:
     - `VITE_API_URL`: Your Render backend URL (e.g., `https://your-app.onrender.com/api/v1`)

3. **Deploy**

### Docker Deployment

#### Backend

```bash
cd backend
docker build -t paperlens-backend .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key paperlens-backend
```

#### Frontend

Build the frontend first, then serve with a static server or use Vercel/Netlify.

## Architecture

### RAG Pipeline

1. **Document Upload**: PDF uploaded and text extracted using PyMuPDF
2. **Text Chunking**: Text split into overlapping chunks (1000 chars, 200 overlap)
3. **Embedding**: Chunks embedded using Sentence-Transformers
4. **Storage**: Embeddings stored in ChromaDB with metadata
5. **Query Processing**:
   - User question embedded
   - Top-K similar chunks retrieved from ChromaDB
   - Context + question sent to Groq LLaMA-3
   - Answer generated with citations

### System Prompts

The system uses level-specific prompts:
- **Beginner**: Simple language, analogies, no jargon
- **Student**: Academic terms with definitions
- **Researcher**: Technical depth, implementation details

All prompts enforce:
- Only use information from provided context
- No hallucinations
- Cite sources when possible
- State uncertainty when information is unavailable

## Development

### Running Tests

```bash
# Backend (when tests are added)
cd backend
pytest

# Frontend (when tests are added)
cd frontend
npm test
```

### Code Style

- Backend: Follow PEP 8, use type hints
- Frontend: ESLint configuration included

## Limitations

- Maximum file size: 50MB
- PDFs must contain extractable text (not scanned images)
- Groq API rate limits apply
- ChromaDB stores data locally (consider cloud storage for production scaling)

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the API docs at `/docs` when running locally

## Acknowledgments

- Groq for fast LLaMA-3 inference
- ChromaDB for vector storage
- FastAPI and React communities

---

Built with ❤️ for researchers and students who want to understand papers better.


