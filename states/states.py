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
    
class AdminMain(StatesGroup):
    branch = State()
    menu = State()

class AddBranch(StatesGroup):
    location = State()
    name = State()
    opening_time = State()
    yes_or_no = State()

class UserBranch(StatesGroup):
    branch = State()

class UpdateBranch(StatesGroup):
    step_one = State()
    update = State()
    choose_command = State()
    update_field = State()

class AdminCategory(StatesGroup):
    step_one = State()

class AddCategory(StatesGroup):
    name_uz = State()
    name_ru = State()

class GetCategories(StatesGroup):
    step_one = State()
    delete = State()

class AdminProduct(StatesGroup):
    step_one = State()
    choose = State()
    command = State()
    update = State()
    name_uz = State()
    name_ru = State()
    description_uz = State()
    description_ru = State()
    price = State()
    image = State()
    
class AddProduct(StatesGroup):
    category = State()
    name_uz = State()
    name_ru = State()
    description_uz = State()
    description_ru = State()
    price = State()
    image = State()
    check = State()

class Staff(StatesGroup):
    step_one = State()
    # Chef
    chef_state = State()
    # Chef create
    chef_name = State()
    chef_branch = State()
    chef_password = State()
    # Chef Get-Update-Delete
    get_chef = State()
    command_chef = State()
    update = State()
    # Deliverman
    deliverman_state = State()
    # Deliverman Create
    deliverman_name = State()
    deliverman_branch = State()
    deliverman_password = State()
    # Deliverman Get-Update-Delete
    get_deliverman = State()
    command_delliverman = State()
    update_deliverman = State()

class UserMenu(StatesGroup):
    delivery_or_pick_up = State()
    category = State()
    food = State()
    plus_minus = State()
    cart = State()

class Cart(StatesGroup):
    step_one = State()
    delivery = State()
    set_delivery = State()
    location = State()
    buy = State()
    yes_or_no = State()
    card = State()
    
