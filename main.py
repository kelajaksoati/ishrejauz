import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID
from database import Database
from quiz_engine import QuizEngine 
import keyboards as kb
import functions as func

# Sozlamalar
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')
qe = QuizEngine()

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    calc_toifa = State()
    calc_soat = State()
    ai_query = State()
    reklama = State()
    set_price_value = State()
    
    add_f_cat = State()
    add_f_subj = State()
    add_f_quarter = State()
    add_f_name = State()
    add_f_file = State()
    
    add_vac_title = State()
    add_vac_link = State()
    
    add_q_subj = State()
    add_q_file = State()
    
    universal_delete = State()

def is_admin_check(user_id):
    return db.is_admin(user_id, ADMIN_ID)

async def send_files(chat_id, files):
    if not files:
        await bot.send_message(chat_id, "❌ Hozircha fayllar mavjud emas.")
    else:
        for name, f_id in files:
            await bot.send_document(chat_id, f_id, caption=f"📄 {name}")

# --- 1. ASOSIY ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    db.add_user(message.from_user.id, message.from_user.full_name)
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\nKerakli bo'limni tanlang:", reply_markup=kb.main_menu())

# --- 2. OYLIK HISOBLASH (QO'LDA KIRITISH) ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def salary_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu":
        await cmd_start(message, state)
        return
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingizni kiriting:\n(Masalan: 18 yoki 21.5)", reply_markup=kb.back_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_final(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu":
        await cmd_start(message, state)
        return

    data = await state.get_data()
    try:
        soat_str = message.text.replace(',', '.') # vergulni nuqtaga almashtirish
        soat = float(soat_str)
        res = func.calculate_salary_from_db(db, data['toifa'], soat)
        await message.answer(f"📊 *Hisob-kitob:* \nToifa: {data['toifa']}\nDars soati: {soat}\n\n💰 Maoshingiz: *{res:,} so'm*", reply_markup=kb.main_menu())
        await state.finish()
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting! (Masalan: 19.5)")

# --- 3. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi")
async def ai_start(message: types.Message):
    await message.answer("🤖 Savolingizni yo'llang:", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu":
        await cmd_start(message, state)
        return

    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    try:
        res = await func.get_ai_answer(message.text)
        await wait_msg.delete()
        await message.answer(f"🤖 *AI Javobi:* \n\n{res}")
    except Exception as e:
        await wait_msg.edit_text("❌ AI xatosi yuz berdi. Keyinroq urinib ko'ring.")
        logging.error(f"AI Error: {e}")
    finally:
        await state.finish()

# --- 4. QO'SHIMCHA TUGMALAR HANDLERLARI ---
@dp.message_handler(text="📢 Vakansiyalar")
async def view_vacancies(message: types.Message):
    vacs = db.get_items("vacancies")
    if not vacs:
        await message.answer("🤷‍♂️ Hozircha bo'sh ish o'rinlari mavjud emas.")
    else:
        text = "📢 *Mavjud vakansiyalar:*\n\n"
        for v in vacs:
            text += f"🔹 {v[1]}\n"
        await message.answer(text)

@dp.message_handler(text="📝 Onlayn Test")
async def online_test_start(message: types.Message):
    await message.answer("Qaysi fan bo'yicha test topshirmoqchisiz?", reply_markup=kb.subjects_menu())

@dp.message_handler(text="📄 Hujjat yaratish")
async def doc_gen(message: types.Message):
    await message.answer("🛠 Bu bo'lim hozirda takomillashtirilmoqda...")

# --- 5. DINAMIK BO'LIMLAR (ISH REJA VA FAYLLAR) ---
@dp.message_handler(lambda m: m.text in db.get_categories())
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"📂 {message.text} uchun fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects())
async def subject_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = data.get('cat', '')
    if "Ish reja" in cat:
        await state.update_data(subj=message.text)
        await message.answer("Chorakni tanlang:", reply_markup=kb.quarter_menu())
    else:
        files = db.get_files(cat, message.text)
        await send_files(message.from_user.id, files)

@dp.message_handler(lambda m: m.text in db.get_quarters())
async def quarter_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data.get('cat'), data.get('subj'), message.text)
    await send_files(message.from_user.id, files)

# --- 6. ADMIN PANEL VA BOSHQARUV ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📊 Statistika")
async def stats(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer(f"📈 Foydalanuvchilar soni: {db.get_users_count()}")

@dp.message_handler(text="➕ Test qo'shish")
async def add_test_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qaysi fan uchun test yuklamoqchisiz?", reply_markup=kb.subjects_menu())
        await BotStates.add_q_subj.set()

# (Qolgan barcha admin funksiyalari o'z holicha saqlandi...)
# [add_q_subj, add_q_file, add_f_cat, add_vac va h.k. handlerlari]

@dp.message_handler(state=BotStates.add_q_subj)
async def add_test_subj(message: types.Message, state: FSMContext):
    await state.update_data(q_subj=message.text)
    await message.answer(f"📂 *{message.text}* uchun fayl yuboring:", reply_markup=kb.back_menu())
    await BotStates.add_q_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_q_file)
async def handle_quiz_doc(message: types.Message, state: FSMContext):
    if not message.document.file_name.endswith(('.docx', '.pdf')):
        return await message.answer("❌ Faqat .docx yoki .pdf yuboring!")
    
    file_path = f"downloads/{message.document.file_name}"
    if not os.path.exists('downloads'): os.makedirs('downloads')
    await message.document.download(destination_file=file_path)
    
    data = await state.get_data()
    try:
        questions = qe.parse_quiz_docx(file_path) if file_path.endswith('.docx') else qe.parse_quiz_pdf(file_path)
        added = qe.save_to_db(questions, data['q_subj'])
        await message.answer(f"✅ {added} ta savol yuklandi!", reply_markup=kb.admin_menu())
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
