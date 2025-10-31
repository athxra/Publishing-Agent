import os, json, requests
from datetime import datetime

PUBLISHER_URL = os.getenv('PUBLISHER_URL', 'http://localhost:8000/publish/async')
API_KEY = os.getenv('PUBLISHER_API_KEY', 'change_me')
PROCESSED_FILE = 'processed_ids.json'

ALL_BLOGS_URL = "URL"
BY_DATE_URL = "URL"

def load_processed():
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_processed(processed):
    with open(PROCESSED_FILE, 'w') as f:
        json.dump(list(processed), f)

def fetch_blogs(date=None):
    url = BY_DATE_URL.format(date=date) if date else ALL_BLOGS_URL
    print(f"Fetching blogs from {url} ...")
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data.get("blogs", [])

def publish_blog(blog):
    payload = {
        "channels": ["google_news"],
        "content": {
            "title": blog.get("title"),
            "body_html": blog.get("content"),
            "url": blog.get("url"),
            "meta_title": blog.get("meta_title"),
            "meta_description": blog.get("meta_description"),
            "image_url": blog.get("image_url"),
            "date_published": blog.get("date_published"),
        }
    }
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    r = requests.post(PUBLISHER_URL, headers=headers, json=payload)
    print(f"→ Published: {blog['title']} | {r.status_code}")
    return r.status_code in (200, 202)

def main():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    blogs = fetch_blogs(today)
    if not blogs:
        print("No new blogs today, fetching all...")
        blogs = fetch_blogs()

    processed = load_processed()
    new_blogs = [b for b in blogs if str(b['id']) not in processed]
    print(f"Found {len(new_blogs)} new blogs.")

    for blog in new_blogs:
        if publish_blog(blog):
            processed.add(str(blog['id']))

    save_processed(processed)
    print("✅ Done.")

if __name__ == '__main__':
    main()
