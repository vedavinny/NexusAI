# NexusAI

NexusAI is a Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and ask natural language questions grounded in their content.

The system combines semantic retrieval, CrossEncoder reranking, and Llama 3.1 to generate accurate, context-aware responses while reducing hallucinations.

---

## Features

- JWT Authentication
- PDF Upload and Processing
- Semantic Chunking
- Dense Embeddings (BAAI/bge-small-en-v1.5)
- Qdrant Vector Database
- Semantic Retrieval
- CrossEncoder Reranking
- Llama 3.1 Answer Generation (Groq)
- Source Attribution
- Document Deletion
- React Chat Interface

---

## Architecture

```
PDF
 │
 ▼
Text Extraction
 │
 ▼
Semantic Chunking
 │
 ▼
BGE Embeddings
 │
 ▼
Qdrant
 │
 ▼
Semantic Retrieval
 │
 ▼
CrossEncoder Reranker
 │
 ▼
Llama 3.1
 │
 ▼
Grounded Answer
```

---

## Tech Stack

### Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- Qdrant
- LangChain
- Sentence Transformers
- Groq API
- Docker

### Frontend

- React
- Vite
- Tailwind CSS
- Axios

---

## Project Structure

```
backend/
frontend/
docker/
uploads/
README.md
docker-compose.yml
```

---

## Installation

### Clone

```bash
git clone https://github.com/<username>/nexusai.git
cd nexusai
```

### Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt

uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend

npm install

npm run dev
```

### Docker Services

```bash
docker compose up postgres redis qdrant
```

---

## Environment Variables

Create a `.env` file inside the `backend` directory.

```env
DATABASE_URL=
JWT_SECRET_KEY=
GROQ_API_KEY=
QDRANT_HOST=
QDRANT_PORT=
EMBEDDING_MODEL=
GROQ_MODEL_NAME=
```

---

## Future Improvements

- Hybrid Retrieval (BM25 + Dense Search)
- Streaming Responses
- Agentic Retrieval
- Cloud Deployment