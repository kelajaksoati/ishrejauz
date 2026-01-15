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
    add_vac_title = State(); add_vac_link = State()
    add_q_subj = State(); add_q_file = State() # Test qo'shish uchun
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

# --- 2. ONLAYN TEST (FOYDALANUVCHI) ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_start(message: types.Message):
    await message.answer("Qaysi fan bo'yicha test topshirmoqchisiz?", reply_markup=kb.subjects_menu())

# --- 3. TEST BOSHLASH VA FAYL QIDIRISH ---
@dp.message_handler(lambda m: m.text in db.get_subjects(), state="*")
async def handle_subject_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'cat' in data: # Agar foydalanuvchi fayl qidirayotgan bo'lsa
        # ... avvalgi fayl qidirish kodi ...
        pass 
    else: # Agar foydalanuvchi "Onlayn Test" dan kelgan bo'lsa
        quizzes = db.get_quizzes(message.text)
        if not quizzes:
            return await message.answer("⚠️ Bu fan bo'yicha testlar mavjud emas.")
        
        await state.update_data(quizzes=quizzes, current_idx=0, correct_count=0, subject=message.text)
        await send_next_quiz(message.from_user.id, state)

async def send_next_quiz(user_id, state: FSMContext):
    data = await state.get_data()
    idx, quizzes = data['current_idx'], data['quizzes']
    
    if idx >= len(quizzes):
        res = f"🏁 **Test yakunlandi!**\n\n📚 Fan: {data['subject']}\n✅ To'g'ri: {data['correct_count']}\n❌ Xato: {len(quizzes)-data['correct_count']}"
        await bot.send_message(user_id, res, reply_markup=kb.main_menu(is_admin_check(user_id)))
        await state.finish()
        return

    q_text, q_options, q_correct = quizzes[idx]
    options = q_options.split('|')
    
    text = f"❓ **{idx+1}-savol:**\n\n{q_text}\n\n"
    for i, opt in enumerate(options):
        text += f"{['A','B','C','D','E'][i]}) {opt}\n"
    
    await bot.send_message(user_id, text, reply_markup=kb.quiz_answer_menu(q_correct, len(options)))

@dp.callback_query_handler(lambda c: c.data.startswith('quiz_ans_'), state="*")
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'quizzes' not in data: return
    
    _, _, chosen_id, correct_id = callback.data.split('_')
    
    if chosen_id == correct_id:
        await callback.answer("✅ To'g'ri!", show_alert=False)
        await state.update_data(correct_count=data['correct_count'] + 1)
    else:
        await callback.answer("❌ Noto'g'ri!", show_alert=False)
    
    await state.update_data(current_idx=data['current_idx'] + 1)
    await callback.message.delete()
    await send_next_quiz(callback.from_user.id, state)

@dp.callback_query_handler(text="quiz_stop", state="*")
async def stop_quiz(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("⏹ Test to'xtatildi.")
    await state.finish()
    await cmd_start(callback.message, state)

# --- 4. ADMIN: TEST QO'SHISH (.TXT FAYL ORQALI) ---
@dp.message_handler(text="➕ Test qo'shish", state="*")
async def add_quiz_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qaysi fan uchun test yuklamoqchisiz?", reply_markup=kb.subjects_menu())
        await BotStates.add_q_subj.set()

@dp.message_handler(state=BotStates.add_q_subj)
async def add_quiz_subj(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(q_subj=message.text)
    await message.answer(f"📖 {message.text} fani uchun .txt faylni yuboring.\n\n*Format:* Savol?#Var1|Var2|Var3#0", parse_mode="Markdown")
    await BotStates.add_q_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_q_file)
async def add_quiz_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_path = f"downloads/{message.document.file_name}"
    await message.document.download(destination_file=file_path)
    
    # QuizEngine orqali faylni o'qish va bazaga yozish
    try:
        count = qe.process_quiz_file(file_path, data['q_subj'], db)
        os.remove(file_path)
        await message.answer(f"✅ Tayyor! {count} ta savol bazaga qo'shildi.", reply_markup=kb.admin_menu())
    except Exception as e:
        await message.answer(f"❌ Faylda xatolik: {e}")
    finally:
        await state.finish()

# --- OYLIK HISOBLASH, AI VA BOSHQA HANDLERLAR (AVVALGI KODDAGI KABI) ---
# ... (Yuqoridagi kodingizning qolgan qismlari shu yerda davom etadi)

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
