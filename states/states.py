from aiogram.dispatcher.filters.state import StatesGroup, State

class Register(StatesGroup):
    lang = State()
    phone = State()
    name = State()

class Settings(StatesGroup):
    step_one = State()
    lang = State()
    phone = State()
    name = State()

class Rating(StatesGroup):
    step_one = State()
    comment = State()

class StaffRegister(StatesGroup):
    role = State()
    password = State()

class AddBranch(StatesGroup):
    location = State()
    name = State()
    opening_time = State()
    yes_or_no = State()