import os
API_TOKEN = os.getenv("API_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") # група або твій чат
CHANNEL_ID = os.getenv("CHANNEL_ID")

CHECK_INTERVAL = 300  # інтервал перевірки новин у секундах

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