import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

import gpt
import secure_data
import db

API_TOKEN = secure_data.TELEGRAM_API_KEY

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    db.init_user(message.chat.id)
    await message.answer(message.text)


@dp.message_handler(commands=['help'])
async def help_handler(message: types.Message):
    await message.answer(
        "Тех поддержка Бота t.me/cursor_tech.\nЕсли бот перестал отвечать, просто очистите историю через *Меню* и продублируйте вопрос.")


@dp.message_handler(commands=['settings'])
async def settings_handler(message: types.Message):
    kb = InlineKeyboardMarkup()
    user_data = db.get_user_data(message.chat.id)
    new_status = '-'
    visual_status = '✅'
    if user_data.need_translation is False:
        new_status = '+'
        visual_status = '❌'
    kb.add(InlineKeyboardButton(text=f"Перевод запроса {visual_status}", callback_data=f'set_translate_{new_status}'))
    await message.answer('⚙ Настройки', reply_markup=kb)


@dp.callback_query_handler(lambda data: 'set_translate' in data.data)
async def set_translate_handler(data: CallbackQuery):
    to_what_set = data.data.replace('set_translate_', '')
    db.change_translation_status(data.message.chat.id, to_what_set)
    await data.answer("Успешно!")
    kb = InlineKeyboardMarkup()
    user_data = db.get_user_data(data.message.chat.id)
    new_status = '-'
    visual_status = '✅'
    if user_data.need_translation is False:
        new_status = '+'
        visual_status = '❌'
    kb.add(InlineKeyboardButton(text=f"Перевод запроса {visual_status}", callback_data=f'set_translate_{new_status}'))
    await data.message.edit_reply_markup(reply_markup=kb)


@dp.message_handler(commands=['clear'])
async def clear_handler(message: types.Message):
    db.clear_history(message.chat.id)
    await message.answer('История очищена')


@dp.message_handler()
async def handle_requests(message: types.Message):
    user_data = db.get_user_data(message.chat.id)
    if user_data.requests_value == 4:
        return  # Тут код поста заказчика
    elif user_data.requests_value == 0:
        return  # Тут код оплаты заказчика
    db.update_requests_before_pay(message.chat.id, user_data.requests_value - 1)
    loop = asyncio.get_event_loop()
    user_data.context += f"User: {message}\n"
    answer = await loop.run_in_executor(None, gpt.get_answer, user_data.context)
    user_data.context += f'Bot: {answer}'
    await message.answer(answer)
    db.update_request_context(user_data.chat_id, user_data.context)


executor.start_polling(dp, skip_updates=True)
