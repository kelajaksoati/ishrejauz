import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID
from database import Database
import keyboards as kb
import functions as func
import generator as gen
from quiz_engine import QuizEngine

# Loglar va Bot sozlamalari
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')
quiz = QuizEngine()

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    add_f_cat = State()
    add_f_subj = State()
    add_f_name = State()
    add_f_file = State()
    reklama = State()
    ai_query = State()
    hujjat_ism = State()

def is_admin_check(user_id):
    return db.is_admin(user_id, ADMIN_ID)

# --- 1. ASOSIY KOMANDALAR ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    db.add_user(message.from_user.id)
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\n*Ish Reja Uz* botiga xush kelibsiz!", reply_markup=kb.main_menu())

# --- 2. 💰 OYLIK HISOBLASH ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def oylik_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def oylik_step2(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text.lower())
    await message.answer("Dars soatingizni tanlang yoki kiriting:", reply_markup=kb.soat_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def oylik_step3(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    if not message.text.isdigit(): return await message.answer("Raqam kiriting!")
    await state.update_data(soat=int(message.text))
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Ha", "Yo'q", "🏠 Bosh menu")
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=markup)
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def oylik_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    data = await state.get_data()
    sinf = 100 if message.text == "Ha" else 0
    res = func.calculate_salary_logic(db.get_setting(data['toifa']), data['soat'], sinf, db.get_setting('bhm'))
    await message.answer(f"✅ Hisoblandi: *{res:,}* so'm", reply_markup=kb.main_menu())
    await state.finish()

# --- 3. 🤖 AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi")
async def ai_ask(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🏠 Bosh menu")
    await message.answer("Mavzuni yoki savolingizni yozing:", reply_markup=markup)
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_ans(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    msg = await message.answer("🔍 AI tahlil qilmoqda...")
    res = await func.get_ai_help(message.text) 
    await msg.edit_text(res)
    await state.finish()

# --- 4. 📚 FAYLLAR BILAN ISHLASH ---
@dp.message_handler(text=["📚 Ish rejalar", "📁 Darsliklar", "📝 Testlar"])
async def file_cat(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"*{message.text}* bo'limi. Fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika", "Biologiya", "Kimyo"])
async def file_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'cat' not in data: return 
    
    files = db.get_files(data.get('cat'), message.text)
    if not files:
        await message.answer("😔 Kechirasiz, bu fan bo'yicha fayl topilmadi.", reply_markup=kb.main_menu())
    else:
        for n, f_id in files:
            await bot.send_document(message.from_user.id, f_id, caption=f"📄 {n}")
    await state.finish()

# --- 5. ⚙️ ADMIN PANEL ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruvi:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📊 Statistika")
async def admin_stats(message: types.Message):
    if is_admin_check(message.from_user.id):
        count = db.get_users_count()
        await message.answer(f"👥 Bot foydalanuvchilari soni: *{count}* ta")

@dp.message_handler(text="➕ Fayl qo'shish")
async def add_f(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Kategoriya?", reply_markup=kb.cat_menu())
        await BotStates.add_f_cat.set()

@dp.message_handler(state=BotStates.add_f_cat)
async def add_f2(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fan?", reply_markup=kb.subjects_menu())
    await BotStates.add_f_subj.set()

@dp.message_handler(state=BotStates.add_f_subj)
async def add_f3(message: types.Message, state: FSMContext):
    await state.update_data(subj=message.text)
    await message.answer("Nomini yozing:")
    await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_name)
async def add_f4(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Faylni yuboring:")
    await BotStates.add_f_file.set()

@dp.message_handler(state=BotStates.add_f_file, content_types=['document'])
async def add_f_final(message: types.Message, state: FSMContext):
    d = await state.get_data()
    db.add_file(d['name'], message.document.file_id, d['cat'], d['subj'])
    await message.answer("✅ Saqlandi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="📢 Xabar yuborish")
async def rek_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Xabarni (tekst, rasm yoki video) yuboring:", reply_markup=types.ReplyKeyboardRemove())
        await BotStates.reklama.set()

@dp.message_handler(state=BotStates.reklama, content_types=['any'])
async def rek_send(message: types.Message, state: FSMContext):
    users = db.get_users()
    count = 0
    for u in users:
        try:
            await message.copy_to(u[0])
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await message.answer(f"✅ Tugadi. {count} ta foydalanuvchiga yuborildi.", reply_markup=kb.admin_menu())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
