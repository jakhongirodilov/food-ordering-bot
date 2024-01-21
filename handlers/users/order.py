from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db, bot

from states.createOrderState import Order
from keyboards.default.contact import contact_keyboard
from keyboards.inline.ordersKeyboard import initialKeyboard



@dp.callback_query_handler(text="order")
async def start_order(callback_query: types.CallbackQuery):
    await dp.bot.answer_callback_query(callback_query.id)
    await dp.bot.send_message(callback_query.from_user.id, "To'liq ismingizni kiriting")
    await Order.full_name.set()


# ism-familiya kiritish
@dp.message_handler(state=Order.full_name)
async def answer_fullname(message: types.Message, state: FSMContext):
    fullname = message.text

    await state.update_data(
        {"name": fullname}
    )

    await message.answer("Telefon raqamingizni kiriting:", reply_markup=contact_keyboard)

    await Order.next()

# Handler to process the received contact
@dp.message_handler(content_types=types.ContentType.CONTACT, state=Order.phone_number)
async def process_contact(message: types.Message, state: FSMContext):
    phone_number = str(message.contact.phone_number)
    print(phone_number)

    await state.update_data(
        {"phone_number": phone_number}
    )

    await message.answer("Manzil kiriting:", reply_markup=types.ReplyKeyboardRemove())

    await Order.next()


@dp.message_handler(state=Order.address)
async def answer_address(message: types.Message, state: FSMContext):
    address = message.text

    await state.update_data(
        {"address": address}
    )

    # Ma`lumotlarni qayta o'qiymiz
    data = await state.get_data()
    name = data.get("name")
    phone = data.get("phone_number")
    address = data.get("address")

    msg = "Quyidai ma`lumotlar qabul qilindi:\n"
    msg += f"Ismingiz - {name}\n"
    msg += f"Telefon: - {phone}\n"
    msg += f"Address: - {address}"
    await message.answer(msg)

    cart_products = db.get_cart_products(message.from_user.id)
    """
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    """

    for product in cart_products:
        db.create_order(user_id=product[1], product_id=product[2], quantity=product[3], full_name=name, phone_number=phone, address=address)

    db.clear_cart(message.from_user.id)

    await state.finish()
    await bot.send_message(message.from_user.id, "Buyurtmangiz saqlandi ✅", reply_markup=initialKeyboard)


# my_orders
@dp.callback_query_handler(text="my_orders", state=None)
async def my_orders(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id

    orders = db.get_orders(chat_id)
    print(orders)

    if orders:
        msg = f"Buyurtmalaringiz: \n\n"
        for order in orders:
            product_id = order[2]
            product = db.select_product(id=product_id)[1]
            quantity = order[3]
            name = order[4]
            phone_number = order[5]
            address = order[6]

            msg += f"-----------------------------\n\n"
            msg += f"Mahsulot nomi: {product}\n"
            msg += f"Miqdori: {quantity}\n"
            msg += f"Buyurtmachi ismi: {name}\n"
            msg += f"Buyurtmachi telefon raqami: {phone_number}\n"
            msg += f"Buyurtmachi manzili: {address}\n\n"

        await bot.delete_message(chat_id=callback_query.from_user.id, message_id=callback_query.message.message_id)
        
        await bot.send_message(chat_id, msg, reply_markup=initialKeyboard)

    await callback_query.answer()