# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = "8320380215:AAHyIRxWdhjHw2a6ZAXoK6GV1QDM1jI48zc"
CHANNEL_ID = "@elcapononews"
ADMIN_CHAT_ID = -1003135405579
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