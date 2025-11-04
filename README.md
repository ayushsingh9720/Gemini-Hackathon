**🚀 AI-Powered Resume Parser and Job Matcher**
A robust, scalable, and intelligent system for parsing resumes from various formats and calculating semantic match scores against job descriptions. Leverages modern AI techniques including Large Language Models (LLMs) and NLP (Hugging Face Transformers) built on a high-throughput microservice architecture.

**Video Presentation**: (https://drive.google.com/file/d/1qcZz8jj2GpR4VLJB76wlJ2l84qOD9uCF/view?usp=drive_link)

Project Presentation: (https://drive.google.com/file/d/1qcZz8jj2GpR4VLJB76wlJ2l84qOD9uCF/view?usp=drive_link](https://drive.google.com/file/d/1AASKFCT2fu8jQY_ObgsgvLqRrbiIHVvS/view?usp=drive_link)

**🏗️ Architecture: Decoupled Microservices**
The system is orchestrated by Docker Compose and designed for resilience and scalability by decoupling the fast API layer from the heavy processing layer.

Service	Technology	Role
api	FastAPI (Python)	Handles client requests, file validation, and queues parsing jobs to Celery
worker	Celery / PyTorch	Decoupled processing engine for text extraction, AI parsing, and matching
db	PostgreSQL	Persistent storage for parsed resume data with JSONB for flexible schema
redis	Redis	High-speed message broker for Celery task queuing
⚙️ Setup and Installation
Prerequisites
Ensure you have the following installed:

Docker Desktop (or Docker Engine)

Docker Compose

Quick Start
Navigate to the project root directory and run the setup script:

bash
chmod +x setup.sh
./setup.sh
The script will:

Build Docker images

Install dependencies (including AI libraries)

Start all services

Initialize the database
