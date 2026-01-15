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

# --- LOGGING VA SOZLAMALAR ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')
qe = QuizEngine()

# --- YORDAMCHI FUNKSIYALAR ---
def is_admin_check(user_id):
    return str(user_id) == str(ADMIN_ID)

def is_float(value):
    try:
        float(value.replace(',', '.'))
        return True
    except ValueError:
        return False

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    calc_toifa = State(); calc_soat = State(); calc_sinf = State()
    calc_daftar = State(); calc_sertifikat = State(); calc_staj = State(); calc_olis = State()
    ai_query = State(); reklama = State()
    waiting_for_feedback = State(); waiting_for_admin_reply = State()
    # Admin uchun yangi holatlar
    add_f_cat = State(); add_f_subj = State(); add_f_quarter = State()
    add_f_name = State(); add_f_file = State()
    add_vac_title = State(); add_vac_link = State()
    add_q_subj = State(); add_q_file = State()
    quiz_process = State()

# --- 1. START VA ASOSIY MENU ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    settings = db.get_settings()
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.full_name)
    text = f"👋 Salom, {message.from_user.first_name}!\n\n📅 **Joriy o'quv yili:** {settings.get('study_year', '2024-2025')}\n\nKerakli bo'limni tanlang:"
    await message.answer(text, reply_markup=kb.main_menu(is_admin_check(user_id)))

# --- 2. ASOSIY TUGMALAR HANDLERI ---
@dp.message_handler(lambda m: m.text in ["📁 Darsliklar", "🎨 Portfolio", "📄 Hujjat yaratish", "📢 Vakansiyalar"], state="*")
async def handle_categories(message: types.Message):
    text = message.text
    if text == "📢 Vakansiyalar":
        await message.answer("🔍 Oxirgi vakansiyalar e'lon qilinmoqda...")
        # Vakansiya chiqarish logikasi bu yerda
    else:
        await message.answer(f"✅ {text} bo'limi tanlandi.\nFaningizni tanlang:", reply_markup=kb.subjects_menu())

# --- 3. ALOQA BO'LIMI ---
@dp.message_handler(text="✍️ Savol yo'llash", state="*")
async def feedback_start(message: types.Message):
    await message.answer("Savolingizni yozing. Adminlarimiz javob berishadi.", reply_markup=kb.back_menu())
    await BotStates.waiting_for_feedback.set()

@dp.message_handler(state=BotStates.waiting_for_feedback)
async def feedback_sent(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await bot.send_message(ADMIN_ID, f"📩 Savol: {message.text}\nID: {message.from_user.id}", reply_markup=kb.feedback_reply_markup(message.from_user.id))
    await message.answer("✅ Savolingiz yuborildi.", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 4. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi", state="*")
async def ai_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Savolingizni yozing (Masalan: 'Insho yozishga yordam ber'):", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    res = await func.get_ai_answer(message.text)
    await wait_msg.delete()
    await message.answer(f"🤖 **AI Javobi:**\n\n{res}", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 5. ONLAYN TEST ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_start(message: types.Message):
    await message.answer("Fanini tanlang:", reply_markup=kb.subjects_menu())

# --- 6. ADMIN PANEL VA UNING TUGMALARI ---
@dp.message_handler(text="⚙️ Admin panel", state="*")
async def admin_panel(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=kb.admin_menu())

@dp.message_handler(lambda m: is_admin_check(m.from_user.id) and m.text in ["➕ Fayl qo'shish", "➕ Vakansiya qo'shish", "➕ Kategoriya/Fan/Chorak", "📊 Statistika", "⚙️ Narxlarni o'zgartirish", "📅 O'quv yilini o'zgartirish"], state="*")
async def admin_tools(message: types.Message):
    text = message.text
    if text == "📊 Statistika":
        count = len(db.get_all_users())
        await message.answer(f"👥 Bot a'zolari soni: {count} ta")
    elif text == "⚙️ Narxlarni o'zgartirish":
        await message.answer("Narxlarni sozlash:", reply_markup=kb.settings_menu())
    else:
        await message.answer(f"🛠 {text} funksiyasi tez orada to'liq ishga tushadi.")

# OYLI HISOBLASH KODI (O'ZGARISHSIZ QOLDI)
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish(); await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

# ... (Bu yerda salary_toifa va boshqa salary handlerlari joylashgan bo'lishi kerak)
# ... (User yuborgan avvalgi koddagi salary va quiz qismlarini ham shu yerga qo'shib qo'ying)

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
