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

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Database('ebaza_ultimate.db')

# --- FSM Holatlari ---
class BotStates(StatesGroup):
    # Oylik hisoblash
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    # Fayl qo'shish (Admin)
    add_f_cat = State()
    add_f_subj = State()
    add_f_name = State()
    add_f_file = State()
    # Reklama
    reklama = State()
    # Hujjat yaratish
    doc_name = State()

# --- Handlerlar ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer(f"Xush kelibsiz, {message.from_user.first_name}! 👋\nPremium E-Baza botiga kiring.", reply_markup=kb.main_menu())

# --- 💰 OYLIK HISOBLASH ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def oylik_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def oylik_step2(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text.lower())
    await message.answer("Haftalik dars soatingizni kiriting (raqamda):", reply_markup=types.ReplyKeyboardRemove())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def oylik_step3(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Iltimos, faqat raqam kiriting!")
    await state.update_data(soat=int(message.text))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def oylik_res(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf_foiz = 100 if message.text == "Ha" else 0
    bhm = db.get_setting('bhm')
    stavka = db.get_setting(data['toifa'])
    
    natija = calculate_salary_logic(stavka, data['soat'], sinf_foiz, bhm)
    await message.answer(f"✅ *Hisob-kitob:* \n\n💰 Qo'lga tegadigan summa: {natija:,} so'm", reply_markup=kb.main_menu())
    await state.finish()

# --- 📁 FAYLLAR BO'LIMI ---
@dp.message_handler(text=["📚 Ish rejalar", "📁 Darsliklar"])
async def show_files(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya"])
async def send_file_res(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data.get('cat'), message.text)
    if not files:
        await message.answer("❌ Bu bo'limda fayllar topilmadi.")
    else:
        for name, f_id in files:
            await bot.send_document(message.from_user.id, f_id, caption=name)

# --- ⚙️ ADMIN PANEL ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_p(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📢 Reklama yuborish")
async def rek_p(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Reklama xabarini yuboring (Rasm, Video yoki Matn):")
        await BotStates.reklama.set()

@dp.message_handler(state=BotStates.reklama, content_types=types.ContentType.ANY)
async def send_rek_final(message: types.Message, state: FSMContext):
    users = db.get_users()
    count = 0
    for u in users:
        try:
            await message.copy_to(u[0])
            count += 1
            await asyncio.sleep(0.05)
        except: pass
    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi.", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="🏠 Chiqish")
async def exit_back(message: types.Message):
    await message.answer("Asosiy menu:", reply_markup=kb.main_menu())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
