# Wings AI Platform

An AI-powered platform built with a lightweight, production-oriented architecture using **FastAPI, LangGraph, Ollama, Qwen3 4B, PostgreSQL + pgvector, and React**.

The platform is designed to run on **OCI Always Free infrastructure** while supporting **RAG, ReAct agents, tool calling, and multi-step AI workflows**.

---

## 1. Architecture

```text
                         WINGS AI PLATFORM
                                │
                                ▼
                         React Frontend
                                │
                                ▼
                         FastAPI Backend
                                │
                                ▼
                           LangGraph
                                │
                 ┌──────────────┼──────────────┐
                 │              │              │
                 ▼              ▼              ▼
              Qwen3 4B        RAG          Tools / APIs
              Ollama       Pipeline
                 │              │
                 │              ▼
                 │       nomic-embed-text
                 │              │
                 │              ▼
                 │       PostgreSQL
                 │        + pgvector
                 │
                 └──────────────┬──────────────┘
                                ▼
                         Final Response
```

---

## 2. Technology Stack

| Layer                 | Technology                  |
| --------------------- | --------------------------- |
| Frontend              | React                       |
| Backend               | Python FastAPI              |
| Agent Orchestration   | LangGraph                   |
| LLM Runtime           | Ollama                      |
| LLM                   | Qwen3 4B                    |
| Embeddings            | nomic-embed-text            |
| Database              | PostgreSQL 16               |
| Vector Search         | pgvector                    |
| Containerization      | Docker / Docker Compose     |
| Infrastructure        | Oracle Cloud Infrastructure |
| Target Infrastructure | OCI Always Free             |
| API Style             | REST                        |
| Python Environment    | Python 3.x                  |

---

## 3. AI Models

### Chat / Reasoning Model

```env
OLLAMA_MODEL=qwen3:4b
```

Qwen3 4B is used for:

* General AI responses
* Reasoning
* RAG answer generation
* Agent planning
* ReAct workflows
* Tool selection
* Multi-step tasks

### Embedding Model

```env
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

The embedding model is used for:

* Document embeddings
* Semantic search
* RAG retrieval
* Similarity matching

The chat model and embedding model have separate responsibilities.

---

## 4. Core Capabilities

### RAG

The platform supports Retrieval-Augmented Generation:

```text
Document
   │
   ▼
Document Parser
   │
   ▼
Chunking
   │
   ▼
Embedding
   │
   ▼
nomic-embed-text
   │
   ▼
PostgreSQL + pgvector
   │
   ▼
Similarity Search
   │
   ▼
Relevant Context
   │
   ▼
Qwen3 4B
   │
   ▼
Grounded Answer
```

### ReAct Agent

The agent follows a controlled reasoning/tool loop:

```text
START
  │
  ▼
Agent
  │
  ├── No tool required ──► END
  │
  └── Tool required
          │
          ▼
      Execute Tool
          │
          ▼
      Observation
          │
          ▼
        Agent
          │
          ▼
         END
```

LangGraph controls the workflow rather than allowing an uncontrolled agent loop.

---

## 5. Project Structure

```text
wings-ai-platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── agents/
│   │   ├── rag/
│   │   ├── tools/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── Dockerfile
│
├── docker/
│
├── .env
├── .env.example
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 6. Environment Configuration

Create `.env`:

```env
# Application
APP_NAME=Wings AI Platform
APP_ENV=development
DEBUG=true

# PostgreSQL
POSTGRES_DB=wings_ai
POSTGRES_USER=wings_admin
POSTGRES_PASSWORD=wings_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text

# API
BACKEND_PORT=8000

# Frontend
FRONTEND_PORT=3000
```

Never commit the real `.env` file.

Use:

```text
.env.example
```

for source control.

---

## 7. Docker Services

The initial stack intentionally keeps the infrastructure minimal.

```text
docker-compose.yml
│
├── postgres
├── ollama
├── backend
└── frontend
```

pgAdmin can be included for development/database administration but is not required by the application runtime.

Redis is intentionally excluded unless a concrete requirement is introduced.

---

## 8. Start the Entire Platform

From the project root:

```bash
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

View backend logs:

```bash
docker compose logs -f backend
```

View Ollama logs:

```bash
docker compose logs -f ollama
```

---

## 9. Download AI Models

After Ollama starts:

```bash
docker compose exec ollama ollama pull qwen3:4b
```

Pull the embedding model:

```bash
docker compose exec ollama ollama pull nomic-embed-text
```

Verify:

```bash
docker compose exec ollama ollama list
```

Expected models:

```text
qwen3:4b
nomic-embed-text
```

---

## 10. PostgreSQL

PostgreSQL is the primary application database.

It stores:

* Users
* Conversations
* Messages
* Documents
* Document chunks
* Metadata
* Agent state where required
* Vector embeddings

The database uses PostgreSQL with pgvector for semantic retrieval.

Example connection:

```text
Host: postgres
Port: 5432
Database: wings_ai
User: wings_admin
```

Inside Docker, the PostgreSQL hostname is:

```text
postgres
```

Do not use:

```text
localhost
```

from the backend container.

---

## 11. Backend

The backend is implemented using FastAPI.

Primary responsibilities:

* Authentication
* REST APIs
* Request validation
* AI orchestration
* LangGraph execution
* RAG
* Tool execution
* Database access
* Conversation management

Run locally without Docker:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

API documentation:

```text
http://localhost:8000/docs
```

---

## 12. LangGraph

LangGraph manages the AI workflow.

A typical workflow:

```text
User Request
     │
     ▼
Intent / Agent
     │
     ├───────────────┐
     │               │
     ▼               ▼
   RAG            Tool Call
     │               │
     ▼               ▼
Retrieve          Execute
Context             Tool
     │               │
     └───────┬───────┘
             ▼
          Agent
             │
             ▼
      Final Response
```

LangGraph is responsible for workflow state and transitions.

The LLM should not directly control infrastructure or database operations.

---

## 13. RAG Pipeline

### Ingestion

```text
Upload Document
      │
      ▼
Parse Document
      │
      ▼
Clean Text
      │
      ▼
Chunk Document
      │
      ▼
Generate Embeddings
      │
      ▼
Store in PostgreSQL
```

### Retrieval

```text
User Question
      │
      ▼
Generate Query Embedding
      │
      ▼
pgvector Similarity Search
      │
      ▼
Top Relevant Chunks
      │
      ▼
Context Construction
      │
      ▼
Qwen3 4B
      │
      ▼
Answer
```

---

## 14. Security Principles

The platform follows these principles:

* Secrets are stored in environment variables.
* Database credentials are never hardcoded.
* AI tools are explicitly registered.
* Tool permissions are controlled by the backend.
* User input is validated before processing.
* Database access is performed through the backend.
* The LLM never receives unrestricted infrastructure access.
* RAG responses should be grounded in retrieved context.
* Production debugging should not expose sensitive data.

---

## 15. OCI Always Free Target

The architecture is designed to minimize resource consumption.

Target deployment:

```text
OCI Compute
│
├── FastAPI
├── LangGraph
├── Ollama
│    └── Qwen3 4B
│
├── PostgreSQL
│    └── pgvector
│
└── React
```

The design avoids unnecessary infrastructure such as:

```text
Redis
Kafka
RabbitMQ
Elasticsearch
Separate Vector DB
Separate LLM Server
```

unless future requirements justify them.

---

## 16. Development Workflow

Start everything:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Follow logs:

```bash
docker compose logs -f
```

Restart backend:

```bash
docker compose restart backend
```

Restart Ollama:

```bash
docker compose restart ollama
```

Stop the stack:

```bash
docker compose down
```

Stop and remove database volumes:

```bash
docker compose down --volumes
```

> `--volumes` permanently removes PostgreSQL data stored in Docker volumes.

---

## 17. Fresh Rebuild

For a complete application rebuild:

```bash
docker compose down --volumes --remove-orphans
docker compose build --no-cache
docker compose up -d
```

Check:

```bash
docker compose ps
```

Then download models if necessary:

```bash
docker compose exec ollama ollama pull qwen3:4b
docker compose exec ollama ollama pull nomic-embed-text
```

---

## 18. Health Checks

The platform should expose health endpoints.

Example:

```text
GET /health
```

Expected:

```json
{
  "status": "ok"
}
```

AI health should verify:

```text
FastAPI
   │
   ├── PostgreSQL ✓
   │
   └── Ollama ✓
```

---

## 19. Production Principles

The initial goal is a small but production-oriented architecture.

### Keep

* FastAPI
* PostgreSQL
* pgvector
* Ollama
* Qwen3 4B
* LangGraph
* React
* Docker

### Add only when required

* Redis
* Message queues
* Separate vector database
* Kubernetes
* Additional model servers
* Distributed workers

The architecture should evolve based on actual load rather than adding infrastructure prematurely.

---

## 20. Roadmap

### Phase 1 — Foundation

* [ ] Docker infrastructure
* [ ] PostgreSQL
* [ ] FastAPI
* [ ] React
* [ ] Ollama
* [ ] Qwen3 4B
* [ ] Basic authentication

### Phase 2 — AI

* [ ] LangGraph
* [ ] Agent workflow
* [ ] Tool calling
* [ ] ReAct workflow
* [ ] Conversation memory

### Phase 3 — RAG

* [ ] Document upload
* [ ] Document parsing
* [ ] Chunking
* [ ] Embeddings
* [ ] pgvector
* [ ] Semantic retrieval
* [ ] Source-aware responses

### Phase 4 — Production

* [ ] Authentication hardening
* [ ] Authorization
* [ ] Rate limiting
* [ ] Structured logging
* [ ] Monitoring
* [ ] Error handling
* [ ] Automated tests
* [ ] CI/CD
* [ ] OCI deployment

---

## 21. Design Goal

Wings AI is designed around a simple principle:

> **Build the smallest infrastructure that can reliably deliver production-grade AI capabilities.**

The initial platform therefore uses:

```text
FastAPI
+
LangGraph
+
Qwen3 4B
+
Ollama
+
PostgreSQL
+
pgvector
+
React
+
Docker
```

This provides a foundation for **RAG + ReAct + tool-based AI workflows** while remaining practical for a low-cost OCI deployment.
