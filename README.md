# 📰 Publisher Agent

Automated system to fetch blog posts from PrestaShop and publish them to Google News through a Google News–compliant RSS feed.

---

## 🚀 Overview

The **Publisher Agent** automates the end-to-end publishing workflow:

* Fetches blog posts from your **PrestaShop API**
* Converts them into valid **RSS feed entries**
* Automatically **pings Google WebSub Hub** to notify Google News
* Runs continuously via **Celery workers** and **Docker containers**

---

## 🧩 System Architecture

**Components:**

* **FastAPI** – Exposes `/publish` and `/publish/async` endpoints
* **Celery** – Manages background publishing tasks
* **Redis** – Acts as the message broker
* **Docker Compose** – Handles containerized deployment
* **RSS Feed** – Hosted at `/public/rss.xml`, updated automatically

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/publisher-agent.git
cd publisher-agent
```

### 2️⃣ Create a `.env` File

Create a `.env` file in the root directory with the following values:

```
PUBLISHER_API_KEY=your_secret_api_key
RSS_BASE_URL=https://insightsgulfstore.com
WEB_SUB_HUB=https://pubsubhubbub.appspot.com
REDIS_URL=redis://redis:6379/0
RSS_FEED_PATH=/app/public/rss.xml
PRESTASHOP_API_URL=https://insightsgulfstore.com/module/blogapi/api?action=all-blogs
```

> ⚠️ Never upload your `.env` file to GitHub.

---

## 🐳 Docker Deployment

### Build and Run:

```bash
cd deploy
docker compose --env-file ../.env up --build
```

This will start:

* **publisher_web** → FastAPI server ([http://127.0.0.1:8000](http://127.0.0.1:8000))
* **publisher_worker** → Celery worker
* **publisher_redis** → Redis broker

---

## 🧠 API Endpoints

### **`POST /publish`**

Immediately publishes a new blog post to the RSS feed.

Example Request:

```json
{
  "channels": ["google_news"],
  "content": {
    "title": "First Blog Test",
    "body_html": "<p>This is a sample blog for RSS generation.</p>",
    "url": "https://insightsgulfstore.com/test-blog-1",
    "meta_title": "Test Blog 1",
    "meta_description": "Sample RSS generation post",
    "image_url": "https://insightsgulfstore.com/img/test.jpg",
    "date_published": "2025-10-31T14:00:00Z"
  }
}
```

---

## 🔄 Integration with PrestaShop

A helper script `scripts/publish_prestashop.py` automates blog fetching:

* Calls PrestaShop API (`/all-blogs` or `/by-date`)
* Sends each entry to `/publish`
* Keeps Google News up to date automatically

---

## 🗞️ Google News Integration

* RSS feed hosted at:
  **`https://insightsgulfstore.com/rss.xml`**
* The system notifies Google via **WebSub Hub**:
  `https://pubsubhubbub.appspot.com`
* To appear in **Google News**, register your RSS feed in [Google Publisher Center](https://publishercenter.google.com/)

---

## 🧾 File Structure

```
publisher-agent/
│
├── app/
│   ├── celery_app.py
│   ├── main.py
│   ├── oauth_stub.py
│   ├── tasks.py
│   └── publishers/
│       └── google_news_publisher.py
│
├── deploy/
│   ├── docker-compose.yml
│   └── Dockerfile
│
├── public/
│   └── rss.xml
│
├── scripts/
│   └── publish_prestashop.py
│
├── .env
├── README.md
└── requirements.txt
```

