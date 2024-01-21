from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


product_categories = ["🥤 drinks", "🍔 burgers", "🍕 pizzas", "🍨 desserts", "🥗 salads"]

categories_keyboard = InlineKeyboardMarkup(row_width=1)
for category in product_categories:
    categories_keyboard.add(InlineKeyboardButton(text=category, callback_data=f"category_{category.split()[1]}"))
categories_keyboard.add(InlineKeyboardButton(text="🔙 ortga", callback_data="cancel"))
