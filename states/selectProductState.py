from aiogram.dispatcher.filters.state import StatesGroup, State

class ProductSelectState(StatesGroup):
    select_category = State()
    select_food = State()
    add_to_cart = State()