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
    # Oylik hisoblash
    calc_toifa = State(); calc_soat = State(); calc_sinf = State()
    calc_daftar = State(); calc_sertifikat = State(); calc_staj = State(); calc_olis = State()
    # AI va Reklama
    ai_query = State(); reklama = State()
    # Aloqa bo'limi
    waiting_for_feedback = State(); waiting_for_admin_reply = State()
    # Fayl va Test boshqaruvi
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

# --- 2. ALOQA BO'LIMI (FEEDBACK) ---
@dp.message_handler(text="✍️ Savol yo'llash", state="*")
async def feedback_start(message: types.Message):
    await message.answer("Savolingizni yoki taklifingizni yozing. Adminlarimiz tez orada javob berishadi.", reply_markup=kb.back_menu())
    await BotStates.waiting_for_feedback.set()

@dp.message_handler(state=BotStates.waiting_for_feedback)
async def feedback_sent(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    
    await bot.send_message(
        ADMIN_ID, 
        f"📩 **Yangi savol!**\n\n👤 Kimdan: {message.from_user.full_name}\n🆔 ID: {message.from_user.id}\n❓ Savol: {message.text}",
        reply_markup=kb.feedback_reply_markup(message.from_user.id)
    )
    db.add_feedback(message.from_user.id, message.text)
    await message.answer("✅ Savolingiz adminga yetkazildi. Javobni kuting.", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith('reply_'), state="*")
async def admin_reply_start(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[1]
    await state.update_data(reply_to_user=user_id)
    await callback.message.answer(f"🆔 {user_id} uchun javobingizni yozing:")
    await BotStates.waiting_for_admin_reply.set()
    await callback.answer()

@dp.message_handler(state=BotStates.waiting_for_admin_reply)
async def admin_reply_sent(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('reply_to_user')
    try:
        await bot.send_message(user_id, f"📩 **Admin javobi:**\n\n{message.text}")
        await message.answer("✅ Javob yuborildi.")
    except:
        await message.answer("❌ Foydalanuvchi botni bloklagan.")
    await state.finish()

# --- 3. ONLAYN TEST TIZIMI ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_start(message: types.Message):
    await message.answer("Qaysi fan bo'yicha test topshirmoqchisiz?", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects(), state="*")
async def handle_subject_selection(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if 'f_cat' in data: # Agar admin/user fayl qidirishda bo'lsa
        # Fayl qidirish mantiqi bu yerda (kerak bo'lsa qo'shish mumkin)
        pass 
    else: # Test boshlash
        quizzes = db.get_quizzes(message.text)
        if not quizzes: return await message.answer("⚠️ Testlar mavjud emas.")
        await state.update_data(quizzes=quizzes, current_idx=0, correct_count=0, subject=message.text)
        await send_next_quiz(message.from_user.id, state)

async def send_next_quiz(user_id, state: FSMContext):
    data = await state.get_data()
    idx, quizzes = data['current_idx'], data['quizzes']
    if idx >= len(quizzes):
        res = f"🏁 **Test yakunlandi!**\n✅ To'g'ri: {data['correct_count']}\n❌ Xato: {len(quizzes)-data['correct_count']}"
        await bot.send_message(user_id, res, reply_markup=kb.main_menu(is_admin_check(user_id)))
        await state.finish(); return
    q_text, q_options, q_correct = quizzes[idx]
    options = q_options.split('|')
    full_text = f"❓ **{idx+1}-savol:**\n\n{q_text}\n\n"
    for i, opt in enumerate(options): full_text += f"{['A','B','C','D','E'][i]}) {opt}\n"
    await bot.send_message(user_id, full_text, reply_markup=kb.quiz_answer_menu(q_correct, len(options)))

@dp.callback_query_handler(lambda c: c.data.startswith('quiz_ans_'), state="*")
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if 'quizzes' not in data: return
    _, _, chosen_id, correct_id = callback.data.split('_')
    if chosen_id == correct_id: await state.update_data(correct_count=data['correct_count'] + 1)
    await state.update_data(current_idx=data['current_idx'] + 1)
    await callback.message.delete()
    await send_next_quiz(callback.from_user.id, state)

# --- 4. OYLIK HISOBLASH VA PDF ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish(); await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text); await message.answer("Dars soatingiz:", reply_markup=kb.back_menu())
    await BotStates.calc_soat.set()

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
    await message.answer("Sertifikat ustamasi (%):", reply_markup=kb.back_menu()); await BotStates.calc_sertifikat.set()

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
    data = await state.get_data()
    wait_msg = await message.answer("⌛️ *Hisobot PDF shaklida tayyorlanmoqda...*")
    try:
        res = func.calculate_salary_advanced(db, data)
        pdf_path = func.generate_salary_pdf(data, res, message.from_user.first_name)
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                await message.answer_document(pdf_file, caption=f"💰 Oylik: *{res:,.0f} so'm*".replace(',',' '), reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
            os.remove(pdf_path)
        else:
            await message.answer(f"💰 Oylik: {res:,.0f} so'm")
    except Exception as e:
        logging.error(f"Salary PDF Error: {e}")
        await message.answer("❌ Xatolik yuz berdi.")
    await wait_msg.delete(); await state.finish()

# --- 5. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi", state="*")
async def ai_start(message: types.Message, state: FSMContext):
    await state.finish(); await message.answer("Savolingizni yozing:", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    res = await func.get_ai_answer(message.text)
    await wait_msg.delete()
    await message.answer(f"🤖 **AI Javobi:**\n\n{res}", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 6. ADMIN: TEST QO'SHISH ---
@dp.message_handler(text="➕ Test qo'shish", state="*")
async def add_quiz_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qaysi fan uchun?", reply_markup=kb.subjects_menu()); await BotStates.add_q_subj.set()

@dp.message_handler(state=BotStates.add_q_subj)
async def add_quiz_subj(message: types.Message, state: FSMContext):
    await state.update_data(q_subj=message.text); await message.answer("TXT faylni yuboring:"); await BotStates.add_q_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_q_file)
async def add_quiz_file(message: types.Message, state: FSMContext):
    data = await state.get_data(); file_path = f"downloads/{message.document.file_name}"
    await message.document.download(destination_file=file_path)
    try:
        count = qe.process_quiz_file(file_path, data['q_subj'], db); os.remove(file_path)
        await message.answer(f"✅ {count} ta savol qo'shildi.", reply_markup=kb.admin_menu())
    except Exception as e: await message.answer(f"❌ Xato: {e}")
    finally: await state.finish()

# --- 7. BOSHQA ADMIN FUNKSIYALARI ---
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
    users = db.get_all_users()
    for u in users:
        try: await bot.copy_message(u[0], message.chat.id, message.message_id); await asyncio.sleep(0.05)
        except: continue
    await message.answer("✅ Yakunlandi."); await state.finish()

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
