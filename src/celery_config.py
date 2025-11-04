# src/celery_config.py

from celery import Celery
import os

# Get Redis URL from environment variable set in docker-compose.yml
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Initialize Celery application
celery_app = Celery(
    'resume_parser_tasks',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['src.tasks']  # We will put our long-running tasks here
)

# Optional: Configure Timezone
celery_app.conf.update(
    enable_utc=True,
    timezone='Asia/Kolkata', # Set a timezone appropriate for you
)