
import feedparser
from bs4 import BeautifulSoup
from config import NEWS_FEEDS

SERIOUS_KEYWORDS = [
    "україна", "війна", "зсу", "армія", "обстріл", "ракет", "дрон", "окупаці", "контрнаступ",
    "політик", "уряд", "влада", "президент", "прем'єр", "парламент", "вибор", "закон",
    "економ", "фінанс", "валюта", "банк", "бізнес", "ринок",
    "європа", "сша", "росія", "китай", "нато", "ООН", "міжнародн",
    "пожежа", "повінь", "землетрус", "аварія", "катастрофа",
    "інновац", "технологі", "штучний інтелект", "космос"
]

SKIP_KEYWORDS = [
    "погода", "рецепт", "розваги", "концерт", "шоу", "акція", "знижка", "фото", "мем",
    "пробки", "затори", "транспорт", "оновлення", "смартфон"
]


def is_serious_news(title: str, summary: str) -> bool:
    """Перевіряє, чи новина серйозна за ключовими словами"""
    text = f"{title} {summary}".lower()
    if any(w in text for w in SKIP_KEYWORDS):
        return False
    return any(w in text for w in SERIOUS_KEYWORDS)


def extract_image_from_entry(entry) -> str | None:
    """Витягує картинку з RSS запису в порядку пріоритету"""
    
    # 1. Шукаємо в summary (HTML)
    summary = getattr(entry, "summary", "") or ""
    if summary:
        soup = BeautifulSoup(summary, "html.parser")
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            return img_tag.get("src")
    
    # 2. Шукаємо в content[0].value
    if hasattr(entry, "content") and entry.content:
        try:
            soup_c = BeautifulSoup(entry.content[0].value, "html.parser")
            img_tag = soup_c.find("img")
            if img_tag and img_tag.get("src"):
                return img_tag.get("src")
        except Exception as e:
            print(f"⚠️ Помилка парсингу content: {e}")
    
    # 3. Шукаємо в media_content
    if hasattr(entry, "media_content"):
        try:
            media = getattr(entry, "media_content", None)
            if media and isinstance(media, list) and len(media) > 0:
                if media[0].get("url"):
                    return media[0].get("url")
        except Exception as e:
            print(f"⚠️ Помилка парсингу media_content: {e}")
    
    # 4. Шукаємо в media_thumbnail
    if hasattr(entry, "media_thumbnail"):
        try:
            thumbnail = getattr(entry, "media_thumbnail", None)
            if thumbnail and isinstance(thumbnail, list) and len(thumbnail) > 0:
                if thumbnail[0].get("url"):
                    return thumbnail[0].get("url")
        except Exception as e:
            print(f"⚠️ Помилка парсингу media_thumbnail: {e}")
    
    # 5. Шукаємо в enclosures
    if hasattr(entry, "enclosures"):
        try:
            for enclosure in entry.enclosures:
                if enclosure.type and "image" in enclosure.type.lower():
                    return enclosure.href
        except Exception as e:
            print(f"⚠️ Помилка парсингу enclosures: {e}")
    
    return None


def get_latest_news(seen_links: set):
    """Отримує нові новини з RSS фідів"""
    new_items = []
    
    for feed_url in NEWS_FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
            
            for entry in parsed.entries:
                link = getattr(entry, "link", None)
                title = getattr(entry, "title", "")
                summary = getattr(entry, "summary", "") or ""
                
                if not link or not title:
                    continue
                
                # Перевіряємо чи це серйозна новина
                if not is_serious_news(title, summary):
                    continue
                
                # Перевіряємо чи вже бачили цей лінк
                if link in seen_links:
                    continue
                
                # Витягуємо картинку
                image = extract_image_from_entry(entry)
                
                seen_links.add(link)
                new_items.append({
                    "title": title,
                    "text": summary,
                    "link": link,
                    "image": image
                })
                
        except Exception as e:
            print(f"⚠️ Помилка RSS ({feed_url}): {e}")
    
    return new_items