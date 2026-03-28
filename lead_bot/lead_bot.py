import asyncio
import os 
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Survey(StatesGroup):
    name = State()
    date = State()   # Состояние для даты
    contact = State()

@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("👋 Hello! You've reached N&D Barbershop. What's your name?")
    await state.set_state(Survey.name)

@dp.message(Survey.name, F.text)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Survey.date)
    await message.answer(f"Nice to meet you, {message.text}! When would you like to visit us? (e.g., Tomorrow at 2 PM)")

@dp.message(Survey.date, F.text)
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text) 
    await state.set_state(Survey.contact)
    await message.answer("Got it! Please share your phone number so our administrator can confirm your appointment.")

@dp.message(Survey.contact, F.text)
async def process_contact(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    
    name = user_data.get('name')
    date = user_data.get('date') 
    contact = message.text
    
    await message.answer("Perfect! Your request has been sent to our administrator. We will contact you shortly to confirm.")
    
    report = (
        f"📅 **NEW APPOINTMENT**\n\n"
        f"👤 **Client:** {name}\n"
        f"⏰ **Desired Date:** {date}\n"
        f"📞 **Contact:** {contact}"
    )
    
    try:
        await bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending to admin: {e}")
    
    await state.clear()

async def main():
    print("Barbershop Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
