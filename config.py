
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ⚠️ ВАЖЛИВО: Не комітьте реальні токени! Використовуйте .env файл
API_TOKEN = os.getenv("API_TOKEN", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@your_channel")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))

NEWS_FEEDS = [
    "https://www.pravda.com.ua/rss/view_news/",
    "https://censor.net/ua/rss/all",
    "https://www.unian.ua/rss",
    "https://nv.ua/rss/all.xml",
    "https://24tv.ua/rss/all.xml",
    "https://lb.ua/rss",
    "https://gazeta.ua/rss",
    "https://glavcom.ua/rss",
    "https://zaxid.net/rss",
    "https://www.rbc.ua/static/rss/all.rus.rss"
]

OLLAMA_CMD = os.getenv("OLLAMA_CMD", "ollama")

# Optional: increase delays to avoid telegram flood
MIN_SEND_DELAY = float(os.getenv("MIN_SEND_DELAY", 4.0))
MAX_SEND_DELAY = float(os.getenv("MAX_SEND_DELAY", 6.5))
FALLBACK_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"