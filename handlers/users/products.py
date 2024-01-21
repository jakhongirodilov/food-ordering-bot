from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command

from loader import dp, db, bot

from states.selectProductState import ProductSelectState
from keyboards.inline.categoriesKeyboard import categories_keyboard
from keyboards.inline.ordersKeyboard import initialKeyboard
from utils.db_api import sqlite


# @dp.callback_query_handler(text="order")
# async def start_order(callback_query: types.CallbackQuery):
#     await dp.bot.answer_callback_query(callback_query.id)
#     await dp.bot.send_message(callback_query.from_user.id, "To'liq ismingizni kiriting")
#     await ProductSelectState.full_name.set()


# # ism-familiya kiritish
# @dp.message_handler(state=ProductSelectState.full_name)
# async def answer_fullname(message: types.Message, state: FSMContext):
#     fullname = message.text

#     await state.update_data(
#         {"name": fullname}
#     )

#     await message.answer("Telefon raqamingizni kiriting:")

#     await ProductSelectState.next()


# # telefon raqam kiritish
# @dp.message_handler(state=ProductSelectState.phone_number)
# async def answer_phone(message: types.Message, state: FSMContext):
#     phone = message.text

#     await state.update_data(
#         {"phone": phone}
#     )

#     # Ma`lumotlarni qayta o'qiymiz
#     data = await state.get_data()
#     name = data.get("name")
#     phone = data.get("phone")

#     msg = "Quyidai ma`lumotlar qabul qilindi:\n"
#     msg += f"Ismingiz - {name}\n"
#     msg += f"Telefon: - {phone}"
#     await message.answer(msg)

#     await bot.send_message(message.chat.id, "Yegulik kategoriyasini tanlang:", reply_markup=categories_keyboard)
#     # await message.answer("Yegulik kategoriyasini tanlang:", reply_markup=categories_keyboard)

#     await ProductSelectState.next()


# kategoriyalarni ko'rsatish
@dp.callback_query_handler(text="menu")
async def start_order(callback_query: types.CallbackQuery):
    await dp.bot.answer_callback_query(callback_query.id)
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await bot.send_message(callback_query.from_user.id, "Yegulik kategoriyasini tanlang:", reply_markup=categories_keyboard)

    await ProductSelectState.select_category.set()


# kategoriyadagi mahsulotlarni ko'rsatish
@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('category_'), state=ProductSelectState.select_category)
async def products_in_category(callback_query: types.CallbackQuery, state: FSMContext):
    category = callback_query.data.split('_')[1]


    products_by_category = db.select_products_by_category(category=category)
    
    if products_by_category:
        productsKeyboard = InlineKeyboardMarkup(row_width=1)
        for product in products_by_category:
            product_id = product[0]
            productsKeyboard.add(InlineKeyboardButton(text=product[1].capitalize(), callback_data=product_id))
        productsKeyboard.add(InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel"))

        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, f"{category.capitalize()} kategoriyasidagi mahsulotlar:", reply_markup=productsKeyboard)
        # await callback_query.answer(cache_time=60)
        await ProductSelectState.next()

    else:
        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        await bot.send_message(callback_query.from_user.id, "Ushbu kategoriyada mahsulotlar mavjud emas...", reply_markup=initialKeyboard)
        await state.finish()


@dp.callback_query_handler(lambda callback_query: callback_query.data.isdigit(), state=ProductSelectState.select_food)
async def products(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data)

    print(product_id)
    await state.update_data(
        {"product_id": product_id}
    )

    product_details = db.select_product(id=product_id)

    # Inline keyboard for adjusting quantity and adding to cart
    add_to_cart_keyboard = InlineKeyboardMarkup(row_width=4)
    # Add buttons for decrementing, displaying and incrementing quantity
    add_to_cart_keyboard.add(
        InlineKeyboardButton(text="-", callback_data="decrease"),
        InlineKeyboardButton(text="1", callback_data="quantity"),
        InlineKeyboardButton(text="+", callback_data="increase"))
    add_to_cart_keyboard.add(
        InlineKeyboardButton(text="Add to Cart", callback_data="add_to_cart")
    )
    add_to_cart_keyboard.add(InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel"))

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    # Display product details with quantity adjustment and add to cart options
    await bot.send_message(
        callback_query.from_user.id,
        f"Product: {product_details[1]}\n"
        f"Category: {product_details[2]}\n"
        f"Price: {int(product_details[3])}so'm\n",
        reply_markup=add_to_cart_keyboard
    )

    await ProductSelectState.next()


# tanlangan mahsulotni savatchaga qo'shish
@dp.callback_query_handler(text="add_to_cart", state=ProductSelectState.add_to_cart)
async def add_to_cart(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback_query.from_user.id
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1) # Get the quantity from the state data, default to 1

    # Check if the product is already in the cart
    if db.get_cart_item(user_id, product_id):
        # If yes, increment the quantity by the selected amount
        db.increment_quantity(quantity, user_id, product_id)
    else:
        # If not, add the product to the cart with the selected quantity
        db.add_to_cart(user_id=user_id, product_id=product_id, quantity=quantity)

    product_name = db.select_product(product_id)[1]

    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)

    added_to_cart = InlineKeyboardMarkup(row_width=1)
    added_to_cart.add(
        InlineKeyboardButton(text="📖 Menu", callback_data="menu")
    )
    added_to_cart.add(
        InlineKeyboardButton(text="🛒 Savatcha", callback_data="cart")
    )

    cart = InlineKeyboardButton(text="🛒 Savatchaga o'tish", callback_data="cart")

    await bot.send_message(callback_query.from_user.id, f"{product_name.capitalize()} savatga qo'shildi ✅", reply_markup=categories_keyboard)
    await state.finish()


# kamaytirish tugmasini bosganda
@dp.callback_query_handler(text="decrease", state=ProductSelectState.add_to_cart)
async def decrease_quantity(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get("quantity", 1) # Get the quantity from the state data, default to 1
    if quantity > 1: # Only decrease if quantity is more than 1
        quantity -= 1 # Decrement the quantity by 1
        await state.update_data(quantity=quantity) # Update the state data with the new quantity
        
        # Edit the message and the inline keyboard with the new quantity
        
        # Inline keyboard for adjusting quantity and adding to cart
        add_to_cart_keyboard = InlineKeyboardMarkup(row_width=4)
        # Add buttons for decrementing, displaying and incrementing quantity
        add_to_cart_keyboard.add(
            InlineKeyboardButton(text="-", callback_data="decrease"),
            InlineKeyboardButton(text=str(quantity), callback_data="quantity"),
            InlineKeyboardButton(text="+", callback_data="increase"))
        add_to_cart_keyboard.add(
            InlineKeyboardButton(text="Add to Cart", callback_data="add_to_cart")
        )
        add_to_cart_keyboard.add(InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel"))

        await bot.edit_message_text(
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            text=callback_query.message.text,
            reply_markup=add_to_cart_keyboard
        )

# oshirish tugmasini bosganda
@dp.callback_query_handler(text="increase", state=ProductSelectState.add_to_cart)
async def increase_quantity(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quantity = data.get("quantity", 1) # Get the quantity from the state data, default to 1
    quantity += 1 # Increment the quantity by 1
    await state.update_data(quantity=quantity) # Update the state data with the new quantity
    # Edit the message and the inline keyboard with the new quantity

    # Inline keyboard for adjusting quantity and adding to cart
    add_to_cart_keyboard = InlineKeyboardMarkup(row_width=4)
    # Add buttons for decrementing, displaying and incrementing quantity
    add_to_cart_keyboard.add(
        InlineKeyboardButton(text="-", callback_data="decrease"),
        InlineKeyboardButton(text=str(quantity), callback_data="quantity"),
        InlineKeyboardButton(text="+", callback_data="increase"))
    add_to_cart_keyboard.add(
        InlineKeyboardButton(text="Add to Cart", callback_data="add_to_cart")
    )
    add_to_cart_keyboard.add(InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="cancel"))

    await bot.edit_message_text(
        chat_id=callback_query.from_user.id,
        message_id=callback_query.message.message_id,
        text=callback_query.message.text,
        reply_markup=add_to_cart_keyboard
    )



@dp.callback_query_handler(text="cancel", state='*')
async def cancel_buying(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
    await state.reset_state()

    await bot.send_message(callback_query.from_user.id, "Amaliyot bekor qilindi!", reply_markup=initialKeyboard)