Deployment Guide

This guide provides the necessary steps to set up and run the entire AI Resume Parser application using Docker and Docker Compose, fulfilling the hackathon submission requirements.

Prerequisites

Git: Installed and configured.

Docker: Docker Desktop (Windows/Mac) or Docker Engine (Linux) installed and running.

1. Setup and Initialization (One Command)

The entire environment is set up via the required setup.sh script.

Clone the repository:

git clone [Your GitHub Repo URL]
cd resume-parser-ai

Run the automated setup script:

./setup.sh

This script performs the following critical actions:

Builds all Docker images, installing all AI/ML dependencies (PyTorch/Transformers).

Starts the four services: api, db, redis, and worker.

Executes the database migration script to create the resumes table.

2. Verification

Once the script completes, confirm the core services are running by checking your terminal logs:

API Gateway: You should see INFO: Uvicorn running on http://0.0.0.0:8000

Worker Engine: You should see celery@... ready.

3. Usage and Testing

The application is fully accessible via the exposed port 8000.

A. API Documentation (Swagger UI)

Access URL: http://localhost:8000/docs

B. Resume Upload and Parsing (Core Feature)

Endpoint: POST /resumes/upload

Flow: Upload a resume file using the Swagger UI. The API will return 202 Accepted.

Monitor: The worker-1 logs will show the extraction, AI/ML processing, and final status update to completed.

C. Resume-Job Matching (Advanced Feature)

Endpoint: POST /resumes/{id}/match

Flow: Use the ID from the successful upload and submit the job description JSON via the Swagger UI.

Result: API returns 200 OK with the calculated overallScore and gapAnalysis.
