import asyncio
import hashlib
from bs4 import BeautifulSoup

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from news_scraper import get_latest_news
from ai_generate import ai_generate
from config import CHECK_INTERVAL, ADMIN_CHAT_ID, CHANNEL_ID

pending_news = {}
seen_links = set()

ADMIN_QUEUE_PAUSE = 5
CHANNEL_QUEUE_PAUSE = 5

admin_queue = asyncio.Queue()
channel_queue = asyncio.Queue()

# Функція для підбору емодзі за категорією/ключовими словами
def get_emoji(title: str) -> str:
    title_lower = title.lower()
    if any(word in title_lower for word in ["економ", "ринок", "фінанс", "валюта", "акції"]):
        return "📊"
    elif any(word in title_lower for word in ["політик", "уряд", "влада", "закон"]):
        return "🏛️"
    elif any(word in title_lower for word in ["спорт", "чемпіонат", "матч", "гравець"]):
        return "⚽"
    elif any(word in title_lower for word in ["технолог", "айті", "робот", "інновац"]):
        return "💻"
    else:
        return "📰"

async def send_news(bot: Bot, chat_id: int, title: str, text: str, reply_markup=None):
    emoji = get_emoji(title)
    msg_text = f"{emoji} <b>{title}</b>\n\n{text}"
    try:
        await bot.send_message(chat_id=chat_id, text=msg_text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        print(f"⚠️ Помилка надсилання: {e}")

def hash_link(link: str) -> str:
    return hashlib.sha1(link.encode()).hexdigest()[:10]

async def news_fetcher():
    while True:
        news_list = get_latest_news(seen_links)
        for news in news_list:
            news_hash = hash_link(news["link"])
            pending_news[news_hash] = news
            await admin_queue.put(news_hash)
        await asyncio.sleep(CHECK_INTERVAL)

async def admin_worker(bot: Bot):
    while True:
        news_hash = await admin_queue.get()
        news = pending_news.get(news_hash)
        if not news:
            admin_queue.task_done()
            continue

        clean_text = BeautifulSoup(news["text"], "html.parser").get_text()

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Опублікувати", callback_data=f"approve_{news_hash}"),
                InlineKeyboardButton(text="🚫 Пропустити", callback_data=f"skip_{news_hash}")
            ]
        ])

        await send_news(bot, ADMIN_CHAT_ID, news["title"], clean_text, reply_markup=keyboard)
        await asyncio.sleep(ADMIN_QUEUE_PAUSE)
        admin_queue.task_done()

async def channel_worker(bot: Bot):
    while True:
        news_hash = await channel_queue.get()
        news = pending_news.get(news_hash)
        if not news:
            channel_queue.task_done()
            continue

        try:
            formatted = await ai_generate(news["text"])
            clean_text = BeautifulSoup(formatted, "html.parser").get_text()
            await send_news(bot, CHANNEL_ID, news["title"], clean_text)
        except Exception as e:
            print(f"⚠️ Помилка каналу: {e}")

        await asyncio.sleep(CHANNEL_QUEUE_PAUSE)
        channel_queue.task_done()

async def publish_to_channel(news_hash: str):
    await channel_queue.put(news_hash)
