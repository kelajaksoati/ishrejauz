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
    add_f_cat = State(); add_f_subj = State(); add_f_quarter = State()
    add_f_name = State(); add_f_file = State()
    add_vac_title = State(); add_vac_link = State(); set_year = State()
    add_quarter = State(); del_quarter = State()
    changing_price = State(); new_category = State(); new_subject = State()
    add_q_subj = State(); add_q_file = State(); quiz_process = State()

# --- 1. START VA ASOSIY MENU ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    settings = db.get_settings()
    study_year = settings.get('study_year', "Belgilanmagan")
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.full_name)
    text = f"👋 Salom, {message.from_user.first_name}!\n\n📅 **Joriy o'quv yili:** {study_year}\n\nKerakli bo'limni tanlang:"
    await message.answer(text, reply_markup=kb.main_menu(is_admin_check(user_id)))

# --- 2. ONLAYN TEST (FOYDALANUVCHI) ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_start(message: types.Message):
    await message.answer("Qaysi fan bo'yicha test topshirmoqchisiz?", reply_markup=kb.subjects_menu())

# --- 3. FAYL QIDIRISH VA TEST BOSHLASH (MOSLASHUVCHAN HANDLER) ---
@dp.message_handler(lambda m: m.text in db.get_categories(), state="*")
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"📂 {message.text}:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects(), state="*")
async def handle_subject_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # FAYL QIDIRISH MANTIQI
    if 'cat' in data:
        cat = data['cat']
        if "Ish reja" in cat:
            await state.update_data(subj=message.text)
            await message.answer("Chorakni tanlang:", reply_markup=kb.quarter_menu())
        else:
            files = db.get_files(cat, message.text)
            await func.send_files(bot, message.from_user.id, files)
            await state.finish()
    # TEST BOSHLASH MANTIQI
    else:
        quizzes = db.get_quizzes(message.text)
        if not quizzes:
            return await message.answer("⚠️ Bu fan bo'yicha testlar mavjud emas.")
        await state.update_data(quizzes=quizzes, current_idx=0, correct_count=0)
        await send_next_quiz(message.from_user.id, state)

async def send_next_quiz(user_id, state: FSMContext):
    data = await state.get_data()
    idx = data['current_idx']
    quizzes = data['quizzes']
    if idx >= len(quizzes):
        res = f"🏁 **Test yakunlandi!**\n✅ To'g'ri: {data['correct_count']}\n❌ Xato: {len(quizzes)-data['correct_count']}"
        await bot.send_message(user_id, res, reply_markup=kb.main_menu(is_admin_check(user_id)))
        await state.finish()
        return
    q_text, q_options, q_correct = quizzes[idx]
    options = q_options.split('|')
    full_text = f"❓ **Savol {idx+1}:**\n\n{q_text}\n\n"
    for i, opt in enumerate(options): full_text += f"{['A','B','C','D'][i]}) {opt}\n"
    await bot.send_message(user_id, full_text, reply_markup=kb.quiz_answer_menu(q_correct, len(options)))

@dp.callback_query_handler(lambda c: c.data.startswith('quiz_ans_'), state="*")
async def check_quiz_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'quizzes' not in data: return
    _, _, chosen_id, correct_id = callback.data.split('_')
    if chosen_id == correct_id:
        await state.update_data(correct_count=data['correct_count'] + 1)
    await state.update_data(current_idx=data['current_idx'] + 1)
    await callback.message.delete()
    await send_next_quiz(callback.from_user.id, state)

# --- 4. OYLIK HISOBLASH (TO'LIQ) ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish(); await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingiz:", reply_markup=kb.back_menu()); await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_soat(message: types.Message, state: FSMContext):
    if not is_float(message.text): return await message.answer("Faqat raqam!")
    await state.update_data(soat=message.text.replace(',','.')); await message.answer("Sinf rahbarlik?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def salary_sinf(message: types.Message, state: FSMContext):
    await state.update_data(sinf_rahbar=("HA" in message.text.upper()))
    await message.answer("Daftar tekshirish?", reply_markup=kb.yes_no_menu()); await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_daftar)
async def salary_daftar(message: types.Message, state: FSMContext):
    await state.update_data(daftar_tekshirish=("HA" in message.text.upper()))
    await message.answer("Sertifikat ustamasi (%):"); await BotStates.calc_sertifikat.set()

@dp.message_handler(state=BotStates.calc_sertifikat)
async def salary_sert(message: types.Message, state: FSMContext):
    await state.update_data(sertifikat=int(message.text) if message.text.isdigit() else 0)
    await message.answer("Ish staji (yil):"); await BotStates.calc_staj.set()

@dp.message_handler(state=BotStates.calc_staj)
async def salary_staj(message: types.Message, state: FSMContext):
    await state.update_data(staj=int(message.text) if message.text.isdigit() else 0)
    await message.answer("Olis hudud?", reply_markup=kb.yes_no_menu()); await BotStates.calc_olis.set()

@dp.message_handler(state=BotStates.calc_olis)
async def salary_final(message: types.Message, state: FSMContext):
    await state.update_data(olis_hudud=("HA" in message.text.upper()))
    res = func.calculate_salary_advanced(db, await state.get_data())
    await message.answer(f"💰 Oylik: {res:,.0f} so'm".replace(',',' '), reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 5. ADMIN PANEL VA REKLAMA ---
@dp.message_handler(text="⚙️ Admin panel", state="*")
async def admin_panel(message: types.Message):
    if is_admin_check(message.from_user.id): await message.answer("🛠 Panel:", reply_markup=kb.admin_menu())

@dp.message_handler(text="📢 Xabar yuborish", state="*")
async def broadcast(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Xabarni yuboring:", reply_markup=kb.back_menu()); await BotStates.reklama.set()

@dp.message_handler(state=BotStates.reklama, content_types=types.ContentTypes.ANY)
async def send_reklama(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    users = db.get_items("users")
    for u in users:
        try: await bot.copy_message(u[0], message.chat.id, message.message_id); await asyncio.sleep(0.05)
        except: continue
    await message.answer("✅ Yakunlandi."); await state.finish()

# --- 6. ADMIN: FAYL VA TEST QO'SHISH ---
@dp.message_handler(text="➕ Fayl qo'shish", state="*")
async def add_f_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        cats = db.get_categories()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for c in cats: markup.insert(c)
        await message.answer("Kategoriya:", reply_markup=markup.add("🏠 Bosh menu"))
        await BotStates.add_f_cat.set()

@dp.message_handler(state=BotStates.add_f_cat)
async def add_f_c(message: types.Message, state: FSMContext):
    await state.update_data(f_cat=message.text)
    subs = db.get_subjects()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subs: markup.insert(s)
    await message.answer("Fan:", reply_markup=markup.add("🏠 Bosh menu")); await BotStates.add_f_subj.set()

@dp.message_handler(state=BotStates.add_f_subj)
async def add_f_s(message: types.Message, state: FSMContext):
    await state.update_data(f_subj=message.text)
    data = await state.get_data()
    if "Ish reja" in data['f_cat']:
        qs = db.get_quarters()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for q in qs: markup.insert(q)
        await message.answer("Chorak:", reply_markup=markup.add("🏠 Bosh menu")); await BotStates.add_f_quarter.set()
    else:
        await message.answer("Fayl nomi:"); await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_name)
async def add_f_n(message: types.Message, state: FSMContext):
    await state.update_data(f_name=message.text); await message.answer("Faylni yuboring:"); await BotStates.add_f_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_f_file)
async def add_f_final(message: types.Message, state: FSMContext):
    d = await state.get_data()
    db.add_file(d['f_name'], message.document.file_id, d['f_cat'], d['f_subj'], d.get('f_quarter'))
    await message.answer("✅ Saqlandi.", reply_markup=kb.admin_menu()); await state.finish()

# --- STARTUP ---
if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
