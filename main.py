import logging
import asyncio
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import BOT_TOKEN, ADMIN_ID
from database import Database
import keyboards as kb
import functions as func

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')

# --- FSM HOLATLARI ---
class BotStates(StatesGroup):
    # Oylik va AI
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    ai_query = State()
    reklama = State()
    
    # Fayl va Kategoriya
    add_f_cat = State()
    add_f_subj = State()
    add_f_name = State()
    add_f_file = State()
    new_cat_name = State()
    new_subj_name = State()
    
    # Test (Quiz)
    add_q_subj = State()
    add_q_text = State()
    add_q_options = State()
    add_q_correct = State()
    
    # Admin boshqaruvi va O'chirish
    add_admin_id = State()
    rem_admin_id = State()
    del_file_name = State()
    del_subj_name = State()

def is_admin_check(user_id):
    return user_id == int(ADMIN_ID) or db.is_admin(user_id, ADMIN_ID)

# --- 1. ASOSIY KOMANDALAR ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    db.add_user(message.from_user.id)
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\nKerakli bo'limni tanlang:", reply_markup=kb.main_menu())

# --- 2. ADMIN BOSHQARUVI (ADD/REM ADMIN) ---
@dp.message_handler(text="➕ Admin qo'shish")
async def add_admin_start(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer("Yangi adminning Telegram ID raqamini yozing:")
        await BotStates.add_admin_id.set()

@dp.message_handler(state=BotStates.add_admin_id)
async def add_admin_final(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        db.set_role(int(message.text), 'admin')
        await message.answer(f"✅ ID: {message.text} admin qilindi!", reply_markup=kb.admin_menu())
        await state.finish()
    else:
        await message.answer("Xato! Faqat raqam kiriting.")

@dp.message_handler(text="➖ Admin o'chirish")
async def rem_admin_start(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer("Adminlikdan olinadigan ID raqamini yozing:")
        await BotStates.rem_admin_id.set()

@dp.message_handler(state=BotStates.rem_admin_id)
async def rem_admin_final(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        db.set_role(int(message.text), 'user')
        await message.answer(f"❌ ID: {message.text} adminlikdan olindi.", reply_markup=kb.admin_menu())
        await state.finish()

# --- 3. TEST QO'SHISH ---
@dp.message_handler(text="➕ Test qo'shish")
async def add_quiz_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Fan tanlang:", reply_markup=kb.subjects_menu())
        await BotStates.add_q_subj.set()

@dp.message_handler(state=BotStates.add_q_subj)
async def add_quiz_subj(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(subj=message.text)
    await message.answer("Savolni kiriting:", reply_markup=types.ReplyKeyboardRemove())
    await BotStates.add_q_text.set()

@dp.message_handler(state=BotStates.add_q_text)
async def add_quiz_q(message: types.Message, state: FSMContext):
    await state.update_data(question=message.text)
    await message.answer("Variantlarni vergul bilan ajrating (A, B, C...):")
    await BotStates.add_q_options.set()

@dp.message_handler(state=BotStates.add_q_options)
async def add_quiz_opt(message: types.Message, state: FSMContext):
    options = [i.strip() for i in message.text.split(",")]
    if len(options) < 2: return await message.answer("Kamida 2 variant!")
    await state.update_data(options=options)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i, opt in enumerate(options): markup.add(f"{i} - {opt}")
    await message.answer("To'g'ri javob ID raqamini tanlang:", reply_markup=markup)
    await BotStates.add_q_correct.set()

@dp.message_handler(state=BotStates.add_q_correct)
async def add_quiz_final(message: types.Message, state: FSMContext):
    try:
        data = await state.get_data()
        c_id = int(message.text.split(" - ")[0])
        db.add_quiz(data['question'], json.dumps(data['options']), c_id, data['subj'])
        await message.answer("✅ Test saqlandi!", reply_markup=kb.admin_menu())
        await state.finish()
    except: await message.answer("Xato! ID ni to'g'ri tanlang.")

# --- 4. FAYL VA FANLARNI O'CHIRISH ---
@dp.message_handler(text="➖ Fayl o'chirish")
async def del_file_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("O'chiriladigan fayl nomini kiriting:")
        await BotStates.del_file_name.set()

@dp.message_handler(state=BotStates.del_file_name)
async def del_file_res(message: types.Message, state: FSMContext):
    if db.delete_file_by_name(message.text):
        await message.answer(f"🗑 '{message.text}' o'chirildi.", reply_markup=kb.admin_menu())
    else: await message.answer("Topilmadi.")
    await state.finish()

@dp.message_handler(text="➖ Fanni o'chirish")
async def del_subj_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())
        await BotStates.del_subj_name.set()

@dp.message_handler(state=BotStates.del_subj_name)
async def del_subj_res(message: types.Message, state: FSMContext):
    db.delete_subject(message.text)
    await message.answer(f"❌ '{message.text}' o'chirildi.", reply_markup=kb.admin_menu())
    await state.finish()

# --- 5. BAZANI TOZALASH ---
@dp.message_handler(text="🧹 Bazani tozalash")
async def clear_ask(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        btn = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("✅ HA", callback_data="db_clear_confirm"),
            types.InlineKeyboardButton("❌ YO'Q", callback_data="db_clear_cancel")
        )
        await message.answer("⚠️ Diqqat! Barcha ma'lumotlar o'chib ketadi. Rozimisiz?", reply_markup=btn)

@dp.callback_query_handler(text="db_clear_confirm")
async def db_clear_done(call: types.CallbackQuery):
    if call.from_user.id == int(ADMIN_ID):
        db.clear_all_data()
        await call.message.edit_text("✅ Baza tozalandi!")
    await call.answer()

@dp.callback_query_handler(text="db_clear_cancel")
async def db_cancel(call: types.CallbackQuery):
    await call.message.edit_text("🔄 Bekor qilindi.")
    await call.answer()

# --- 6. DINAMIK FAYLLARNI KO'RISH ---
@dp.message_handler(lambda m: m.text in db.get_categories())
async def file_cat(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects())
async def file_send(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data.get('cat'), message.text)
    if not files: await message.answer("Fayllar mavjud emas.")
    else:
        for n, f_id in files: await bot.send_document(message.from_user.id, f_id, caption=f"📄 {n}")

# --- 7. ADMIN PANEL VA BOSHQA HANDLERLAR ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruvi:", reply_markup=kb.admin_menu())

@dp.message_handler(text="➕ Kategoriya qo'shish")
async def add_cat(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Yangi kategoriya nomi:")
        await BotStates.new_cat_name.set()

@dp.message_handler(state=BotStates.new_cat_name)
async def add_cat_res(message: types.Message, state: FSMContext):
    db.add_category(message.text)
    await message.answer("✅ Qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="➕ Fan qo'shish")
async def add_subj(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Yangi fan nomi:")
        await BotStates.new_subj_name.set()

@dp.message_handler(state=BotStates.new_subj_name)
async def add_subj_res(message: types.Message, state: FSMContext):
    db.add_subject(message.text)
    await message.answer("✅ Qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="➕ Fayl qo'shish")
async def add_f_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Kategoriya tanlang:", reply_markup=kb.cat_menu())
        await BotStates.add_f_cat.set()

@dp.message_handler(state=BotStates.add_f_cat)
async def add_f_c(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fan tanlang:", reply_markup=kb.subjects_menu())
    await BotStates.add_f_subj.set()

@dp.message_handler(state=BotStates.add_f_subj)
async def add_f_s(message: types.Message, state: FSMContext):
    await state.update_data(subj=message.text)
    await message.answer("Fayl nomi:")
    await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_name)
async def add_f_n(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Faylni yuboring:")
    await BotStates.add_f_file.set()

@dp.message_handler(state=BotStates.add_f_file, content_types=['document'])
async def add_f_done(message: types.Message, state: FSMContext):
    d = await state.get_data()
    db.add_file(d['name'], message.document.file_id, d['cat'], d['subj'])
    await message.answer("✅ Fayl saqlandi!", reply_markup=kb.admin_menu())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
