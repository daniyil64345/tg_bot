
# run.py
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from keep_alive import keep_alive  # ← додай цей імпорт
from config import API_TOKEN
from handlers import (
    admin_worker, channel_worker, news_fetcher,
    publish_to_channel, edit_text_callback_handler, updated_text_handler, 
    EditNewsText, set_bot
)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Встановлюємо глобальний bot
set_bot(bot)

# --- Callback кнопки ---
@dp.callback_query(F.data.startswith("approve_"))
async def handle_approve(query: CallbackQuery):
    news_hash = query.data.replace("approve_", "")
    await publish_to_channel(news_hash)
    try:
        await bot.edit_message_reply_markup(chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            reply_markup=None)
        await query.answer("Опубліковано ✅")
    except Exception as e:
        print(f"⚠️ Помилка опублікування новини: {e}")

@dp.callback_query(F.data.startswith("skip_"))
async def handle_skip(query: CallbackQuery):
    try:
        await bot.edit_message_reply_markup(chat_id=query.message.chat.id,
                                            message_id=query.message.message_id,
                                            reply_markup=None)
        await query.answer("Пропущено ❌")
    except Exception as e:
        print(f"⚠️ Помилка пропуску новини: {e}")

# --- Хендлер для редагування ---
@dp.callback_query(F.data.startswith("edit_"))
async def handle_edit_text(query: CallbackQuery, state: FSMContext):
    await edit_text_callback_handler(bot, query, state)

# --- Хендлер для FSM вводу тексту ---
@dp.message(EditNewsText.waiting_for_text)
async def handle_updated_text(message: Message, state: FSMContext):
    await updated_text_handler(message, state, bot)

# --- Основна функція ---
async def main():
    asyncio.create_task(news_fetcher())
    asyncio.create_task(admin_worker(bot))
    asyncio.create_task(channel_worker(bot))

    await dp.start_polling(bot)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())