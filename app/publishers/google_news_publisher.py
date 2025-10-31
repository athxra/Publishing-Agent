import os
from feedgen.feed import FeedGenerator
from datetime import datetime
import xml.etree.ElementTree as ET

RSS_PATH = os.getenv("RSS_FEED_PATH", "/app/public/rss.xml")
BASE_URL = os.getenv("RSS_BASE_URL", "http://localhost:8000")

def _load_existing_feed():
    if not os.path.exists(RSS_PATH):
        return None
    try:
        tree = ET.parse(RSS_PATH)
        return tree
    except Exception:
        return None

def publish_entry(entry: dict):
    fg = FeedGenerator()
    existing = _load_existing_feed()
    if existing is not None:
        root = existing.getroot()
        ch = root.find('channel')
        title = ch.find('title').text if ch is not None and ch.find('title') is not None else 'Publisher Agent Feed'
        link = ch.find('link').text if ch is not None and ch.find('link') is not None else BASE_URL
        desc = ch.find('description').text if ch is not None and ch.find('description') is not None else 'Auto-generated feed'
        fg.title(title)
        fg.link(href=link)
        fg.description(desc)
    else:
        fg.title('Publisher Agent Feed')
        fg.link(href=BASE_URL)
        fg.description('Auto-generated feed')

    fe = fg.add_entry()
    fe.id(entry.get('url'))
    fe.title(entry.get('title'))
    fe.link(href=entry.get('url'))
    fe.published(entry.get('date_published') or datetime.utcnow().isoformat())
    fe.content(entry.get('body_html') or '', type='CDATA')

    rss_str = fg.rss_str(pretty=True)
    os.makedirs(os.path.dirname(RSS_PATH), exist_ok=True)
    with open(RSS_PATH, 'wb') as f:
        f.write(rss_str)
    return True
