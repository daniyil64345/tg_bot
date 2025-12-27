
import asyncio
import hashlib
import random
import aiohttp
from bs4 import BeautifulSoup
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import CHECK_INTERVAL, ADMIN_CHAT_ID, CHANNEL_ID


class EditNewsText(StatesGroup):
    waiting_for_text = State()


pending_news = {}
seen_links = set()
admin_queue = asyncio.Queue()
channel_queue = asyncio.Queue()


DEFAULT_IMAGES = [
    "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=800",
    "https://images.unsplash.com/photo-1557408172-e596b84ad1b3?w=800",
    "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
    "https://images.unsplash.com/photo-1559027615-cd1628902df4?w=800",
    "https://images.unsplash.com/photo-1491841573634-28fb1df7d93f?w=800",
]

THEME_IMAGES = {
    "війна": [
        "https://images.unsplash.com/photo-1578070221651-94e7f47b1f9f?w=800",
        "https://images.unsplash.com/photo-1535083783855-76ae62b2914e?w=800"
    ],
    "спорт": [
        "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800",
        "https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800"
    ],
    "технолог": [
        "https://images.unsplash.com/photo-1557408172-e596b84ad1b3?w=800",
        "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=800"
    ],
    "політик": [
        "https://images.unsplash.com/photo-1559027615-cd1628902df4?w=800",
        "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800"
    ],
    "економ": [
        "https://images.unsplash.com/photo-1526374965328-7f5ae4e8e42e?w=800",
        "https://images.unsplash.com/photo-1611974260368-63fe0a9d0c1b?w=800"
    ],
}

global_bot: Bot = None


def set_bot(bot: Bot):

    global global_bot
    global_bot = bot


def get_emoji(title: str) -> str:

    t = title.lower()
    if any(w in t for w in ["економ", "фінанс", "валют", "ринок", "бізнес"]):
        return "📊"
    if any(w in t for w in ["політик", "влада", "закон", "парламент"]):
        return "🏛"
    if any(w in t for w in ["війна", "зсу", "армія", "обстріл"]):
        return "🪖"
    if any(w in t for w in ["спорт", "матч", "чемпіон"]):
        return "⚽️"
    if any(w in t for w in ["технолог", "айті", "робот", "інновац"]):
        return "💻"
    return "📰"


async def extract_image_from_article(html: str) -> str | None:

    try:
        soup = BeautifulSoup(html, "html.parser")
        
        og_image = soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            return og_image["content"]
        
        twitter_image = soup.find("meta", property="twitter:image")
        if twitter_image and twitter_image.get("content"):
            return twitter_image["content"]
        
        article = soup.find(["article", "div"], class_=lambda x: x and any(c in x.lower() for c in ["article", "post", "content", "news"]))
        if article:
            img = article.find("img")
            if img and img.get("src"):
                return img["src"]
        
        img = soup.find("img", src=True)
        if img:
            src = img["src"]
            if any(x in src.lower() for x in ["logo", "icon", "avatar", "16x16", "32x32"]):
                return None
            return src
        
    except Exception as e:
        print(f"⚠️ Помилка витягу зображення: {e}")
    
    return None


async def validate_image_url(url: str) -> bool:

    if not url:
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=5), ssl=False) as resp:
                return resp.status == 200
    except Exception as e:
        print(f"⚠️ Помилка валідації картинки {url}: {e}")
        return False


async def get_image_for_news(news: dict) -> str:

    if news.get("image"):
        if await validate_image_url(news["image"]):
            print(f"✅ Зображення з RSS: {news['image'][:50]}...")
            return news["image"]
    

    if "text" in news:
        extracted_url = await extract_image_from_article(news["text"])
        if extracted_url and await validate_image_url(extracted_url):
            print(f"✅ Зображення витягнене з text: {extracted_url[:50]}...")
            return extracted_url

    title = news.get("title", "").lower()
    for key, imgs in THEME_IMAGES.items():
        if key in title:
            return random.choice(imgs)

    return random.choice(DEFAULT_IMAGES)


async def send_news(bot: Bot, chat_id: int, title: str, text: str, reply_markup=None, image_url: str = None):

    emoji = get_emoji(title)
    clean_text = BeautifulSoup(text, "html.parser").get_text()
    caption_title = f"{emoji} <b>{title}</b>"

    try:
        if image_url:
            try:
                if len(caption_title + "\n\n" + clean_text) <= 1024:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=f"{caption_title}\n\n{clean_text}",
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                else:
                    await bot.send_photo(
                        chat_id=chat_id,
                        photo=image_url,
                        caption=caption_title,
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                    await asyncio.sleep(1)
                    await bot.send_message(chat_id=chat_id, text=clean_text, parse_mode="HTML")

                await asyncio.sleep(random.uniform(10, 20))
                return

            except (TelegramBadRequest, Exception) as e:
                print(f"⚠️ Помилка відправки фото: {e}. Надсилаємо як текст...")
        
        await bot.send_message(
            chat_id=chat_id,
            text=f"{caption_title}\n\n{clean_text}",
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        await asyncio.sleep(random.uniform(10, 20))

    except TelegramRetryAfter as e:
        await asyncio.sleep(getattr(e, "retry_after", 30))
        return await send_news(bot, chat_id, title, text, reply_markup, image_url)


def hash_link(link: str) -> str:
    return hashlib.sha1(link.encode()).hexdigest()[:10]


async def news_fetcher():
    from news_scraper import get_latest_news
    while True:
        try:
            news_list = get_latest_news(seen_links)
            for news in news_list:
                news_hash = hash_link(news["link"])
                pending_news[news_hash] = news
                await admin_queue.put(news_hash)
        except Exception as e:
            print(f"⚠️ Помилка news_fetcher: {e}")
        await asyncio.sleep(CHECK_INTERVAL)


async def admin_worker(bot: Bot):
    while True:
        news_hash = await admin_queue.get()
        news = pending_news.get(news_hash)
        if not news:
            admin_queue.task_done()
            continue

        clean_text = BeautifulSoup(news["text"], "html.parser").get_text()
        image_url = await get_image_for_news(news)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Редагувати", callback_data=f"edit_{news_hash}")],
            [InlineKeyboardButton(text="✅ Опублікувати", callback_data=f"approve_{news_hash}"),
             InlineKeyboardButton(text="🚫 Пропустити", callback_data=f"skip_{news_hash}")]
        ])
        await send_news(bot, chat_id=ADMIN_CHAT_ID, title=news["title"], text=clean_text, reply_markup=keyboard, image_url=image_url)
        admin_queue.task_done()


async def channel_worker(bot: Bot):
    while True:
        news_hash = await channel_queue.get()
        news = pending_news.get(news_hash)
        if not news:
            channel_queue.task_done()
            continue

        clean_text = BeautifulSoup(news["text"], "html.parser").get_text()
        image_url = await get_image_for_news(news)
        await send_news(bot, chat_id=CHANNEL_ID, title=news["title"], text=clean_text, image_url=image_url)
        channel_queue.task_done()


async def publish_to_channel(news_hash: str):
    await channel_queue.put(news_hash)


async def edit_text_callback_handler(bot: Bot, query: CallbackQuery, state: FSMContext):

    news_hash = query.data.replace("edit_", "")
    news = pending_news.get(news_hash)
    if not news:
        await query.answer("Новина не знайдена ❌")
        return

    clean_text = BeautifulSoup(news["text"], "html.parser").get_text()
    await query.message.answer(
        text=f"Редагуйте текст для новини:\n\n<b>{news['title']}</b>\n\nПоточний текст:\n{clean_text}",
        parse_mode="HTML"
    )

    await state.update_data(news_hash=news_hash)
    await state.set_state(EditNewsText.waiting_for_text)
    await query.answer()


async def updated_text_handler(message: Message, state: FSMContext, bot: Bot):

    data = await state.get_data()
    news_hash = data.get("news_hash")
    
    if not news_hash or news_hash not in pending_news:
        await message.answer("❌ Новина не знайдена")
        await state.clear()
        return

    pending_news[news_hash]["text"] = message.text
    await message.answer(f"✅ Текст оновлено!")
    

    image_url = await get_image_for_news(pending_news[news_hash])
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опублікувати", callback_data=f"approve_{news_hash}"),
         InlineKeyboardButton(text="🚫 Пропустити", callback_data=f"skip_{news_hash}")]
    ])
    await send_news(
        bot=bot,
        chat_id=ADMIN_CHAT_ID,
        title=pending_news[news_hash]["title"],
        text=pending_news[news_hash]["text"],
        reply_markup=keyboard,
        image_url=image_url
    )
    
    await state.clear()
