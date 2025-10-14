# news_scraper.py
import feedparser
from bs4 import BeautifulSoup
from config import NEWS_FEEDS


def get_latest_news(seen_links: set):
    new_items = []

    for feed_url in NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            for entry in parsed.entries:
                link = entry.link
                title = entry.title
                summary = entry.get("summary", "")

                image = None

                # 1. <img> в summary
                soup = BeautifulSoup(summary, "html.parser")
                img_tag = soup.find("img")
                if img_tag:
                    image = img_tag.get("src")

                # 2. content[0].value
                if not image and hasattr(entry, "content") and entry.content:
                    soup_content = BeautifulSoup(entry.content[0].value, "html.parser")
                    img_tag = soup_content.find("img")
                    if img_tag:
                        image = img_tag.get("src")

                # 3. media_content
                if not image and "media_content" in entry:
                    media = entry.media_content
                    if media and isinstance(media, list):
                        image = media[0].get("url")

                if link not in seen_links:
                    seen_links.add(link)
                    new_items.append({
                        "title": title,
                        "text": summary,
                        "link": link,
                        "image": image
                    })
        except Exception as e:
            print(f"⚠️ Помилка RSS: {feed_url} — {e}")

    return new_items
