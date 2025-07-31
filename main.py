from multiprocessing import Process
from aiogram.utils.executor import start_polling
from loader import dp, dp2, bot, bot2, db
from config import ADMINS
from services.database.sql import create_table_user, create_table_rating, create_table_branhes, create_table_staff, create_staff, create_table_category, create_table_foods, create_table_cart, create_table_order, create_table_order_items, get_staff
import handlers


async def on_startup1(dp):
    try:
        for admin in ADMINS:
            await bot.send_message(admin, "✅ Bot 1 ishga tushdi!")
    except Exception as e:
        print(f"Bot 1 xabari yuborilmadi: {e}")


async def on_startup2(dp2):
    try:
        for admin in ADMINS:
            await bot2.send_message(admin, "✅ Bot 2 ishga tushdi!")
    except Exception as e:
        print(f"Bot 2 xabari yuborilmadi: {e}")


def run_bot1():
    start_polling(dp, skip_updates=True, on_startup=on_startup1)


def run_bot2():
    start_polling(dp2, skip_updates=True, on_startup=on_startup2)


def main():
    db.execute(create_table_user, commit=True)
    db.execute(create_table_rating, commit=True)
    db.execute(create_table_branhes, commit=True)
    db.execute(create_table_staff, commit=True)
    db.execute(create_table_category, commit=True)
    db.execute(create_table_foods, commit=True)
    db.execute(create_table_order, commit=True)
    db.execute(create_table_cart, commit=True)
    db.execute(create_table_order_items, commit=True)
    staff = db.execute(get_staff, ('Admin', ), fetchall=True)
    if not staff:
        db.execute(create_staff, ('Admin', 'A.S.Nazarov'), commit=True)
    
    p1 = Process(target=run_bot1)
    p2 = Process(target=run_bot2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()


if __name__ == "__main__":
    main()
