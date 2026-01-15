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

# --- FSM HOLATLARI (TO'LIQ) ---
class BotStates(StatesGroup):
    # Oylik hisoblash bosqichlari
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    calc_daftar = State()
    calc_sertifikat = State()
    calc_staj = State()
    calc_olis = State()
    
    # AI va boshqalar
    ai_query = State()
    reklama = State()
    
    # Fayl qo'shish
    add_f_cat = State()
    add_f_subj = State()
    add_f_quarter = State()
    add_f_name = State()
    add_f_file = State()
    
    # Vakansiya va Quiz
    add_vac_title = State()
    add_vac_link = State()
    add_q_subj = State()
    add_q_file = State()

# --- 1. ASOSIY BO'LIM ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Foydalanuvchi"
    db.add_user(user_id, message.from_user.full_name)
    
    await message.answer(f"👋 Salom, {user_name}!\nKerakli bo'limni tanlang:", 
                         reply_markup=kb.main_menu(is_admin_check(user_id)))

# --- 2. OYLIK HISOBLASH BO'LIMI ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingizni kiriting (masalan: 18 yoki 22.5):", reply_markup=kb.back_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_soat(message: types.Message, state: FSMContext):
    if not is_float(message.text):
        return await message.answer("❌ Faqat raqam kiriting (masalan: 18.5)!")
    
    await state.update_data(soat=message.text.replace(',', '.'))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def salary_sinf(message: types.Message, state: FSMContext):
    val = True if "HA" in message.text.upper() else False
    await state.update_data(sinf_rahbar=val)
    await message.answer("Daftar tekshirish (yozuv ishlari) bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_daftar)
async def salary_daftar(message: types.Message, state: FSMContext):
    val = True if "HA" in message.text.upper() else False
    await state.update_data(daftar_tekshirish=val)
    await message.answer("Sertifikat ustamasi bormi? (Foizda kiriting, yo'q bo'lsa 0):", reply_markup=kb.back_menu())
    await BotStates.calc_sertifikat.set()

@dp.message_handler(state=BotStates.calc_sertifikat)
async def salary_sertifikat(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ Faqat raqam kiriting!")
    await state.update_data(sertifikat=int(message.text))
    await message.answer("Umumiy ish stajingiz necha yil?", reply_markup=kb.back_menu())
    await BotStates.calc_staj.set()

@dp.message_handler(state=BotStates.calc_staj)
async def salary_staj(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ Faqat raqam kiriting!")
    await state.update_data(staj=int(message.text))
    await message.answer("Olis hududda joylashgan maktabmi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_olis.set()

@dp.message_handler(state=BotStates.calc_olis)
async def salary_final(message: types.Message, state: FSMContext):
    olis = True if "HA" in message.text.upper() else False
    await state.update_data(olis_hudud=olis)
    
    data = await state.get_data()
    res = func.calculate_salary_advanced(db, data)
    
    result_text = (
        f"📊 **Hisob-kitob natijasi:**\n\n"
        f"🔹 Toifa: {data['toifa']}\n"
        f"🔹 Dars soati: {data['soat']}\n"
        f"🔹 Ustamalar: {'Sinf rahbari, ' if data['sinf_rahbar'] else ''}"
        f"{'Daftar tekshirish, ' if data['daftar_tekshirish'] else ''}"
        f"{data['sertifikat']}% sertifikat\n"
        f"🔹 Ish staji: {data['staj']} yil\n"
        f"🔹 Olis hudud: {'Ha' if data['olis_hudud'] else 'Yo\'q'}\n\n"
        f"💰 **Qo'lga tegadigan oylik: {res:,.0f} so'm**".replace(',', ' ')
    )
    
    await message.answer(result_text, reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 3. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi", state="*")
async def ai_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("🤖 Metodik savolingizni yozing:", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    try:
        res = await func.get_ai_answer(message.text)
        await wait_msg.delete()
        await message.answer(f"🤖 **AI Javobi:**\n\n{res}")
    except Exception as e:
        await wait_msg.edit_text("❌ AI xizmatida xatolik yuz berdi.")
    finally:
        await state.finish()

# --- 4. DINAMIK BO'LIMLAR (Fayllar va Rejalar) ---
@dp.message_handler(lambda m: m.text in db.get_categories())
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"📂 {message.text} uchun fanni tanlang:", reply_markup=kb.subjects_menu())

@dp.message_handler(lambda m: m.text in db.get_subjects())
async def subject_select(message: types.Message, state: FSMContext):
    data = await state.get_data()
    cat = data.get('cat', '')
    if cat and "Ish reja" in cat:
        await state.update_data(subj=message.text)
        await message.answer("Chorakni tanlang:", reply_markup=kb.quarter_menu())
    else:
        files = db.get_files(cat, message.text)
        await func.send_files(bot, message.from_user.id, files)

# --- 5. VAKANSIYALAR BO'LIMI ---
@dp.message_handler(text="📢 Vakansiyalar", state="*")
async def show_vacancies(message: types.Message):
    vacs = db.get_vacancies() 
    if not vacs:
        await message.answer("Hozircha bo'sh ish o'rinlari yo'q.")
    else:
        text = "📢 *Bo'sh ish o'rinlari:*\n\n"
        for v in vacs:
            text += f"🔹 {v[1]}\n🔗 [Batafsil ko'rish]({v[2]})\n\n"
        await message.answer(text, disable_web_page_preview=True)

# --- 6. ADMIN PANEL VA VAKANSIYA QO'SHISH ---
@dp.message_handler(text="⚙️ Admin panel", state="*")
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin boshqaruv paneli:", reply_markup=kb.admin_menu())
    else:
        await message.answer("❌ Siz admin emassiz!")

@dp.message_handler(text="➕ Vakansiya qo'shish", state="*")
async def add_vac_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Vakansiya sarlavhasini kiriting (masalan: Matematika o'qituvchisi kerak):")
        await BotStates.add_vac_title.set()

@dp.message_handler(state=BotStates.add_vac_title)
async def add_vac_t(message: types.Message, state: FSMContext):
    await state.update_data(v_title=message.text)
    await message.answer("Vakansiya uchun havola (link) yuboring:")
    await BotStates.add_vac_link.set()

@dp.message_handler(state=BotStates.add_vac_link)
async def add_vac_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Eslatma: database.py dagi add_item funksiyasiga mos holda
    db.add_item("vacancies", "title, link", f"'{data['v_title']}', '{message.text}'")
    await message.answer("✅ Vakansiya muvaffaqiyatli qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ISHGA TUSHIRISH ---
if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
