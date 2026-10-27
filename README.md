# Secure Enterprise RAG System

A production-grade, secure Retrieval-Augmented Generation (RAG) platform built with a unified PostgreSQL architecture. This system consolidates relational user permissions, document metadata, vector embeddings, full-text keyword indices, and compliance audit trails into a single PostgreSQL instance.

## Architecture & Tech Stack

* **Database & Vector Store:** PostgreSQL 17 with the `pgvector` extension, hosted via Docker.
* **Backend & API:** FastAPI with asynchronous request handling.
* **Package Management:** `uv` for high-performance Python dependency resolution.
* **Framework & Orchestration:** LangChain and custom modular pipelines.
* **AI & Local Execution:** Ollama (`nomic-embed-text` for vector embeddings and local LLMs for generation and evaluation).
* **Advanced Patterns:** Hybrid Search (Vector Cosine Similarity + PostgreSQL Full-Text Search), Corrective RAG (CRAG) with Attempt 2 validation loops, and LLM-as-Judge evaluation.

## Key Features

1. **Unified Single-Database Architecture**
   Eliminates data drift across distributed stores by keeping relational metadata, security rules, and vector data in one Postgres database linked via foreign keys (`ON DELETE CASCADE`).
2. **Hybrid Search Implementation**
   * **Semantic Search:** Employs HNSW indexing and cosine similarity (`<=>`) through `pgvector`.
   * **Keyword Search:** Utilizes native PostgreSQL `TSVECTOR` and GIN indices for exact term and phrase matching.
3. **Corrective RAG & Attempt 2 Logic**
   Includes automated validation steps where retrieved context is evaluated for relevance and accuracy, triggering corrective refinement loops if initial grounding fails.
4. **Auditability & Compliance**
   Maintains an immutable audit log (`audit_events`) capturing user context, queries, source citations, and generation success metrics.

## Docker Setup

The database runs within a containerized environment using `pgvector/pgvector:pg17`.

```yaml
services:
  db:
    image: pgvector/pgvector:pg17
    container_name: rag-postgres
    environment:
      POSTGRES_USER: rag
      POSTGRES_PASSWORD: vyomsoni
      POSTGRES_DB: vector_db
    ports:
      - "5433:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U rag -d vector_db"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  pgdata:
```

## Configuration

Create a `.env` file in the project root containing:

```env
DATABASE_URL=postgresql://rag:vyomsoni@localhost:5433/vector_db
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=nomic-embed-text
```

## Installation & Execution

1. Start the Docker database container:
   ```powershell
   docker compose up -d
   ```

2. Synchronize project dependencies using `uv`:
   ```powershell
   uv sync
   ```

3. Launch the FastAPI application server:
   ```powershell
   uv run uvicorn API.app:app --reload
   ```

The application runs locally at `http://127.0.0.1:8000`, with interactive documentation available at `http://127.0.0.1:8000/docs`.
