import sqlite3
from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from data.config import ADMINS
from keyboards.inline.ordersKeyboard import initialKeyboard

from loader import dp, db, bot


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    name = message.from_user.full_name

    try:
        db.add_user(id=message.from_user.id, name=name)
    except sqlite3.IntegrityError as err:
        await bot.send_message(chat_id=ADMINS[0], text=err)

    await message.answer(f"Salom, {message.from_user.full_name}! \nBotimizga xush kelibsiz!!!", reply_markup=initialKeyboard)
    
    # adminga yangi foydalanuvchi haqida xabar berish
    count = db.count_users()[0]
    msg = f"{message.from_user.full_name} bazaga qo'shildi.\nBazada {count} ta foydalanuvchi bor."
    await bot.send_message(chat_id=ADMINS[0], text=msg)