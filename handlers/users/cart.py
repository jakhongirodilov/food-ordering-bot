from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.builtin import CommandStart, Command

from loader import dp, db, bot

from states.selectProductState import ProductSelectState
from keyboards.inline.categoriesKeyboard import categories_keyboard
from keyboards.inline.ordersKeyboard import initialKeyboard
from utils.db_api import sqlite



@dp.callback_query_handler(text="cart", state=None)
async def handle_cart_button(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id

    cart = db.get_cart_products(chat_id)
    print(cart)

    if cart:
        msg = f"Savatchadagi mahsulotlar: \n\n"
        total_cost = 0
        for object in cart:
            product_id = object[2]
            product = db.select_product(id=product_id)
            product_name = product[1]
            # print(type(product))
            quantity = object[3]
            price = product[3]
            total_cost += price*quantity
        
            msg += f"Mahsulot nomi: {product_name}\nMiqdori: {quantity}\nNarxi: {int(price)*quantity}so'm\n\n"
        msg += f"Umumiy narx: {int(total_cost)}so'm\n"

        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        
        keyboard = InlineKeyboardMarkup(row_width=1)

        menu = InlineKeyboardButton(text="➕🛒 Mahsulot qo'shish", callback_data="menu")
        keyboard.insert(menu)

        clear = InlineKeyboardButton(text="🔄🛒 Savatchani tozalash", callback_data="clear")
        keyboard.insert(clear)

        order = InlineKeyboardButton(text="📦✅ Buyurtma berish", callback_data="order")
        keyboard.insert(order)

        keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="cancel"))

        await bot.send_message(chat_id, msg, reply_markup=keyboard)

        
    else: 
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

        keyboard = InlineKeyboardMarkup(row_width=1)

        menu = InlineKeyboardButton(text="Mahsulot qo'shish", callback_data="menu")
        keyboard.insert(menu)

        keyboard.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="cancel"))

        await bot.send_message(chat_id, "Savatchangizda mahsulotlar mavjud emas...", reply_markup=keyboard)

    await callback_query.answer()


@dp.callback_query_handler(text="clear", state=None)
async def clear_cart(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    db.clear_cart(user_id=user_id)

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Savatchangiz tozalandi!", reply_markup=initialKeyboard)