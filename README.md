# Event Telegram Bot

**[English](#english) | [中文](#中文)**

---

## English

A Telegram bot for creating events and managing sign-ups. It is built with Python, aiogram 3 and SQLite. Users can view events and sign up. Administrators can add events, reschedule them and view the list of participants.

### Features

- Event list sorted by month, day and hour
- Event details with the date, time, participant count and venue
- Sign-up through a step-by-step dialog
- Duplicate sign-up check
- Admin commands for adding events, rescheduling them and viewing registrations
- Inline keyboards for selecting events, dates and hours
- Data stored in SQLite

### Requirements

- Python 3.10+
- aiogram 3.x
- python-dotenv
- SQLite (built into Python)

### Installation and launch

1. Open the project directory.
2. Install the dependencies.

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Create a Telegram bot and copy its token from [@BotFather](https://t.me/BotFather).
4. Copy `.env.example` to `.env`. Enter your bot token and choose a numeric admin password.

   ```env
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_PASSWORD=your_numeric_password
   ```

5. Run the bot from the project directory.

   ```bash
   python event_bot.py
   ```

### First launch

SQLite creates `event.db` in the working directory when the bot starts. Send `/start` first to create the tables and open the menu. To add the first event, use `/admin`, enter the password from `.env` and then send `/add`.

### Commands

| Command | Description | Access |
|---|---|---|
| `/start` | Create the database tables and show the menu | Everyone |
| `/events` | Show all events | Everyone |
| `/sign_up` | Choose an event and sign up with your name | Everyone |
| `/admin` | Enter the admin password and open the admin menu | Everyone |
| `/add` | Add an event with a title, date, hour, participant count and venue | Admin |
| `/edit` | Change an event's date and hour | Admin |
| `/regs` | View the names and total number of people signed up for an event | Admin |

### How it works

- **Adding an event.** Enter its title, choose the hour, month and day using the buttons, then enter the participant count and venue.
- **Signing up.** Choose an event and enter your name. The bot checks whether you have already signed up using your Telegram user ID and the event title.
- **Rescheduling.** Choose an event and select a new hour, month and day.
- **Viewing registrations.** Choose an event in `/regs` to see its participant list.

The bot uses aiogram FSM state groups for these dialogs.

| State group | Steps | Command |
|---|---|---|
| `Password` | Password | `/admin` |
| `AddEvent` | Title → hour → month → day → participant count → venue | `/add` |
| `Sign_up` | Event → participant name | `/sign_up` |
| `Edit` | Event → new hour → new month → new day | `/edit` |
| `Regs` | Event | `/regs` |

### Project structure

- `event_bot.py` contains the commands and FSM dialogs.
- `utils.py` creates database tables and keyboards and checks admin access.

### Database

| Table | Columns | Purpose |
|---|---|---|
| `events` | `id`, `name`, `month`, `day`, `time`, `cpeople`, `place` | Event details |
| `admin` | `id`, `user_id` | Telegram user IDs with admin access |
| `register` | `id`, `user_id`, `username`, `eventname` | Names and event sign-ups |

Registrations are stored by event title. Use distinct titles to keep the participant lists separate. The bot displays the participant count entered by the administrator. The bot interface is in Russian.

---

## 中文

这是一个用于创建活动和管理报名的 Telegram 机器人，使用 Python、aiogram 3 和 SQLite 编写。用户可以查看活动并报名，管理员可以添加活动、调整活动时间和查看报名名单。

### 功能

- 按月份、日期和小时排序的活动列表
- 显示活动的日期、时间、人数和地点
- 通过分步骤对话报名
- 检查重复报名
- 管理员可以添加活动、调整时间和查看报名名单
- 使用内联按钮选择活动、日期和小时
- 使用 SQLite 保存数据

### 环境要求

- Python 3.10+
- aiogram 3.x
- python-dotenv
- SQLite（Python 内置）

### 安装与运行

1. 打开项目目录。
2. 安装依赖。

   ```bash
   python -m pip install -r requirements.txt
   ```

3. 创建 Telegram 机器人，并通过 [@BotFather](https://t.me/BotFather) 获取令牌。
4. 将 `.env.example` 复制为 `.env`，填入机器人令牌，并设置数字管理员密码。

   ```env
   BOT_TOKEN=your_telegram_bot_token
   ADMIN_PASSWORD=your_numeric_password
   ```

5. 在项目目录中运行机器人。

   ```bash
   python event_bot.py
   ```

### 首次启动

启动机器人后，SQLite 会在当前工作目录创建 `event.db`。先发送 `/start` 创建数据表并打开菜单。添加第一个活动时，先发送 `/admin` 并输入`.env` 中设置的密码，再发送 `/add`。

### 命令

| 命令 | 说明 | 权限 |
|---|---|---|
| `/start` | 创建数据表并显示菜单 | 所有人 |
| `/events` | 查看所有活动 | 所有人 |
| `/sign_up` | 选择活动并输入姓名报名 | 所有人 |
| `/admin` | 输入管理员密码并打开管理菜单 | 所有人 |
| `/add` | 添加活动，填写名称、日期、小时、人数和地点 | 管理员 |
| `/edit` | 修改活动日期和小时 | 管理员 |
| `/regs` | 查看某个活动的报名名单和总人数 | 管理员 |

### 工作原理

- **添加活动。** 输入活动名称，用按钮选择小时、月份和日期，然后填写人数和地点。
- **报名。** 选择活动并输入姓名。机器人根据 Telegram 用户 ID 和活动名称检查是否已经报名。
- **调整时间。** 选择活动，再选择新的小时、月份和日期。
- **查看报名。** 发送 `/regs` 并选择活动，即可查看报名名单。

机器人使用 aiogram FSM 状态组处理这些对话。

| 状态组 | 步骤 | 命令 |
|---|---|---|
| `Password` | 密码 | `/admin` |
| `AddEvent` | 名称 → 小时 → 月份 → 日期 → 人数 → 地点 | `/add` |
| `Sign_up` | 活动 → 报名者姓名 | `/sign_up` |
| `Edit` | 活动 → 新小时 → 新月份 → 新日期 | `/edit` |
| `Regs` | 活动 | `/regs` |

### 项目结构

- `event_bot.py` 包含命令和 FSM 对话。
- `utils.py` 负责创建数据表、生成键盘和检查管理员权限。

### 数据库

| 表 | 字段 | 用途 |
|---|---|---|
| `events` | `id`、`name`、`month`、`day`、`time`、`cpeople`、`place` | 活动信息 |
| `admin` | `id`、`user_id` | 具备管理员权限的 Telegram 用户 ID |
| `register` | `id`、`user_id`、`username`、`eventname` | 报名者姓名和报名记录 |

报名记录按活动名称保存。为每个活动使用不同的名称，即可区分报名名单。活动列表会显示管理员填写的人数。机器人的界面语言为俄语。
