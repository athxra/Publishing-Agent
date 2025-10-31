from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
celery_app = Celery("publisher", broker=redis_url, backend=redis_url)
celery_app.conf.task_routes = {"tasks.publish_to_google_news": {"queue": "publishers"}}
