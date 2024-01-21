import sqlite3
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command
from data.config import ADMINS
from keyboards.inline.ordersKeyboard import initialKeyboard
from keyboards.inline.categoriesKeyboard import categories_keyboard
from states.addProductState import AddProduct

from loader import dp, db, bot


@dp.message_handler(Command("addproduct"), state=None, user_id=ADMINS)
async def cmd_add_product(message: types.Message):
    await message.answer("Mahsulot nomini kiriting:")
    await AddProduct.name.set()


@dp.message_handler(state=AddProduct.name)
async def product_name(message: types.Message, state: FSMContext):
    name = message.text

    await state.update_data(
        {"name": name}
    )

    await message.answer("Mahsulot turini kiriting:", reply_markup=categories_keyboard)

    await AddProduct.next()



@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('category_'), state=AddProduct.category)
async def product_category(callback_query: types.CallbackQuery, state: FSMContext):
    # Extract category from callback data
    category = callback_query.data.split('_')[1]

    await state.update_data(
        {"category": category}
    )

    await bot.send_message(callback_query.from_user.id, "Mahsulot narxini kiriting:")
    await AddProduct.next()


@dp.message_handler(state=AddProduct.price)
async def product_name(message: types.Message, state: FSMContext):
    price = message.text

    await state.update_data(
        {"price": price}
    )

    data = await state.get_data()
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')

    db.add_product(name=name, category=category, price=price)

    await message.answer(f"Mahsulot bazaga, \"{category}\" kategoriyasiga qo'shildi!")
    await message.answer(f"{category} kategoriyasidagi mahsulotlar: {db.select_products_by_category(category=category)}")
    await state.reset_state()


@dp.message_handler(Command("delete_all_products"), state=None)
async def cmd_delete_all_products(message: types.Message):
    # Check if the user is an admin
    if message.from_user.id == ADMINS:
        await message.answer("Bazadan mahsulotlarni o'chirish uchun admin bo'lishingiz kerak!")
        return
    
    db.delete_products()
    await message.answer("Barcha mahsulot o'chirildi!")




