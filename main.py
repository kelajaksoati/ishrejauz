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
    set_price_value = State() # Narxlarni yangilash uchun
    
    # Fayl va Kategoriya
    add_f_cat = State()
    add_f_subj = State()
    add_f_quarter = State()
    add_f_name = State()
    add_f_file = State()
    
    # Admin Panel Qo'shish
    new_item_name = State() # Fan, Kategoriya yoki Chorak uchun universal
    universal_delete = State() # O'chirish uchun
    
    # Test va Admin boshqaruvi
    add_q_subj = State()
    add_q_text = State()
    add_q_options = State()
    add_q_correct = State()
    add_admin_id = State()
    rem_admin_id = State()

def is_admin_check(user_id):
    return db.is_admin(user_id, ADMIN_ID)

async def send_files(chat_id, files):
    if not files:
        await bot.send_message(chat_id, "❌ Kechirasiz, ushbu bo'limda hozircha fayllar mavjud emas.")
    else:
        for name, f_id in files:
            await bot.send_document(chat_id, f_id, caption=f"📄 {name}")

# --- 1. ASOSIY KOMANDALAR ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    db.add_user(message.from_user.id, message.from_user.full_name)
    await message.answer(f"👋 Salom, {message.from_user.first_name}!\nKerakli bo'limni tanlang:", reply_markup=kb.main_menu())

# --- 2. ISH REJA VA CHORAKLAR MANTIQI (DINAMIK) ---
@dp.message_handler(lambda m: m.text in db.get_categories())
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"📂 {message.text} bo'limi uchun fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects())
async def subject_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(subj=message.text)
    
    # Agar tanlangan kategoriya "Ish rejalar" bo'lsa chorakni so'raydi
    if "Ish reja" in data.get('cat', ''):
        await message.answer("Chorakni tanlang:", reply_markup=kb.quarter_menu())
    else:
        # Boshqa kategoriyalar (Darsliklar, Testlar) uchun choraksiz fayllarni chiqaradi
        files = db.get_files(data.get('cat'), message.text)
        await send_files(message.from_user.id, files)

@dp.message_handler(lambda m: m.text in db.get_quarters())
async def quarter_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data.get('cat'), data.get('subj'), message.text)
    await send_files(message.from_user.id, files)

# --- 3. OYLIK HISOBLASH MANTIQI ---
@dp.message_handler(text="💰 Oylik hisoblash")
async def salary_start(message: types.Message):
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingizni tanlang yoki yozing:", reply_markup=kb.soat_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        soat = float(message.text)
        res = func.calculate_salary_from_db(db, data['toifa'], soat) # functions.py dagi yangi mantiq
        await message.answer(f"📊 Sizning taxminiy maoshingiz: *{res:,} so'm*", reply_markup=kb.main_menu())
        await state.finish()
    except:
        await message.answer("Iltimos, soatni raqamda kiriting!")

# --- 4. ADMIN PANEL: QO'SHISH VA SOZLAMALAR ---
@dp.message_handler(text="⚙️ Admin panel")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruvi:", reply_markup=kb.admin_menu())

@dp.message_handler(text="➕ Kategoriya/Fan/Chorak")
async def add_item_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add("Kategoriya", "Fan", "Chorak", "🏠 Bosh menu")
        await message.answer("Nima qo'shmoqchisiz?", reply_markup=markup)
        await BotStates.new_item_name.set()

@dp.message_handler(state=BotStates.new_item_name)
async def add_item_res(message: types.Message, state: FSMContext):
    if message.text in ["Kategoriya", "Fan", "Chorak"]:
        await state.update_data(table_type=message.text)
        await message.answer(f"{message.text} nomini yozing:")
    else:
        data = await state.get_data()
        table_map = {"Kategoriya": "categories", "Fan": "subjects", "Chorak": "quarters"}
        db.add_item(table_map[data['table_type']], "name", message.text)
        await message.answer(f"✅ {data['table_type']} muvaffaqiyatli qo'shildi!", reply_markup=kb.admin_menu())
        await state.finish()

@dp.message_handler(text="⚙️ Narxlarni o'zgartirish")
async def change_prices(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Qaysi qiymatni o'zgartiramiz?", reply_markup=kb.settings_menu())

@dp.callback_query_handler(lambda c: c.data.startswith('set_'))
async def set_price_start(call: types.CallbackQuery, state: FSMContext):
    key = call.data.replace('set_', '')
    await state.update_data(price_key=key)
    await call.message.answer(f"➡️ {key.upper()} uchun yangi qi_ymatni kiriting (so'mda):")
    await BotStates.set_price_value.set()
    await call.answer()

@dp.message_handler(state=BotStates.set_price_value)
async def set_price_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text.isdigit():
        db.update_setting(data['price_key'], float(message.text))
        await message.answer(f"✅ {data['price_key'].upper()} yangilandi!", reply_markup=kb.admin_menu())
        await state.finish()
    else: await message.answer("Faqat raqam kiriting!")

# --- 5. UNIVERSAL O'CHIRISH ---
@dp.message_handler(text="➖ O'chirish (Barcha)")
async def delete_hub(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("O'chiriladigan element nomini yozing (Kategoriya, Fan, Chorak yoki Fayl nomi):")
        await BotStates.universal_delete.set()

@dp.message_handler(state=BotStates.universal_delete)
async def universal_del_res(message: types.Message, state: FSMContext):
    val = message.text
    db.delete_item("categories", "name", val)
    db.delete_item("subjects", "name", val)
    db.delete_item("quarters", "name", val)
    db.delete_item("files", "name", val)
    await message.answer(f"🗑 '{val}' bazadan o'chirildi.", reply_markup=kb.admin_menu())
    await state.finish()

# --- 6. FAYL QO'SHISH (CHORAK BILAN) ---
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
    if "Ish reja" in (await state.get_data())['cat']:
        await message.answer("Chorakni tanlang:", reply_markup=kb.quarter_menu())
        await BotStates.add_f_quarter.set()
    else:
        await state.update_data(quarter=None)
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
    await message.answer("Faylni (document) yuboring:")
    await BotStates.add_f_file.set()

@dp.message_handler(state=BotStates.add_f_file, content_types=['document'])
async def add_f_done(message: types.Message, state: FSMContext):
    d = await state.get_data()
    db.add_file(d['name'], message.document.file_id, d['cat'], d['subj'], d.get('quarter'))
    await message.answer("✅ Fayl muvaffaqiyatli saqlandi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- STARTUP ---
async def on_startup(_):
    from config import DEFAULT_CATEGORIES, DEFAULT_SUBJECTS
    if not db.get_categories():
        for c in DEFAULT_CATEGORIES: db.add_item("categories", "name", c)
    if not db.get_subjects():
        for s in DEFAULT_SUBJECTS: db.add_item("subjects", "name", s)
    logging.info("Bot ishga tushdi...")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
