from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    user_phone_number = State()
    category = State()
    product_name = State()
    product_price = State()
    product_image = State()
    product_description = State()
