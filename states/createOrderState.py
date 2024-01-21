from aiogram.dispatcher.filters.state import StatesGroup, State

class Order(StatesGroup):
    full_name = State()
    phone_number = State()
    address = State()