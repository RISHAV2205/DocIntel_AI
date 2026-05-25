# 🚀 AI-Powered Conversational RAG System
An industry-style Conversational Retrieval-Augmented Generation (RAG) system built using FastAPI, PostgreSQL, JWT Authentication, Vector Embeddings, Cross-Encoder Reranking, and HuggingFace LLMs.

This project allows users to upload documents, retrieve semantically relevant information, and chat continuously with an AI assistant that remembers conversation history.

---

# 🌟 Features

## 🔐 JWT Authentication System
- Secure user registration and login
- Password hashing using bcrypt
- JWT token-based authentication
- Protected API routes
- User-specific document isolation

---

## 📄 Document Processing Pipeline
- Upload documents
- Extract text
- Chunk large documents
- Store chunks in PostgreSQL
- Generate embeddings for semantic search

---

## 🧠 Embedding-Based Semantic Retrieval
- Uses Sentence Transformers (`all-MiniLM-L6-v2`)
- Converts:
  - user queries
  - document chunks
into dense vector embeddings

- Performs cosine similarity search to retrieve relevant chunks

---

## ⚡ Cross-Encoder Reranking
After vector retrieval:
- top candidate chunks are passed through a Cross Encoder
- improves retrieval accuracy significantly
- reranks chunks based on query-context relevance

Model Used:
```python
cross-encoder/ms-marco-MiniLM-L-6-v2
````

This architecture is widely used in production-grade RAG systems.

---

# 💬 Conversational AI Memory System

## ✅ Chat Sessions

* Multiple chat sessions per user
* Custom chat titles
* Persistent chat architecture

## ✅ Conversation Memory

* Stores:

  * user messages
  * assistant responses
* Enables continuous multi-turn conversation
* Maintains conversational context

## ✅ Persistent Conversation History

* Messages stored in PostgreSQL
* Previous conversations can be resumed

This transforms the system from:

```text
single prompt-response AI
```

into:

```text
stateful conversational AI system
```

---

# 🧠 Retrieval-Augmented Generation (RAG) Pipeline

## Current RAG Flow

```text
User Query
    ↓
Generate Query Embedding
    ↓
Semantic Vector Search
    ↓
Retrieve Top-K Chunks
    ↓
Cross Encoder Reranking
    ↓
Load Conversation History
    ↓
Build Final Prompt
    ↓
Send to LLM
    ↓
Generate Context-Aware Response
```

---

# 🤖 LLM Integration

Integrated with HuggingFace Inference API.

Current Model:

```python
deepseek-ai/DeepSeek-V4-Flash
```

Benefits:

* Free-tier friendly
* Fast inference
* Strong instruction following
* Excellent for RAG applications

---

# 🏗️ Tech Stack

| Component      | Technology                |
| -------------- | ------------------------- |
| Backend        | FastAPI                   |
| Database       | PostgreSQL                |
| ORM            | SQLAlchemy                |
| Migrations     | Alembic                   |
| Authentication | JWT                       |
| Embeddings     | Sentence Transformers     |
| Reranking      | Cross Encoder             |
| LLM            | HuggingFace Inference API |
| AI Models      | MiniLM + DeepSeek         |
| API Testing    | Swagger UI / Postman      |

---

# 📂 Project Architecture

```bash
app/
│
├── router/
│   ├── auth.py
│   ├── documents.py
│   ├── query.py
│   ├── chats.py
│   └── chat_message.py
│
├── services/
│   ├── embedding.py
│   ├── cross_encoder.py
│   ├── llm.py
│   ├── chunking.py
│   └── extraction.py
│
├── models.py
├── schemas.py
├── oauth2.py
├── database.py
└── main.py
```

---

# 🗄️ Database Design

## Users

Stores:

* authentication details
* account information

## Documents

Stores:

* uploaded file metadata
* ownership information

## Document Chunks

Stores:

* chunked text
* vector embeddings

## Chats

Stores:

* chat sessions
* chat titles

## Messages

Stores:

* complete conversation history

---

# 🔥 Industry-Level Concepts Implemented

## ✅ Semantic Search

Searches by meaning instead of keywords.

## ✅ Vector Embeddings

Transforms text into high-dimensional numerical representations.

## ✅ Reranking Architecture

Improves retrieval precision using neural reranking.

## ✅ Conversational Memory

Maintains chat continuity.

## ✅ Secure Authentication

JWT-protected APIs.

## ✅ Modular Service Architecture

Clean separation of:

* routing
* services
* models
* schemas

## ✅ Production-Oriented Design

Built with scalable backend architecture principles.

---

# 🚀 API Endpoints

## Authentication

```http
POST /login
POST /users
```

## Document APIs

```http
POST /upload
```

## Chat APIs

```http
POST /chat
POST /{chat_id}/message
```

## Query APIs

```http
POST /query
```

---

# ⚙️ Environment Variables

Create a `.env` file:

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=yourpassword
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres

SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

HF_TOKEN=your_huggingface_token
```

---

# ▶️ Running the Project

## Install dependencies

```bash
pip install -r requirements.txt
```

## Run migrations

```bash
alembic upgrade head
```

## Start server

```bash
uvicorn app.main:app --reload
```

---

# 📌 Future Enhancements

## Planned Features

* Streaming responses
* Hybrid search (BM25 + Vector)
* Redis caching
* Async task queues
* Vector databases (Qdrant/Pinecone)
* WebSocket real-time chat
* Citation-aware responses
* Conversation summarization
* Multi-document reasoning
* Docker deployment
* Kubernetes deployment
* CI/CD pipelines

---

# 🧠 Learning Outcomes

This project demonstrates practical understanding of:

* RAG Architecture
* Semantic Search
* Vector Databases
* LLM Integration
* Authentication Systems
* Backend Engineering
* AI System Design
* Conversational AI
* Retrieval Pipelines
* Production API Design

---


# 👨‍💻 Rishav Poddar

Built with FastAPI + AI Engineering principles to explore industry-grade Conversational RAG systems.


