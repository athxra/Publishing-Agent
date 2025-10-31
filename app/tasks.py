import os
import requests
from app.celery_app import celery_app
from app.publishers.google_news_publisher import publish_entry


def notify_websub_hub():
    """Ping Google News WebSub (PubSubHubbub) hub when RSS feed updates."""
    hub_url = os.getenv("WEB_SUB_HUB", "").strip()
    rss_base_url = os.getenv("RSS_BASE_URL", "").strip()

    if not hub_url or not rss_base_url:
        print("⚠️ Skipping WebSub ping — missing WEB_SUB_HUB or RSS_BASE_URL.")
        return

    rss_url = f"{rss_base_url.rstrip('/')}/rss.xml"
    print(f"🔔 Pinging Google News hub for: {rss_url}")

    try:
        response = requests.post(
            hub_url,
            data={
                "hub.mode": "publish",
                "hub.url": rss_url,
            },
            timeout=10,
        )
        if response.status_code in (204, 202):
            print("✅ WebSub ping successful!")
        else:
            print(f"⚠️ WebSub ping returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ WebSub ping failed: {e}")


@celery_app.task(name="tasks.publish_to_google_news")
def publish_to_google_news(content: dict):
    """
    Celery task: publishes a blog entry to Google News RSS feed,
    then pings the WebSub hub to notify Google.
    """
    try:
        # Publish to Google News (write to RSS)
        publish_entry(content)

        # Notify Google News hub
        notify_websub_hub()

        return {"status": "ok", "url": content.get("url")}
    except Exception as e:
        print(f"❌ Error publishing entry: {e}")
        return {"status": "error", "error": str(e)}
