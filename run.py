import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import CallbackQuery
from config import API_TOKEN, ADMIN_CHAT_ID
from handlers import news_fetcher, admin_worker, channel_worker, publish_to_channel

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.callback_query()
async def handle_buttons(callback: CallbackQuery):
    if callback.message.chat.id != ADMIN_CHAT_ID:
        await callback.answer("🚫 Не ваша кнопка")
        return

    try:
        action, news_hash = callback.data.split("_", 1)
    except ValueError:
        await callback.answer("⚠️ Невірні дані")
        return

    if action == "approve":
        await publish_to_channel(news_hash)
        await callback.message.edit_text(f"{callback.message.text}\n\n✅ Опубліковано!")
        await callback.answer("Новина додана у чергу каналу ✅")
    elif action == "skip":
        await callback.message.edit_text(f"{callback.message.text}\n\n🚫 Пропущено")
        await callback.answer("Новина пропущена 🚫")

async def main():
    asyncio.create_task(news_fetcher())
    asyncio.create_task(admin_worker(bot))
    asyncio.create_task(channel_worker(bot))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
