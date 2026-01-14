import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID
from database import Database
import keyboards as kb
from functions import calculate_salary_logic

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
db = Database('ebaza_pro.db')
dp = Dispatcher(bot, storage=MemoryStorage())

class States(StatesGroup):
    reklama = State()
    bhm_edit = State()
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    add_f_cat = State()
    add_f_subj = State()
    add_f_name = State()
    add_f_file = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer("👋 E-Baza botiga xush kelibsiz!", reply_markup=kb.main_menu())

# --- OYLIK HISOBLASH ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def oylik_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await States.calc_toifa.set()

@dp.message_handler(state=States.calc_toifa)
async def oylik_toifa(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text.lower())
    await message.answer("Haftalik dars soatingizni kiriting (Masalan: 18):")
    await States.calc_soat.set()

@dp.message_handler(state=States.calc_soat)
async def oylik_soat(message: types.Message, state: FSMContext):
    await state.update_data(soat=float(message.text))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no())
    await States.calc_sinf.set()

@dp.message_handler(state=States.calc_sinf)
async def oylik_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf_foiz = 100 if "Ha" in message.text else 0
    bhm = db.get_setting('bhm')
    stavka = db.get_setting(data['toifa'])
    
    natija = calculate_salary_logic(stavka, data['soat'], sinf_foiz, bhm)
    await message.answer(f"💰 Sizning oyligingiz: *{natija:,}* so'm\n_(Soliqlar ayirilgan)_", reply_markup=kb.main_menu())
    await state.finish()

# --- ADMIN PANEL ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin boshqaruvi:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📢 Reklama")
async def rek_start(message: types.Message):
    await message.answer("Xabarni yuboring:")
    await States.reklama.set()

@dp.message_handler(state=States.reklama, content_types=types.ContentType.ANY)
async def rek_send(message: types.Message, state: FSMContext):
    users = db.get_users()
    for u in users:
        try:
            await message.copy_to(u[0])
            await asyncio.sleep(0.05)
        except: pass
    await message.answer("✅ Yuborildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="🏠 Chiqish")
async def exit_admin(message: types.Message):
    await message.answer("Asosiy menu:", reply_markup=kb.main_menu())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
