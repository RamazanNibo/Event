import asyncio
import os
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
import sqlite3
from utils import create_tables, create_keyboard, create_events_keyboard, check_admin

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
data = sqlite3.connect("event.db")
cur = data.cursor()
menu = (
    "/events - список мероприятий\n"
    "/sign_up - записаться на мероприятие\n"
    "/admin - войти как администратор"
)
amenu = (
    "/events - список мероприятий\n"
    "/sign_up - записаться на мероприятие\n"
    "/add - добавить мероприятие\n"
    "/edit - изменить мероприятие\n"
    "/regs - посмотреть регистрации"
)


def get_menu(user_id: int):
    if check_admin(user_id, cur):
        return amenu
    return menu


async def main():
    print("Бот работает!")
    await dp.start_polling(bot)


class AddEvent(StatesGroup):
    name = State()
    day = State()
    month = State()
    time = State()
    cpeople = State()
    place = State()
class Password(StatesGroup):
    password = State()
class Sign_up(StatesGroup):
    username = State()
    placename = State()
class Edit(StatesGroup):
    name = State()
    time = State()
    month = State()
    day = State()
class Regs(StatesGroup):
    name = State()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    print("старт")
    create_tables(data)
    await message.answer(f"Привет! Я бот для мероприятий\n{get_menu(message.from_user.id)}")


@dp.message(Command("events"))
async def cmd_events(message: Message):
    cur.execute("select name, month, day, time, cpeople, place from events order by cast(month as int), cast(day as int), cast(time as int)")
    ev = cur.fetchall()
    if ev == []:
        await message.answer("Мероприятий пока нет")
        return
    mes = "Все мероприятия:\n\n"
    for i in ev:
        mes += (
            f"{i[0]}\n"
            f"Дата: {str(i[2]).zfill(2)}.{str(i[1]).zfill(2)}, {str(i[3]).zfill(2)}:00\n"
            f"Количество людей: {i[4]}\n"
            f"Место: {i[5]}\n\n"
        )
    await message.answer(mes)


@dp.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    if not check_admin(message.from_user.id, cur):
        await message.answer("Эта команда только для администраторов")
        return
    await message.answer("Введите название мероприятия")
    await state.set_state(AddEvent.name)


@dp.message(AddEvent.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите время проведения мероприятия", reply_markup=create_keyboard(24, "hour"))
    await state.set_state(AddEvent.day)


@dp.callback_query(F.data.startswith("hour_"))
async def cb_register(callback: CallbackQuery, state: FSMContext):
    hour = int(callback.data.split("_")[1])
    await state.update_data(time=hour)
    await state.set_state(AddEvent.month)
    await callback.message.answer("Введите месяц проведения", reply_markup=create_keyboard(12, "month"))
    await callback.answer()


@dp.callback_query(F.data.startswith("month_"))
async def cb_register(callback: CallbackQuery, state: FSMContext):
    month = int(callback.data.split("_")[1])
    await state.update_data(month=month)
    await state.set_state(AddEvent.day)
    if month in [1, 3, 5, 7, 8, 10, 12]:
        keyboard = create_keyboard(31, "day")
    elif month == 2:
        keyboard = create_keyboard(28, "day")
    else:
        keyboard = create_keyboard(30, "day")
    await callback.message.answer("Введите день проведения", reply_markup=keyboard)
    await callback.answer()


@dp.callback_query(F.data.startswith("day_"))
async def cb_register(callback: CallbackQuery, state: FSMContext):
    day = int(callback.data.split("_")[1])
    await state.update_data(day=day)
    await state.set_state(AddEvent.cpeople)
    await callback.message.answer("Введите количество людей")
    await callback.answer()


@dp.message(AddEvent.cpeople)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(cpeople=message.text)
    await state.set_state(AddEvent.place)
    await message.answer("Введите место проведения мероприятия")


@dp.message(AddEvent.place)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(place=message.text)
    event = await state.get_data()
    print(event)
    data.execute("""insert into events (name,month,day,time,cpeople,place) values (?,?,?,?,?,?) """,
                 [event["name"], event["month"], event["day"], event["time"], event["cpeople"], event["place"]])
    data.commit()
    await state.clear()
    await message.answer("Мероприятие добавлено")


@dp.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    if check_admin(message.from_user.id, cur):
        await message.answer(f"Вы уже администратор\n{amenu}")
        return
    await message.answer("Введите пароль")
    await state.set_state(Password.password)


@dp.message(Password.password)
async def check_password(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        us_password = int(message.text)
    except (ValueError, TypeError):
        await message.answer("Неверный пароль")
        return
    if us_password == int(os.environ["ADMIN_PASSWORD"]):
        cur.execute(f"""select user_id from admin where user_id = ? """, [user_id,])
        usid = cur.fetchone()
        if usid is None:
            data.execute("insert into admin (user_id) values (?)", (user_id,))
            data.commit()
            await message.answer(f"Вы теперь администратор\n{amenu}")
        else:
            await message.answer(f"Вы уже администратор\n{amenu}")
        await state.clear()
    else:
        await message.answer("Неверный пароль")


@dp.message(Command("sign_up"))
async def cmd_sign_up(message: Message, state: FSMContext):
    keyboard = create_events_keyboard("signevent", cur)
    if keyboard is None:
        await message.answer("Мероприятий пока нет")
        return
    await message.answer("Выберите мероприятие", reply_markup=keyboard)
    await state.set_state(Sign_up.placename)


@dp.callback_query(Sign_up.placename, F.data.startswith("signevent_"))
async def Sign_up_placename(callback: CallbackQuery, state: FSMContext):
    evid = int(callback.data.split("_")[1])
    cur.execute("select name from events where id = ?", (evid,))
    x = cur.fetchone()
    if x is None:
        await callback.message.answer("Мероприятие не найдено")
        await state.clear()
        await callback.answer()
        return
    await state.update_data(name=x[0])
    await state.set_state(Sign_up.username)
    await callback.message.answer("Введите свое имя")
    await callback.answer()


@dp.message(Sign_up.username)
async def cmd_sign_up(message: Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(username=message.text)
    register = await state.get_data()
    cur.execute("select eventname from register where user_id = ? and eventname = ?", (user_id, register["name"]))
    x = cur.fetchone()
    print(x)
    if x is None:
        cur.execute("""insert into register(user_id, username, eventname)values(?, ?, ?) """, [user_id, register["username"], register["name"]])
        data.commit()
        await message.answer("Вы зарегистрированы на мероприятие")
    else:
        await message.answer("Вы уже зарегистрированы на это мероприятие")
    await state.clear()


@dp.message(Command("edit"))
async def cmd_edit(message: Message, state: FSMContext):
    if not check_admin(message.from_user.id, cur):
        await message.answer("Эта команда только для администраторов")
        return
    keyboard = create_events_keyboard("editevent", cur)
    if keyboard is None:
        await message.answer("Мероприятий пока нет")
        return
    await message.answer("Выберите мероприятие", reply_markup=keyboard)
    await state.set_state(Edit.name)


@dp.callback_query(Edit.name, F.data.startswith("editevent_"))
async def Edit_name(callback: CallbackQuery, state: FSMContext):
    evid = int(callback.data.split("_")[1])
    cur.execute("select id from events where id = ?", (evid,))
    x = cur.fetchone()
    if x is None:
        await callback.message.answer("Мероприятие не найдено")
        await state.clear()
        await callback.answer()
        return
    await state.update_data(event_id=evid)
    await state.set_state(Edit.time)
    await callback.message.answer("Выберите новое время проведения", reply_markup=create_keyboard(24, "edit_hour"))
    await callback.answer()


@dp.callback_query(F.data.startswith("edit_hour_"))
async def edit_hour(callback: CallbackQuery, state: FSMContext):
    hour = int(callback.data.split("_")[2])
    await state.update_data(time=hour)
    await callback.message.answer("Выберите новый месяц", reply_markup=create_keyboard(12, "edit_month"))
    await state.set_state(Edit.month)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_month_"))
async def edit_month(callback: CallbackQuery, state: FSMContext):
    month = int(callback.data.split("_")[2])
    await state.update_data(month=month)
    if month in [1, 3, 5, 7, 8, 10, 12]:
        keyboard = create_keyboard(31, "edit_day")
    elif month == 2:
        keyboard = create_keyboard(28, "edit_day")
    else:
        keyboard = create_keyboard(30, "edit_day")
    await callback.message.answer("Выберите новый день", reply_markup=keyboard)
    await state.set_state(Edit.day)
    await callback.answer()

@dp.callback_query(F.data.startswith("edit_day_"))
async def edit_day(callback: CallbackQuery, state: FSMContext):
    day = int(callback.data.split("_")[2])
    await state.update_data(day=day)
    event = await state.get_data()
    cur.execute(
        "update events set time = ?, month = ?, day = ? where id = ?",
        (event["time"], event["month"], event["day"], event["event_id"])
    )
    data.commit()
    await callback.message.answer("Мероприятие успешно изменено")
    await state.clear()
    await callback.answer()


@dp.message(Command("regs"))
async def cmd_regs(message: Message, state: FSMContext):
    if not check_admin(message.from_user.id, cur):
        await message.answer("Эта команда только для администраторов")
        return
    keyboard = create_events_keyboard("regevent", cur)
    if keyboard is None:
        await message.answer("Мероприятий пока нет")
        return
    await message.answer("Выберите мероприятие", reply_markup=keyboard)
    await state.set_state(Regs.name)


@dp.callback_query(Regs.name, F.data.startswith("regevent_"))
async def Regs_name(callback: CallbackQuery, state: FSMContext):
    evid = int(callback.data.split("_")[1])
    cur.execute("select name from events where id = ?", (evid,))
    x = cur.fetchone()
    if x is None:
        await callback.message.answer("Мероприятие не найдено")
        await state.clear()
        await callback.answer()
        return
    cur.execute("select username from register where eventname = ?", (x[0],))
    reg = cur.fetchall()
    if reg == []:
        await callback.message.answer(f"На мероприятие {x[0]} пока никто не записан")
        await callback.answer()
        return
    mes = f"Регистрации на мероприятие {x[0]} ({len(reg)}):\n\n"
    for n, i in enumerate(reg, 1):
        mes += f"{n}. {i[0]}\n"
    await callback.message.answer(mes)
    await callback.answer()

asyncio.run(main())