from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Create the event, admin and registration tables.
# 创建活动、管理员和报名数据表。
def create_tables(data):
    data.execute("""create table if not exists events (
    id integer primary key autoincrement,
    name text,
    month text,
    day text,
    time text,
    cpeople int,
    place text
    )""")
    data.execute("""create table if not exists admin (
        id integer primary key autoincrement,
        user_id int unique
        )""")
    data.execute("""create table if not exists register (
          id integer primary key autoincrement,
          user_id int ,
          username str,
          eventname str,
      unique(user_id, eventname))""")


# Build the number buttons for each step.
# 为每个步骤生成数字按钮。
def create_keyboard(count: int, name: str):
    buttons = []
    for i in range(1, count + 1):
        button = InlineKeyboardButton(text=f"{i}", callback_data=f"{name}_{i}")
        buttons.append(button)
    pre_keyboard = []
    for i in range(4):
        pre_keyboard.append(buttons[i * (len(buttons) // 4): (i + 1) * (len(buttons) // 4)])
    if (len(buttons) // 4) * 4 != len(buttons):
        pre_keyboard.append(buttons[(len(buttons) // 4) * 4:len(buttons)])
    keyboard = InlineKeyboardMarkup(inline_keyboard=pre_keyboard)
    return keyboard


# Show a button for each event.
# 为每个活动显示一个按钮。
def create_events_keyboard(name: str, cur):
    cur.execute("select id, name from events")
    ev = cur.fetchall()
    if ev == []:
        return None
    pre_keyboard = []
    for i in ev:
        pre_keyboard.append([InlineKeyboardButton(text=i[1], callback_data=f"{name}_{i[0]}")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=pre_keyboard)
    return keyboard


# Check whether a user is an administrator.
# 检查用户是否为管理员。
def check_admin(user_id: int, cur):
    cur.execute("select user_id from admin where user_id = ?", (user_id,))
    usid = cur.fetchone()
    return usid is not None
