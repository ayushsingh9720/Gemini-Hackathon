🚀 **AI-Powered Resume Parser and Job Matcher**

Project Overview

This project implements a robust, scalable, and intelligent system for parsing resumes from various formats and calculating a semantic match score against job descriptions. The solution leverages modern techniques, including Large Language Models (LLM) and NLP (Hugging Face Transformers), and is built on a high-throughput microservice architecture.

video presentation - https://drive.google.com/file/d/1qcZz8jj2GpR4VLJB76wlJ2l84qOD9uCF/view?usp=drive_link
presentation - https://drive.google.com/file/d/1AASKFCT2fu8jQY_ObgsgvLqRrbiIHVvS/view?usp=sharing

🏗️ Architecture: Decoupled Microservices

The entire system is orchestrated by Docker Compose and designed for resilience and scalability by decoupling the fast API layer from the heavy processing layer.

Service

Technology

Role

api

FastAPI (Python)

Handles all client requests, file validation, and immediately queues parsing jobs to Celery.

worker

Celery / PyTorch

The decoupled processing engine. Executes time-consuming tasks: Text Extraction, AI Parsing, and Matching.

db

PostgreSQL

Persistent storage for parsed resume data, utilizing JSONB for a flexible, nested schema.

redis

Redis

Serves as the high-speed message broker for Celery, enabling asynchronous task queuing and communication.

⚙️ Setup and Installation

Prerequisites

You must have the following tools installed and running:

Docker Desktop (or Docker Engine)

Docker Compose

One-Command Setup

Navigate to the project root directory and execute the setup script. This script handles the image build, dependency installation (including large AI libraries), service startup, and database initialization.

chmod +x setup.sh
./setup.sh
