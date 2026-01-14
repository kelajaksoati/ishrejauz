import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import BOT_TOKEN, ADMIN_ID
from database import Database
import keyboards as kb
from functions import calculate_teacher_salary

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
db = Database('ebaza.db')
dp = Dispatcher(bot, storage=MemoryStorage())

class States(StatesGroup):
    reklama = State()
    bhm_edit = State()
    calc_toifa = State()
    calc_soat = State()
    # Fayl qo'shish
    f_cat = State()
    f_subj = State()
    f_name = State()
    f_file = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer("👋 E-Baza botiga xush kelibsiz!", reply_markup=kb.main_menu())

# --- OYLIK ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def oylik_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await States.calc_toifa.set()

@dp.message_handler(state=States.calc_toifa)
async def oylik_toifa(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text.lower())
    await message.answer("Haftalik dars soatingizni raqamda kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await States.calc_soat.set()

@dp.message_handler(state=States.calc_soat)
async def oylik_res(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bhm = db.get_setting('bhm')
    stavka = db.get_setting(data['toifa'])
    res = calculate_teacher_salary(stavka, int(message.text), bhm, bhm)
    await message.answer(f"💰 Sizning taxminiy oyligingiz: {res:,} so'm", reply_markup=kb.main_menu())
    await state.finish()

# --- FAYLLAR ---
@dp.message_handler(text=["📚 Ish rejalar", "📝 Testlar", "📁 Darsliklar"])
async def show_files_step1(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"])
async def show_files_step2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data['cat'], message.text)
    if not files:
        await message.answer("❌ Fayllar topilmadi.")
    for name, f_id in files:
        await bot.send_document(message.from_user.id, f_id, caption=name)

# --- ADMIN PANEL ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_panel(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Admin rejimdasiz:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📢 Reklama", state="*")
async def rek_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Reklama xabarini yuboring:")
        await States.reklama.set()

@dp.message_handler(state=States.reklama, content_types=types.ContentType.ANY)
async def rek_send(message: types.Message, state: FSMContext):
    users = db.get_users()
    for u in users:
        try:
            await message.copy_to(u[0])
            await asyncio.sleep(0.05)
        except: pass
    await message.answer("✅ Reklama tarqatildi!", reply_markup=kb.admin_menu())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
