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

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    # Oylik hisoblash holatlari
    calc_toifa = State(); calc_soat = State(); calc_sinf = State()
    calc_daftar = State(); calc_sertifikat = State(); calc_staj = State(); calc_olis = State()
    
    ai_query = State(); reklama = State()
    waiting_for_feedback = State(); waiting_for_admin_reply = State()
    
    # Admin holatlari
    add_f_cat = State(); add_f_subj = State(); add_f_quarter = State()
    add_f_name = State(); add_f_file = State()
    add_vac_title = State(); add_vac_link = State()
    add_q_subj = State(); add_q_file = State()
    waiting_for_price = State()

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

# --- 2. FOYDALANUVCHI BO'LIMLARI ---
@dp.message_handler(lambda m: m.text in ["📁 Darsliklar", "🎨 Portfolio", "📄 Hujjat yaratish", "📢 Vakansiyalar"], state="*")
async def handle_categories(message: types.Message, state: FSMContext):
    text = message.text
    if text == "📢 Vakansiyalar":
        await message.answer("🔍 Vakansiyalar bo'limi yuklanmoqda...")
        # Bu yerga vakansiya funksiyasini ulashingiz mumkin
    else:
        await state.update_data(current_category=text)
        await message.answer(f"✅ {text} bo'limi.\nFanni tanlang:", reply_markup=kb.subjects_menu())

@dp.callback_query_handler(lambda c: c.data.startswith('subj_'), state="*")
async def process_subject_choice(callback: types.CallbackQuery, state: FSMContext):
    # Bazadan materiallarni qidirish qismi
    await callback.message.answer("⚠️ Tanlangan fan bo'yicha materiallar topilmadi yoki yuklash jarayonida.")
    await callback.answer()

# --- 3. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi", state="*")
async def ai_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Savolingizni yozing:", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    res = await func.get_ai_answer(message.text)
    await wait_msg.delete()
    await message.answer(f"🤖 **AI Javobi:**\n\n{res}", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 4. OYLIK HISOBLASH (TO'LIQ ZANJIR) ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text)
    await message.answer("Haftalik dars soatingizni kiriting (masalan: 20):")
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_soat(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Faqat raqam kiriting!")
    await state.update_data(soat=int(message.text))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def salary_sinf(message: types.Message, state: FSMContext):
    await state.update_data(sinf_rahbar=(message.text == "Ha"))
    await message.answer("Daftar tekshirish uchun ustama bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_daftar)
async def salary_daftar(message: types.Message, state: FSMContext):
    await state.update_data(daftar=(message.text == "Ha"))
    await message.answer("C1/Sertifikat uchun ustama bormi (20% yoki 50%)?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sertifikat.set()

@dp.message_handler(state=BotStates.calc_sertifikat)
async def salary_sert(message: types.Message, state: FSMContext):
    await state.update_data(sertifikat=(message.text == "Ha"))
    await message.answer("Olis hududda dars berasizmi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_olis.set()

@dp.message_handler(state=BotStates.calc_olis)
async def salary_final(message: types.Message, state: FSMContext):
    await state.update_data(olis_hudud=(message.text == "Ha"))
    data = await state.get_data()
    # Hisoblash funksiyasini chaqiramiz
    results = func.calculate_salary_final(data, db) 
    await message.answer(results, reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 5. ADMIN PANEL ---
@dp.message_handler(text="⚙️ Admin panel", state="*")
async def admin_panel(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=kb.admin_menu())

@dp.message_handler(lambda m: is_admin_check(m.from_user.id) and m.text in ["⚙️ Narxlarni o'zgartirish", "📊 Statistika"], state="*")
async def handle_admin_tools(message: types.Message, state: FSMContext):
    if message.text == "⚙️ Narxlarni o'zgartirish":
        await message.answer("O'zgartirmoqchi bo'lgan narx turini tanlang:", reply_markup=kb.settings_menu())
    elif message.text == "📊 Statistika":
        count = len(db.get_all_users())
        await message.answer(f"👥 Botdagi jami foydalanuvchilar: {count} ta")

@dp.callback_query_handler(lambda c: c.data.startswith('set_'), state="*")
async def process_setting_change(callback: types.CallbackQuery, state: FSMContext):
    setting_key = callback.data.replace('set_', '')
    names = {
        "bhm": "BHM", "daftar": "Daftar tekshirish", "kabinet": "Kabinet mudirligi",
        "oliy": "Oliy toifa", "birinchi": "1-toifa", "ikkinchi": "2-toifa", "mutaxassis": "Mutaxassis"
    }
    await state.update_data(changing_setting=setting_key)
    await callback.message.answer(f"🔢 {names.get(setting_key, setting_key)} uchun yangi qiymatni kiriting (raqamda):")
    await BotStates.waiting_for_price.set()
    await callback.answer()

@dp.message_handler(state=BotStates.waiting_for_price)
async def save_new_price(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    if not message.text.isdigit():
        return await message.answer("❌ Faqat raqam kiriting!")
    
    data = await state.get_data()
    setting_key = data.get('changing_setting')
    if setting_key:
        db.update_setting(setting_key, int(message.text))
        await message.answer(f"✅ Yangilandi: {setting_key} = {message.text} so'm", reply_markup=kb.admin_menu())
    await state.finish()

# --- 6. ONLAYN TEST ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_start(message: types.Message):
    await message.answer("Fanini tanlang:", reply_markup=kb.subjects_menu())

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
