import logging
import asyncio
import json
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

# --- 2. ADMIN: TEST YUKLASH (Docx/PDF) ---
@dp.message_handler(text="➕ Test qo'shish")
async def add_test_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qaysi fan uchun test yuklamoqchisiz?", reply_markup=kb.subjects_menu())
        await BotStates.add_q_subj.set()

@dp.message_handler(state=BotStates.add_q_subj)
async def add_test_subj(message: types.Message, state: FSMContext):
    await state.update_data(q_subj=message.text)
    await message.answer(f"📂 *{message.text}* fani uchun .docx faylni yuboring.\n(To'g'ri javob oldiga '*' qo'ying)", reply_markup=kb.back_menu())
    await BotStates.add_q_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_q_file)
async def handle_quiz_doc(message: types.Message, state: FSMContext):
    if not message.document.file_name.endswith(('.docx', '.pdf')):
        return await message.answer("❌ Faqat .docx yoki .pdf yuboring!")

    if not os.path.exists('downloads'): os.makedirs('downloads')
    file_path = f"downloads/{message.document.file_name}"
    await message.document.download(destination_file=file_path)
    
    data = await state.get_data()
    try:
        if file_path.endswith('.docx'):
            questions = qe.parse_quiz_docx(file_path)
        else:
            questions = qe.parse_quiz_pdf(file_path)
            
        added = qe.save_to_db(questions, data['q_subj'])
        await message.answer(f"✅ {added} ta savol yuklandi!", reply_markup=kb.admin_menu())
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")
    finally:
        if os.path.exists(file_path): os.remove(file_path)
        await state.finish()

# --- 3. DINAMIK BO'LIMLAR ---
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

# --- 4. OYLIK HISOBLASH ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def salary_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingizni kiriting:", reply_markup=kb.soat_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        soat = float(message.text)
        res = func.calculate_salary_from_db(db, data['toifa'], soat)
        await message.answer(f"📊 Maoshingiz: *{res:,} so'm*", reply_markup=kb.main_menu())
    except:
        await message.answer("Raqam kiriting!")
    finally: await state.finish()

# --- 5. ADMIN: FAYL QO'SHISH ---
@dp.message_handler(text="➕ Fayl qo'shish")
async def add_f_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Kategoriya:", reply_markup=kb.cat_menu())
        await BotStates.add_f_cat.set()

@dp.message_handler(state=BotStates.add_f_cat)
async def add_f_c(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fan:", reply_markup=kb.subjects_menu())
    await BotStates.add_f_subj.set()

@dp.message_handler(state=BotStates.add_f_subj)
async def add_f_s(message: types.Message, state: FSMContext):
    await state.update_data(subj=message.text)
    data = await state.get_data()
    if "Ish reja" in data['cat']:
        await message.answer("Chorak:", reply_markup=kb.quarter_menu())
        await BotStates.add_f_quarter.set()
    else:
        await message.answer("Fayl nomi:")
        await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_quarter)
async def add_f_q(message: types.Message, state: FSMContext):
    await state.update_data(quarter=message.text)
    await message.answer("Fayl nomi:")
    await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_name)
async def add_f_n(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Hujjatni yuboring:")
    await BotStates.add_f_file.set()

@dp.message_handler(state=BotStates.add_f_file, content_types=['document'])
async def add_f_done(message: types.Message, state: FSMContext):
    d = await state.get_data()
    db.add_file(d['name'], message.document.file_id, d['cat'], d['subj'], d.get('quarter'))
    await message.answer("✅ Saqlandi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- 6. ADMIN: VAKANSIYA, NARX, O'CHIRISH ---
@dp.message_handler(text="➕ Vakansiya qo'shish")
async def add_vac(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Sarlavha:")
        await BotStates.add_vac_title.set()

@dp.message_handler(state=BotStates.add_vac_title)
async def add_vac_t(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Link/Aloqa:")
    await BotStates.add_vac_link.set()

@dp.message_handler(state=BotStates.add_vac_link)
async def add_vac_f(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_item("vacancies", "title", data['title'])
    await message.answer("✅ Qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="⚙️ Narxlarni o'zgartirish")
async def change_prices(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qiymatni tanlang:", reply_markup=kb.settings_menu())

@dp.callback_query_handler(lambda c: c.data.startswith('set_'))
async def set_p_start(call: types.CallbackQuery, state: FSMContext):
    key = call.data.replace('set_', '')
    await state.update_data(price_key=key)
    await call.message.answer(f"Yangit qiymat ({key}):")
    await BotStates.set_price_value.set()

@dp.message_handler(state=BotStates.set_price_value)
async def set_p_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        db.update_setting(data['price_key'], float(message.text))
        await message.answer("✅ Yangilandi!", reply_markup=kb.admin_menu())
        await state.finish()

@dp.message_handler(text="➖ O'chirish (Barcha)")
async def del_hub(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("O'chirish uchun nomni yozing:")
        await BotStates.universal_delete.set()

@dp.message_handler(state=BotStates.universal_delete)
async def del_res(message: types.Message, state: FSMContext):
    v = message.text
    db.delete_item("categories", "name", v)
    db.delete_item("subjects", "name", v)
    db.delete_item("files", "name", v)
    await message.answer(f"🗑 '{v}' o'chirildi.", reply_markup=kb.admin_menu())
    await state.finish()

# --- 7. AI VA STATISTIKA ---
@dp.message_handler(text="🤖 AI Yordamchi")
async def ai_start(message: types.Message):
    await message.answer("Savolingizni yo'llang:")
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    await message.answer("⌛️...")
    res = await func.get_ai_answer(message.text)
    await message.answer(res)
    await state.finish()

@dp.message_handler(text="📊 Statistika")
async def stats(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer(f"📈 Foydalanuvchilar: {db.get_users_count()}")

@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Boshqaruv:", reply_markup=kb.admin_menu())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
