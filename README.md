# 🚀 DocIntel AI — Enterprise Conversational RAG Platform

An industry-grade **Conversational Retrieval-Augmented Generation (RAG)** platform built using **FastAPI**, **PostgreSQL + pgvector**, **Celery**, **Redis**, **AWS S3**, **Jina AI Embeddings**, **Cross-Encoder Reranking**, and **DeepSeek LLM**.

The platform enables users to upload documents, build a semantic knowledge base, and interact with an AI assistant capable of retrieving contextually relevant information while maintaining persistent multi-turn conversations.

Designed with production-oriented backend engineering principles, asynchronous document processing, scalable storage, and modular AI services.

---

# ⭐ Highlights

- 🔐 JWT Authentication & Authorization
- 📄 Intelligent Document Processing Pipeline
- ☁️ AWS S3 Cloud Storage
- ⚡ Celery Background Task Processing
- 🚀 Redis Message Queue
- 🧠 Jina AI Embedding API
- 🔍 Semantic Vector Search using pgvector
- 🎯 Cross-Encoder Neural Reranking
- 💬 Persistent Conversational Memory
- 🤖 DeepSeek LLM Integration
- 📚 Multi-Document Knowledge Base
- 🏗 Modular Service-Oriented Architecture
- 📈 Production-Ready Backend Design
- 🐳 Docker Ready (Upcoming)
- ☁️ Cloud Deployment Ready

---

# 📖 Table of Contents

- Overview
- Features
- System Architecture
- Document Processing Pipeline
- Conversational RAG Pipeline
- Tech Stack
- Project Structure
- Database Design
- Installation
- Configuration
- Running the Project
- API Endpoints
- Future Enhancements
- Learning Outcomes

---

# 🌟 Overview

Traditional LLMs suffer from two major limitations:

- Limited knowledge beyond their training data
- Hallucinated responses when information is unavailable

This project solves these problems using a **Retrieval-Augmented Generation (RAG)** architecture.

Instead of relying solely on an LLM's internal knowledge, the system:

- Stores uploaded documents as vector embeddings
- Retrieves semantically relevant document chunks
- Reranks retrieved context using a Cross Encoder
- Generates accurate responses grounded in retrieved information
- Maintains conversation history for contextual multi-turn dialogue

The result is a scalable conversational AI system capable of answering questions from user-provided documents with significantly improved factual accuracy.

---

# ✨ Features

## 🔐 Authentication & Authorization

- User Registration
- Secure Login
- JWT Authentication
- Password Hashing (bcrypt)
- Protected API Endpoints
- User-specific Document Isolation
- Session-based Chat Ownership

---

## 📄 Intelligent Document Processing

Supports uploading multiple document formats.

Current supported formats:

- PDF
- DOCX

Processing pipeline:

- Upload document
- Store original file in AWS S3
- Extract document text
- Intelligent chunk generation
- Background embedding generation
- Store embeddings inside PostgreSQL + pgvector

---

## ☁️ AWS S3 Cloud Storage

Instead of storing uploaded files on the application server, documents are securely stored in **Amazon S3**.

Benefits:

- Highly scalable object storage
- Improved reliability
- Reduced application server storage
- Cloud-native architecture
- Secure document management

Only document metadata is stored inside PostgreSQL.

---

## ⚡ Asynchronous Background Processing

Document processing is executed asynchronously using **Celery**.

Tasks processed in the background include:

- Document extraction
- Text chunking
- Embedding generation
- Vector storage

Benefits:

- Non-blocking uploads
- Faster API response times
- Better scalability
- Improved user experience

---

## 🚀 Redis Message Broker

Redis serves as the communication layer between FastAPI and Celery.

Responsibilities include:

- Task queue management
- Message brokering
- Worker communication
- Background job scheduling

This architecture decouples heavy AI processing from API requests.

---

## 🧠 Jina AI Embeddings

Semantic search is powered using the **Jina AI Embedding API**.

Each document chunk and user query is converted into dense vector embeddings.

Advantages:

- High-quality semantic representations
- Fast batch embedding generation
- Production-grade embedding models
- Excellent retrieval quality
- Optimized for Retrieval-Augmented Generation

---

## 🔍 Semantic Vector Search

Embeddings are stored inside PostgreSQL using the **pgvector** extension.

During querying:

- Query embeddings are generated
- Similar vectors are retrieved
- Top candidate chunks are selected

Semantic search enables retrieval based on meaning rather than exact keyword matching.

---

## 🎯 Cross-Encoder Reranking

Initial semantic retrieval is further refined using a neural Cross Encoder.

Model:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

Responsibilities:

- Evaluate query-document relevance
- Rerank retrieved chunks
- Improve retrieval precision
- Reduce irrelevant context

This two-stage retrieval architecture closely resembles production RAG systems.

---

## 💬 Persistent Conversational Memory

Unlike traditional question-answer systems, this platform supports persistent conversations.

Features include:

- Multiple chat sessions
- Conversation history
- Custom chat titles
- Multi-turn interactions
- Context-aware responses

Every user message and assistant response is stored inside PostgreSQL, allowing conversations to be resumed at any time.

---

## 🤖 LLM Integration

The retrieved and reranked context is sent to a Large Language Model through the HuggingFace Inference API.

Current model:

```text
deepseek-ai/DeepSeek-V4-Flash
```

The model generates grounded, context-aware responses using:

- Retrieved document chunks
- Conversation history
- Current user query

---

# 🏗️ High-Level System Architecture

                           User
                             │
                             ▼
                     FastAPI Backend
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
 PostgreSQL + pgvector     AWS S3            Redis Queue
        │                    │                    │
        │                    │                    ▼
        │                    │              Celery Worker
        │                    │                    │
        │                    │                    ▼
        │                    └────────► Document Processing
        │
        ▼
Semantic Retrieval
        │
        ▼
Cross Encoder Reranking
        │
        ▼
DeepSeek LLM
        │
        ▼
AI Response
```

---

# 📄 Document Processing Pipeline

```text
User Uploads Document
           │
           ▼
      FastAPI API
           │
           ▼
 Store Original File in AWS S3
           │
           ▼
 Create Celery Background Task
           │
           ▼
 Extract Text
           │
           ▼
 Intelligent Chunking
           │
           ▼
 Batch Embedding Generation (Jina AI)
           │
           ▼
 Store Embeddings in PostgreSQL + pgvector
```

---

# 🧠 Conversational RAG Pipeline

```text
User Query
      │
      ▼
Generate Query Embedding (Jina AI)
      │
      ▼
Vector Similarity Search (pgvector)
      │
      ▼
Retrieve Top-K Chunks
      │
      ▼
Cross Encoder Reranking
      │
      ▼
Load Conversation History
      │
      ▼
Prompt Construction
      │
      ▼
DeepSeek LLM
      │
      ▼
Context-Aware AI Response


---

# 🛠️ Tech Stack

| Category | Technology |
|-----------|------------|
| Backend Framework | FastAPI |
| Programming Language | Python 3.12+ |
| Database | PostgreSQL |
| Vector Database | pgvector |
| ORM | SQLAlchemy |
| Database Migration | Alembic |
| Authentication | JWT |
| Password Hashing | bcrypt + Passlib |
| Background Tasks | Celery |
| Message Broker | Redis |
| Cloud Storage | AWS S3 |
| Embedding Model | Jina AI Embedding API |
| Reranker | Cross Encoder (MS MARCO MiniLM) |
| Large Language Model | DeepSeek-V4-Flash (HuggingFace Inference API) |
| Document Parsing | PyMuPDF, python-docx |
| HTTP Client | Requests / HTTPX |
| API Documentation | Swagger UI |
| Environment Management | python-dotenv |
| Deployment (Planned) | Docker, Docker Compose |
| Cloud Deployment (Planned) | AWS EC2 |

---

# 📂 Project Structure

```text
AI-Document-Analyzer/
│
├── alembic/
│
├── app/
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── chats.py
│   │   ├── messages.py
│   │   └── query.py
│   │
│   ├── services/
│   │   ├── embedding.py
│   │   ├── reranker.py
│   │   ├── llm.py
│   │   ├── extraction.py
│   │   ├── chunking.py
│   │   ├── s3.py
│   │   └── celery_tasks.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── oauth2.py
│   │
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   └── main.py
│
├── requirements.txt
├── .env
├── Dockerfile              (Upcoming)
├── docker-compose.yml      (Upcoming)
└── README.md
```

---

# 🗄️ Database Design

The platform uses PostgreSQL as its primary database.

## Users

Stores:

- User account information
- Login credentials
- Authentication details

---

## Documents

Stores:

- Uploaded document metadata
- S3 object key
- Upload timestamp
- Owner information

---

## Document Chunks

Stores:

- Chunk text
- Chunk index
- Dense vector embeddings
- Document relationship

Each chunk represents a semantically searchable section of the original document.

---

## Chats

Stores:

- Chat sessions
- Chat titles
- User ownership

Allows multiple conversations per user.

---

## Messages

Stores:

- User prompts
- AI responses
- Message timestamps
- Chat relationships

Provides persistent conversation memory.

---

# 🧩 Entity Relationship Overview

```text
Users
   │
   ├──────────────┐
   ▼              ▼
Documents       Chats
   │              │
   ▼              ▼
DocumentChunks  Messages
```

---

# 🔐 Authentication Flow

Authentication is implemented using JWT tokens.

Workflow:

```text
User Login
      │
      ▼
Validate Credentials
      │
      ▼
Generate JWT Token
      │
      ▼
Client Stores Token
      │
      ▼
Protected API Requests
      │
      ▼
JWT Verification
      │
      ▼
Authorized Access
```

Features:

- Stateless authentication
- Secure password hashing
- Token expiration
- Protected routes
- User-specific resource access

---

# ⚙️ Environment Variables

Create a `.env` file in the project root.

```env
# PostgreSQL
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=your_password

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# HuggingFace
HF_TOKEN=your_huggingface_token

# Jina AI
JINA_API_KEY=your_jina_api_key

# AWS
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region
AWS_BUCKET_NAME=your_bucket_name

# Redis
REDIS_URL=redis://localhost:6379/0
```

---

# 🚀 Installation

Clone the repository.

```bash
git clone https://github.com/yourusername/AI-Document-Analyzer.git

cd AI-Document-Analyzer
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Database Migrations

```bash
alembic upgrade head
```

---

## Start Redis

```bash
redis-server
```

---

## Start Celery Worker

```bash
celery -A app.services.celery_tasks worker --loglevel=info
```

---

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

---

# 🌐 API Documentation

Once the server is running:

Swagger UI

```text
http://localhost:8000/docs
```

ReDoc

```text
http://localhost:8000/redoc
```

FastAPI automatically generates interactive API documentation.

---

# 📡 API Endpoints

## Authentication

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/users` | Register new user |
| POST | `/login` | Login user |

---

## Document APIs

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/upload` | Upload document |
| GET | `/documents` | List uploaded documents |
| DELETE | `/documents/{id}` | Delete document |

---

## Chat APIs

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/chat` | Create new chat |
| GET | `/chat` | List user chats |
| DELETE | `/chat/{id}` | Delete chat |

---

## Message APIs

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/chat/{chat_id}/message` | Send message |
| GET | `/chat/{chat_id}/messages` | Conversation history |

---

## Query API

| Method | Endpoint | Description |
|----------|----------|-------------|
| POST | `/query` | Query uploaded knowledge base |

---

# 🔄 Request Lifecycle

```text
Client Request
      │
      ▼
FastAPI Router
      │
      ▼
Authentication
      │
      ▼
Business Logic
      │
      ▼
Database / S3 / Redis
      │
      ▼
AI Services
      │
      ▼
JSON Response
```

---

# 🧪 API Testing

The project has been tested using:

- Swagger UI
- Postman

Testing includes:

- Authentication
- File Uploads
- Chat Sessions
- Conversation Memory
- Document Retrieval
- Semantic Search
- AI Response Generation

---

# 📊 Retrieval Evaluation

Retrieval quality is one of the most critical aspects of any Retrieval-Augmented Generation (RAG) system.

This project includes an evaluation pipeline to measure the effectiveness of semantic retrieval before passing context to the LLM.

Current evaluation metrics include:

- Hit Rate
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)

Evaluation helps determine:

- Whether relevant chunks are retrieved
- The effectiveness of embedding models
- Reranking performance
- Overall retrieval quality

Future improvements include:

- nDCG
- MAP (Mean Average Precision)
- Answer Faithfulness
- Context Precision
- Context Recall
- Hallucination Detection

---

# 🧠 AI Components

## Embedding Model

The project uses the **Jina AI Embedding API** to generate dense vector representations for both document chunks and user queries.

Responsibilities:

- Semantic document indexing
- Semantic query representation
- High-quality vector generation
- Batch embedding support

---

## Vector Database

Embeddings are stored inside PostgreSQL using the **pgvector** extension.

Advantages:

- Native PostgreSQL integration
- Efficient vector similarity search
- Metadata filtering support
- Scalable semantic retrieval

---

## Cross Encoder

The retrieved chunks are reranked using:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The reranker scores every candidate chunk against the user query.

Benefits:

- Higher retrieval precision
- Better contextual relevance
- Reduced irrelevant information
- Improved LLM response quality

---

## Large Language Model

Current LLM:

```text
deepseek-ai/DeepSeek-V4-Flash
```

The model receives:

- Conversation history
- Retrieved document chunks
- Current user query

and generates grounded, context-aware responses.

---

# ⚡ Background Task Architecture

Heavy AI workloads are executed asynchronously using Celery.

```text
               Upload Request
                      │
                      ▼
                FastAPI Backend
                      │
                      ▼
          Push Task to Redis Queue
                      │
                      ▼
               Celery Worker
                      │
      ┌───────────────┼───────────────┐
      │               │               │
      ▼               ▼               ▼
Extract Text     Chunk Document   Generate Embeddings
      │               │               │
      └───────────────┼───────────────┘
                      ▼
          Store Vectors in PostgreSQL
```

This architecture keeps API responses fast while processing computationally expensive tasks in the background.

---

# ☁️ AWS Cloud Architecture

Uploaded documents are stored in Amazon S3.

```text
User
 │
 ▼
FastAPI
 │
 ▼
AWS S3
 │
 ▼
Celery Worker
 │
 ▼
Text Extraction
 │
 ▼
Embedding Generation
 │
 ▼
PostgreSQL + pgvector
```

Benefits:

- Durable object storage
- Better scalability
- Reduced server storage requirements
- Cloud-native design

---

# 🐳 Docker Support (Upcoming)

The project is designed to be containerized using Docker.

Planned containers:

- FastAPI Application
- Celery Worker
- PostgreSQL + pgvector
- Redis

Docker Compose will orchestrate all services for local development and production deployment.

Planned deployment stack:

```text
Docker Compose
      │
      ├── FastAPI
      ├── Celery
      ├── PostgreSQL
      └── Redis
```

---

# ☁️ Cloud Deployment (Upcoming)

The application is designed for deployment on AWS.

Target deployment architecture:

```text
Internet
     │
     ▼
AWS EC2
     │
     ├── FastAPI
     ├── Celery
     ├── Redis
     └── PostgreSQL

          │
          ▼
      AWS S3
```

Future deployment improvements include:

- Docker
- Nginx
- HTTPS
- CI/CD
- Automated backups
- Monitoring

---

# 📈 Future Roadmap

## Retrieval Improvements

- Hybrid Search (BM25 + Dense Retrieval)
- Query Expansion
- Metadata Filtering
- Parent-Child Retrieval
- Multi-Query Retrieval
- Context Compression
- Adaptive Chunking

---

## AI Enhancements

- OCR Support
- Citation-Aware Responses
- Streaming Responses
- Conversation Summarization
- Multi-Document Reasoning
- Agentic RAG
- Function Calling

---

## Infrastructure

- Docker
- Docker Compose
- Kubernetes
- GitHub Actions
- CI/CD Pipeline
- Prometheus
- Grafana
- MLflow
- Redis Caching

---

## Security

- Role-Based Access Control (RBAC)
- Refresh Tokens
- Rate Limiting
- Audit Logs
- API Key Management

---

# 🎯 Learning Outcomes

This project demonstrates practical understanding of:

## AI Engineering

- Retrieval-Augmented Generation (RAG)
- Conversational AI
- Semantic Search
- Dense Embeddings
- Neural Reranking
- Prompt Engineering
- Context Retrieval

---

## Backend Engineering

- FastAPI
- REST APIs
- SQLAlchemy ORM
- PostgreSQL
- pgvector
- JWT Authentication
- Background Processing
- Cloud Storage Integration

---

## Software Engineering

- Modular Architecture
- Clean Code Practices
- Service-Oriented Design
- Dependency Injection
- Environment-Based Configuration
- Production API Design

---

## Cloud & DevOps

- AWS S3
- Redis
- Celery
- Docker (Planned)
- AWS Deployment (Planned)

---

# 🤝 Contributing

Contributions are welcome!

If you have suggestions for improvements, feel free to:

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Rishav Poddar**

AI & Backend Engineering Enthusiast

Interested in:

- Artificial Intelligence
- Retrieval-Augmented Generation
- Backend Development
- Machine Learning
- Cloud Computing
- MLOps
- Production AI Systems

---

# ⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub.

It helps others discover the project and motivates further development.

---

## 🚀 Final Note

This project is not intended to be just another chatbot.

It is designed as a production-oriented **Conversational Retrieval-Augmented Generation (RAG) platform** that combines modern AI techniques with scalable backend engineering practices.

The architecture reflects many of the core concepts used in enterprise AI systems, including semantic retrieval, neural reranking, asynchronous processing, cloud object storage, persistent conversational memory, and modular service design.

As the project evolves, planned enhancements such as hybrid retrieval, Docker-based deployment, Kubernetes orchestration, monitoring, CI/CD, and advanced evaluation pipelines will further strengthen its capabilities and bring it closer to production-grade AI infrastructure.

---

```
