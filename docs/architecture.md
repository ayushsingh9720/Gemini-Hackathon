Architecture Overview: AI Resume Parser

Our solution utilizes a microservice architecture orchestrated by Docker Compose to ensure scalability, resilience, and performance. This design strictly separates the responsive API gateway from the heavy-lifting AI processing engine.

Key Components (4 Services)

Service

Technology

Role

Scalability Benefit

API (api-1)

FastAPI (Python)

Gateway: Handles all incoming HTTP requests (/upload, /match, /get). It validates inputs and queues asynchronous tasks.

High throughput, low latency.

Worker (worker-1)

Celery / PyTorch / Transformers

Processing Engine: Handles the heavy, long-running tasks (document parsing, OCR, and AI/ML model inference). This prevents API timeouts.

Easily scaled by adding more worker replicas.

Broker (redis-1)

Redis

Message Queue/Cache: Acts as the communication bridge (broker) between the API and the Worker, and stores task results.

Decouples the producer (API) from the consumer (Worker).

Database (db-1)

PostgreSQL

Persistent Storage: Stores resume metadata and the final structured JSON data using the JSONB data type for flexible schema.

Reliable, ACID-compliant data persistence.

AI Strategy

Core Extraction (NER): Uses a pre-trained Hugging Face model (dslim/bert-base-NER) to identify key entities (Name, Title, Company, Date) from the unstructured resume text.

Semantic Matching (Advanced Feature): Uses the Sentence Transformer model (all-MiniLM-L6-v2) to generate vector embeddings for the Job Description and the Parsed Resume. Cosine similarity calculates the relevancy score, which drives the final overallScore.
