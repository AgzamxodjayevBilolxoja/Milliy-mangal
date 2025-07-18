from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp, db
from services.database.sql import check_user, get_branches, get_branch_by_name
from keyboards.default.markup import get_branches_markup, uz, ru, back_uz, back_ru, menu_markup
from states.states import UserBranch


@dp.message_handler(text="📍 Filiallarimiz")
@dp.message_handler(text="📍 Наши филиалы")
async def branches_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    if lang == 'uz':
        await message.answer('Filiallardan birini tanlang!', reply_markup=get_branches_markup(branches, uz))
    else:
        await message.answer('Выберите одну из филиалов!', reply_markup=get_branches_markup(branches, ru))
    await UserBranch.branch.set()

@dp.message_handler(lambda x: x.text in [branch[3] for branch in db.execute(get_branches, fetchall=True)], state=UserBranch.branch)
async def get_branch_handler(message: types.Message):
    branch = db.execute(get_branch_by_name, (message.text, ), fetchone=True)
    await message.delete()
    await message.answer_location(latitude=branch[1], longitude=branch[2])
    await message.answer(f"{branch[3]} ---------- {branch[4]}")

@dp.message_handler(lambda x: x.text in [back_uz, back_ru], state=UserBranch.branch)
async def back_main_hadnler(message: types.Message, state: FSMContext):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    if lang == 'uz':
        await message.answer('Menyu!', reply_markup=menu_markup(uz))
    else:
        await message.answer('Меню', reply_markup=menu_markup(ru))
    await state.finish()

@dp.message_handler(state=UserBranch.branch)
async def error_branch_handler(message: types.Message):
    user = db.execute(check_user, (message.from_user.id, ), fetchone=True)
    lang = user[2]
    await message.delete()
    branches = db.execute(get_branches, fetchall=True)
    if lang == 'uz':
        await message.answer('Filiallardan birini tanlang!', reply_markup=get_branches_markup(branches, uz))
    else:
        await message.answer('Выберите одну из филиалов!', reply_markup=get_branches_markup(branches, ru))