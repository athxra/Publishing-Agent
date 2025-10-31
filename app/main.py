from fastapi import FastAPI, HTTPException, Request, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from app import tasks
from app.oauth_stub import router as oauth_router

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(
    title="Publisher Agent",
    version="0.1.0",
    description="Publishes PrestaShop blogs to Google News RSS feed"
)
app.include_router(oauth_router)

# Environment key
PUBLISHER_API_KEY = os.getenv("PUBLISHER_API_KEY", "change_me")

# Security scheme for Swagger UI
security = HTTPBearer()

def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Verify Bearer token against environment API key."""
    if not PUBLISHER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server missing PUBLISHER_API_KEY"
        )
    if credentials.credentials != PUBLISHER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    return credentials.credentials


# Data models
class ContentItem(BaseModel):
    title: str
    body_html: str | None = None
    url: str
    meta_title: str | None = None
    meta_description: str | None = None
    image_url: str | None = None
    date_published: str | None = None


class PublishRequest(BaseModel):
    channels: list[str]
    content: ContentItem | None = None
    content_dir: str | None = None


# Sync publishing route
@app.post("/publish")
async def publish_sync(payload: PublishRequest, api_key: str = Depends(verify_api_key)):
    if payload.content is None:
        raise HTTPException(status_code=400, detail="No content provided")

    if "google_news" in payload.channels:
        res = tasks.publish_to_google_news.apply(args=[payload.content.dict()])
        return {"task": res.result}
    return {"status": "no-op", "detail": "channel not supported"}


# Async publishing route
@app.post("/publish/async")
async def publish_async(payload: PublishRequest, api_key: str = Depends(verify_api_key)):
    if payload.content is None:
        raise HTTPException(status_code=400, detail="No content provided")

    if "google_news" in payload.channels:
        task = tasks.publish_to_google_news.delay(payload.content.dict())
        return {"task_id": task.id}
    return {"status": "no-op", "detail": "channel not supported"}
