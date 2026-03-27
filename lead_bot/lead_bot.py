import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter

import os
from dotenv import load_dotenv
load_dotenv()

import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession # Добавь этот импорт!

# Настройка прокси для PythonAnywhere
proxy_url = "http://proxy.server:3128"
session = AiohttpSession(proxy=proxy_url)

# Инициализация бота с сессией через прокси
API_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=API_TOKEN, session=session)

# --- CONFIG ---
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID") # Чтобы бот присылал тебе контакты лидов

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Состояния опроса (FSM)
class Survey(StatesGroup):
    name = State()
    goal = State()
    contact = State()

# 1. СТАРТ
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Hi! I'm your AI assistant. Want to get a 2026 Market Report? Let's start with your name!")

# 2. ИМЯ -> ЦЕЛЬ (Ждем имя в состоянии None)
@dp.message(StateFilter(None), F.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Survey.goal)
    await message.answer(f"Nice to meet you, {message.text}! What is your main goal for 2026? (e.g., Passive Income, New Career)")

# 3. ЦЕЛЬ -> КОНТАКТ (Ждем цель в состоянии Survey.goal)
@dp.message(Survey.goal)
async def process_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(Survey.contact)
    await message.answer("Got it! Please share your Email or Phone so I can send you the PDF.")

# 4. ФИНАЛ (Ждем контакт в состоянии Survey.contact)
@dp.message(Survey.contact)
async def process_contact(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    # Теперь данные точно сохранятся
    name = user_data.get('name', 'User')
    goal = user_data.get('goal', 'Unknown')
    contact = message.text
    
    await message.answer("Perfect! Your report is being generated and will be sent shortly. Have a great day!")
    
    # Уведомление тебе
    report = f"🚀 NEW LEAD!\nName: {name}\nGoal: {goal}\nContact: {contact}"
    await bot.send_message(ADMIN_ID, report)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())