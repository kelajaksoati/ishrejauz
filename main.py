import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

from database import Database  # Oldingi database.py faylimiz
import keyboards as kb      # Tugmalar uchun alohida fayl

# --- KONFIGURATSIYA ---
API_TOKEN = "BOT_TOKENINGIZNI_YOZING"
ADMIN_ID = 12345678  # O'zingizning ID raqamingiz

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')

# --- FSM HOLATLARI ---
class AdminState(StatesGroup):
    reklama = State()
    bhm_edit = State()
    add_file_cat = State()
    add_file_subj = State()
    add_file_name = State()
    add_file_doc = State()

class CalcState(StatesGroup):
    toifa = State()
    soat = State()
    sinf = State()

# --- ASOSIY HANDLERLAR ---

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    db.add_user(message.from_user.id)
    text = "👋 *Assalomu alaykum! E-Baza botiga xush kelibsiz.*\n\nKerakli bo'limni tanlang 👇"
    await message.answer(text, reply_markup=kb.main_menu())

@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("🛠 *Admin panelga xush kelibsiz!*", reply_markup=kb.admin_menu())

# --- OYLIK HISOBLASH (MUKAMMAL FORMULA) ---

@dp.message_handler(text="💰 Oylik hisoblash")
async def calc_start(message: types.Message):
    await message.answer("Siz qaysi toifadasiz?", reply_markup=kb.toifa_menu())
    await CalcState.toifa.set()

@dp.message_handler(state=CalcState.toifa)
async def calc_get_toifa(message: types.Message, state: FSMContext):
    toifalar = ["Oliy", "Birinchi", "Ikkinchi", "Mutaxassis"]
    if message.text not in toifalar:
        return await message.answer("Iltimos, tugmalardan foydalaning!")
    
    await state.update_data(toifa=message.text.lower())
    await message.answer("Haftalik dars soatingizni kiriting (Masalan: 22):", reply_markup=types.ReplyKeyboardRemove())
    await CalcState.soat.set()

@dp.message_handler(state=CalcState.soat)
async def calc_get_soat(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Faqat raqam kiriting!")
    
    await state.update_data(soat=int(message.text))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no())
    await CalcState.sinf.set()

@dp.message_handler(state=CalcState.sinf)
async def calc_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    bhm = db.get_setting('bhm')
    stavka = db.get_setting(data['toifa'])
    
    # Formula: (Stavka / 18 * soat) + (Sinf rahbarlik agar bo'lsa)
    sinf_ustamasi = bhm if "Ha" in message.text else 0
    jami = (stavka / 18 * data['soat']) + sinf_ustamasi
    toza_oylik = jami * 0.87 # 12% soliq + 1% pensiya
    
    res_text = (
        f"📊 *Hisob-kitob natijasi:*\n\n"
        f"🔹 Toifa: {data['toifa'].capitalize()}\n"
        f"🔹 Dars soati: {data['soat']} soat\n"
        f"🔹 Sinf rahbarlik: {'Mavjud' if sinf_ustamasi > 0 else 'Yoʻq'}\n"
        f"--------------------------\n"
        f"💰 *Qo'lga tegadigan oylik:* {round(toza_oylik, 2):,} so'm"
    )
    await message.answer(res_text, reply_markup=kb.main_menu())
    await state.finish()

# --- ISH REJALAR VA DARSLIKLAR ---

@dp.message_handler(text=["📚 Ish rejalar", "📁 Darsliklar", "📝 Testlar"])
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"*{message.text}* bo'limi uchun fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda message: message.text in ["Ona tili", "Matematika", "Ingliz tili", "Tarix", "Fizika"])
async def subject_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    files = db.get_files(data['cat'], message.text)
    
    if not files:
        await message.answer("❌ Bu bo'limda hozircha fayllar mavjud emas.")
    else:
        await message.answer("Fayllar yuklanmoqda...")
        for name, f_id in files:
            await bot.send_document(message.from_user.id, f_id, caption=name)

# --- ADMIN: FAYL QO'SHISH ---

@dp.message_handler(text="➕ Fayl qo'shish")
async def add_file_start(message: types.Message):
    if message.from_user.id != ADMIN_ID: return
    await message.answer("Kategoriyani tanlang:", reply_markup=kb.cat_menu())
    await AdminState.add_file_cat.set()

@dp.message_handler(state=AdminState.add_file_cat)
async def add_file_cat(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer("Fanni tanlang:", reply_markup=kb.subjects_menu())
    await AdminState.add_file_subj.set()

@dp.message_handler(state=AdminState.add_file_subj)
async def add_file_subj(message: types.Message, state: FSMContext):
    await state.update_data(subj=message.text)
    await message.answer("Fayl nomini kiriting (Caption):")
    await AdminState.add_file_name.set()

@dp.message_handler(state=AdminState.add_file_name)
async def add_file_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Endi faylni o'zini yuboring (Document):")
    await AdminState.add_file_doc.set()

@dp.message_handler(state=AdminState.add_file_doc, content_types=ContentType.DOCUMENT)
async def add_file_doc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_file(data['name'], message.document.file_id, data['cat'], data['subj'])
    await message.answer("✅ Fayl muvaffaqiyatli bazaga qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ADMIN: REKLAMA (HAMMAGA) ---

@dp.message_handler(text="📢 Reklama yuborish")
async def reklama_start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Reklama xabarini yuboring (Rasm, Video yoki Text):")
        await AdminState.reklama.set()

@dp.message_handler(state=AdminState.reklama, content_types=ContentType.ANY)
async def reklama_send(message: types.Message, state: FSMContext):
    users = db.get_users()
    count = 0
    for user in users:
        try:
            await message.copy_to(user[0])
            count += 1
            await asyncio.sleep(0.05) # Spamga tushmaslik uchun
        except:
            pass
    await message.answer(f"✅ Reklama {count} ta foydalanuvchiga yuborildi.", reply_markup=kb.admin_menu())
    await state.finish()

# --- BAZANI TOZALASH ---
@dp.message_handler(text="🧹 Bazani tozalash")
async def db_clean(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        db.clean_db()
        await message.answer("🗑 Foydalanuvchilar bazasi tozalandi!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
