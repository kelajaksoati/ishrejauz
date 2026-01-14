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

# --- BARCHA FSM HOLATLARI ---
class BotStates(StatesGroup):
    # Oylik
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    # Admin: Fayl
    add_f_cat = State()
    add_f_subj = State()
    add_f_name = State()
    add_f_file = State()
    # Admin: Reklama va BHM
    reklama = State()
    edit_bhm = State()
    # Premium
    ai_query = State()
    test_process = State()
    hujjat_ism = State()

# --- 1. ASOSIY KOMANDALAR ---
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish() # Har safar start bosilganda holatlarni tozalash
    db.add_user(message.from_user.id)
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\n*Ultra Premium E-Baza* botiga xush kelibsiz!", reply_markup=kb.main_menu())

# --- 2. 💰 OYLIK HISOBLASH HANDLERLARI ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def oylik_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def oylik_step2(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text.lower())
    await message.answer("Dars soatingizni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def oylik_step3(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("Raqam kiriting!")
    await state.update_data(soat=int(message.text))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def oylik_res(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sinf = 100 if message.text == "Ha" else 0
    res = func.calculate_salary_logic(db.get_setting(data['toifa']), data['soat'], sinf, db.get_setting('bhm'))
    await message.answer(f"✅ Hisoblandi: *{res:,}* so'm", reply_markup=kb.main_menu())
    await state.finish()

# --- 3. 🤖 AI VA 📄 HUJJAT GENERATOR ---
@dp.message_handler(text="🤖 AI Yordamchi")
async def ai_ask(message: types.Message):
    await message.answer("Mavzuni yozing (masalan: 'Insho mavzulari'):")
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_ans(message: types.Message, state: FSMContext):
    msg = await message.answer("🔍 AI tahlil qilmoqda...")
    res = await func.get_ai_help(message.text)
    await msg.edit_text(res)
    await state.finish()

@dp.message_handler(text="📄 Hujjat yaratish")
async def doc_ask(message: types.Message):
    await message.answer("Hujjat uchun to'liq ismingizni yozing:")
    await BotStates.hujjat_ism.set()

@dp.message_handler(state=BotStates.hujjat_ism)
async def doc_gen(message: types.Message, state: FSMContext):
    pdf = gen.generate_certificate_pdf(message.text, "A'lo")
    await message.answer_document(types.InputFile(pdf, filename="hujjat.pdf"), caption="Tayyor! ✅")
    await state.finish()

# --- 4. 📚 FAYLLAR VA TESTLAR ---
@dp.message_handler(text=["📚 Ish rejalar", "📁 Darsliklar", "📝 Testlar"])
async def file_cat(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in ["Ona tili", "Matematika", "Ingliz tili", "Fizika", "Kimyo"])
async def file_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data.get('cat'), message.text)
    if not files: await message.answer("Fayl topilmadi.")
    for n, f_id in files:
        await bot.send_document(message.from_user.id, f_id, caption=n)
    await state.finish()

# --- 5. ⚙️ ADMIN PANEL BARCHA FUNKSIYALARI ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 Admin boshqaruvi:", reply_markup=kb.admin_menu())

@dp.message_handler(text="➕ Fayl qo'shish")
async def add_f(message: types.Message):
    if message.from_user.id == ADMIN_ID:
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

@dp.message_handler(text="📢 Reklama yuborish")
async def rek_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Xabarni yuboring:")
        await BotStates.reklama.set()

@dp.message_handler(state=BotStates.reklama, content_types=['any'])
async def rek_send(message: types.Message, state: FSMContext):
    users = db.get_users()
    for u in users:
        try:
            await message.copy_to(u[0])
            await asyncio.sleep(0.05)
        except: continue
    await message.answer("✅ Tugadi.", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="🏠 Chiqish")
async def go_home(message: types.Message, state: FSMContext):
    await state.finish()
    await cmd_start(message, state)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
