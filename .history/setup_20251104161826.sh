#!/bin/bash

# --- Resume Parser AI Setup Script ---

echo "Starting Resume Parser AI Setup..."

# 1. Stop and clean up any previous running containers and volumes
echo "1. Cleaning up previous Docker environment..."
docker-compose down -v --remove-orphans

# 2. Build Docker images (API and Worker)
echo "2. Building Docker images (This may take 15-20 minutes due to PyTorch/Transformers installation)..."
docker-compose build

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Docker build failed. Please check the error logs and connectivity."
    exit 1
fi

# 3. Start the core services (DB, Redis, API, Worker)
echo "3. Starting services (PostgreSQL, Redis, FastAPI, Celery Worker)..."
docker-compose up -d

# Check if services started
if [ $? -ne 0 ]; then
    echo "ERROR: Docker Compose failed to start services."
    exit 1
fi

# Give the database a moment to initialize before creating tables
echo "Waiting 10 seconds for PostgreSQL to initialize..."
sleep 10

# 4. Create database tables (resumes table)
echo "4. Executing database migrations..."
docker-compose run --rm api python -c "from src.models import Base, engine; Base.metadata.create_all(bind=engine)"

if [ $? -ne 0 ]; then
    echo "WARNING: Database creation script failed. Check if DB is accessible."
fi


echo "--- Setup Complete! ---"
echo "API is accessible at: http://localhost:8000"
echo "Swagger Documentation: http://localhost:8000/docs"
echo "To view logs, run: docker-compose logs -f"
echo "To stop services, run: docker-compose down"
