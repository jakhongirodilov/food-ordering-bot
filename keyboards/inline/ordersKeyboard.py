from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from .callback_data import food_callback


initialKeyboard = InlineKeyboardMarkup(row_width=1)

menu = InlineKeyboardButton(text="📖 Menu", callback_data="menu")
initialKeyboard.insert(menu)

my_orders = InlineKeyboardButton(text="📋 Mening buyurtmalarim", callback_data="my_orders")
initialKeyboard.insert(my_orders)

cart = InlineKeyboardButton(text="🛒 Savatcha", callback_data="cart")
initialKeyboard.insert(cart)

support = InlineKeyboardButton(text="🤝 Support", callback_data="support")
initialKeyboard.insert(support)

