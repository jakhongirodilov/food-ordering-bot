from aiogram.dispatcher.filters.state import StatesGroup, State

class AddProduct(StatesGroup):
    name = State()
    category = State()
    price = State()