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
    calc_toifa = State()
    calc_soat = State()
    calc_sinf = State()
    calc_daftar = State()
    calc_sertifikat = State()
    calc_staj = State()
    calc_olis = State()
    
    # AI va Reklama
    ai_query = State()
    reklama = State()
    
    # Fayl qo'shish (Admin)
    add_f_cat = State()
    add_f_subj = State()
    add_f_quarter = State()
    add_f_name = State()
    add_f_file = State()
    
    # Vakansiya, O'quv yili, Choraklar (Admin)
    add_vac_title = State()
    add_vac_link = State()
    set_year = State()
    add_quarter = State()
    del_quarter = State()

    # Narxlar va Dinamik elementlar
    changing_price = State()
    new_category = State()
    new_subject = State()
    add_q_subj = State()
    add_q_file = State()

# --- 1. ASOSIY BO'LIM (START) ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    settings = db.get_settings()
    study_year = settings.get('study_year', "O'quv yili belgilanmagan")
    
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Foydalanuvchi"
    db.add_user(user_id, message.from_user.full_name)
    
    text = f"👋 Salom, {user_name}!\n\n📅 **Joriy o'quv yili:** {study_year}\n\nKerakli bo'limni tanlang:"
    await message.answer(text, reply_markup=kb.main_menu(is_admin_check(user_id)))

# --- 2. OYLIK HISOBLASH ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text)
    await message.answer("Dars soatingizni kiriting:", reply_markup=kb.back_menu())
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_soat(message: types.Message, state: FSMContext):
    if not is_float(message.text): return await message.answer("❌ Faqat raqam kiriting!")
    await state.update_data(soat=message.text.replace(',', '.'))
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def salary_sinf(message: types.Message, state: FSMContext):
    val = True if "HA" in message.text.upper() else False
    await state.update_data(sinf_rahbar=val)
    await message.answer("Daftar tekshirish bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_daftar)
async def salary_daftar(message: types.Message, state: FSMContext):
    val = True if "HA" in message.text.upper() else False
    await state.update_data(daftar_tekshirish=val)
    await message.answer("Sertifikat ustamasi (%):", reply_markup=kb.back_menu())
    await BotStates.calc_sertifikat.set()

@dp.message_handler(state=BotStates.calc_sertifikat)
async def salary_sertifikat(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ Raqam kiriting!")
    await state.update_data(sertifikat=int(message.text))
    await message.answer("Ish stajingiz (yil):", reply_markup=kb.back_menu())
    await BotStates.calc_staj.set()

@dp.message_handler(state=BotStates.calc_staj)
async def salary_staj(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ Raqam kiriting!")
    await state.update_data(staj=int(message.text))
    await message.answer("Olis hududmi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_olis.set()

@dp.message_handler(state=BotStates.calc_olis)
async def salary_final(message: types.Message, state: FSMContext):
    olis = True if "HA" in message.text.upper() else False
    await state.update_data(olis_hudud=olis)
    data = await state.get_data()
    res = func.calculate_salary_advanced(db, data)
    await message.answer(f"📊 **Natija:**\n💰 **Oylik: {res:,.0f} so'm**".replace(',', ' '), 
                         reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 3. AI YORDAMCHI ---
@dp.message_handler(text="🤖 AI Yordamchi", state="*")
async def ai_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("🤖 Savolingizni yozing:", reply_markup=kb.back_menu())
    await BotStates.ai_query.set()

@dp.message_handler(state=BotStates.ai_query)
async def ai_res(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    wait_msg = await message.answer("⌛️ *O'ylayapman...*")
    try:
        res = await func.get_ai_answer(message.text)
        await wait_msg.delete()
        await message.answer(f"🤖 **AI:**\n\n{res}")
    except:
        await wait_msg.edit_text("❌ Xatolik yuz berdi.")
    finally:
        await state.finish()

# --- 4. FOYDALANUVCHILAR UCHUN FAYL QIDIRISH VA VAKANSIYA ---
@dp.message_handler(lambda m: m.text in db.get_categories())
async def category_select(message: types.Message, state: FSMContext):
    await state.update_data(cat=message.text)
    await message.answer(f"📂 {message.text}:", reply_markup=kb.subjects_menu())

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

# --- 5. ADMIN PANEL ASOSIY ---
@dp.message_handler(text="⚙️ Admin panel", state="*")
@dp.message_handler(text="⚙️ Narxlarni o'zgartirish", state="*") # Ikkala tugma ham bitta menyuga olib boradi
async def admin_main(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("🛠 Admin panel:", reply_markup=kb.admin_menu())

# --- ADMIN: NARX VA BHM SOZLAMALARI ---
@dp.callback_query_handler(lambda c: c.data.startswith('set_'))
async def process_setting_change(callback_query: types.CallbackQuery, state: FSMContext):
    key = callback_query.data.split('_')[1]
    await state.update_data(changing_key=key)
    names = {"bhm": "BHM", "oliy": "Oliy toifa", "birinchi": "1-toifa", "ikkinchi": "2-toifa", "mutaxassis": "Mutaxassis"}
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, f"📝 {names.get(key, key)} uchun yangi qiymatni kiriting:")
    await BotStates.changing_price.set()

@dp.message_handler(state=BotStates.changing_price)
async def save_new_price(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    if not message.text.isdigit(): return await message.answer("❌ Faqat raqam kiriting!")
    data = await state.get_data()
    key = data.get('changing_key')
    db.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, message.text))
    db.connection.commit()
    await message.answer(f"✅ Yangilandi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ADMIN: DINAMIK ELEMENTLAR (Kategoriya/Fan) ---
@dp.message_handler(text="➕ Kategoriya/Fan/Chorak", state="*")
async def add_elements_menu(message: types.Message):
    if is_admin_check(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("📂 Yangi Kategoriya", "📚 Yangi Fan", "🔢 Chorak qo'shish", "🏠 Bosh menu")
        await message.answer("Nima qo'shmoqchisiz?", reply_markup=markup)

@dp.message_handler(text="📂 Yangi Kategoriya")
async def add_cat_start(message: types.Message):
    await message.answer("Yangi kategoriya nomini kiriting:", reply_markup=kb.back_menu())
    await BotStates.new_category.set()

@dp.message_handler(state=BotStates.new_category)
async def save_category(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    db.add_item("categories", "name", message.text)
    await message.answer(f"✅ Kategoriya qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="📚 Yangi Fan")
async def add_subj_start(message: types.Message):
    await message.answer("Yangi fan nomini kiriting:", reply_markup=kb.back_menu())
    await BotStates.new_subject.set()

@dp.message_handler(state=BotStates.new_subject)
async def save_subject(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    db.add_item("subjects", "name", message.text)
    await message.answer(f"✅ Fan qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ADMIN: STATISTIKA VA REKLAMA ---
@dp.message_handler(text="📊 Statistika", state="*")
async def admin_stat(message: types.Message):
    if is_admin_check(message.from_user.id):
        count = db.get_users_count()
        await message.answer(f"👥 **Bot foydalanuvchilari soni:** {count} ta")

@dp.message_handler(text="📢 Xabar yuborish", state="*")
async def broadcast_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Xabarni yuboring (rasm, tekst, video yoki hujjat):", reply_markup=kb.back_menu())
        await BotStates.reklama.set()

@dp.message_handler(state=BotStates.reklama, content_types=types.ContentTypes.ANY)
async def broadcast_final(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    users = db.get_items("users")
    send_count = 0
    error_count = 0
    msg = await message.answer("🚀 Xabar yuborilmoqda...")
    for user in users:
        try:
            await bot.copy_message(chat_id=user[0], from_chat_id=message.chat.id, message_id=message.message_id)
            send_count += 1
            await asyncio.sleep(0.05) 
        except:
            error_count += 1
    await msg.edit_text(f"📢 **Xabar yuborish yakunlandi!**\n\n✅ Yetkazildi: {send_count}\n❌ Yetkazilmadi: {error_count}")
    await state.finish()

# --- ADMIN: O'QUV YILI VA CHORAKLAR ---
@dp.message_handler(text="📅 O'quv yilini o'zgartirish", state="*")
async def set_year_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        current_year = db.get_settings().get('study_year', "Noma'lum")
        await message.answer(f"Hozirgi o'quv yili: {current_year}\nYangi yilni kiriting:", reply_markup=kb.back_menu())
        await BotStates.set_year.set()

@dp.message_handler(state=BotStates.set_year)
async def set_year_final(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    db.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", ('study_year', message.text))
    db.connection.commit()
    await message.answer(f"✅ O'quv yili {message.text} ga yangilandi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="🔢 Choraklarni boshqarish", state="*")
async def manage_quarters(message: types.Message):
    if is_admin_check(message.from_user.id):
        quarters = db.get_quarters()
        text = "🔢 **Mavjud choraklar:**\n" + "\n".join([f"🔹 {q}" for q in quarters])
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("➕ Chorak qo'shish", "➖ Chorakni o'chirish", "🏠 Bosh menu")
        await message.answer(text, reply_markup=markup)

@dp.message_handler(text="➕ Chorak qo'shish")
async def add_q_start(message: types.Message):
    await message.answer("Chorak nomini kiriting:", reply_markup=kb.back_menu())
    await BotStates.add_quarter.set()

@dp.message_handler(state=BotStates.add_quarter)
async def add_q_final(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    db.add_item("quarters", "name", message.text)
    await message.answer(f"✅ {message.text} qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ADMIN: VAKANSIYA VA FAYL QO'SHISH ---
@dp.message_handler(text="➕ Vakansiya qo'shish", state="*")
async def add_vac_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        await message.answer("Vakansiya sarlavhasi:", reply_markup=kb.back_menu())
        await BotStates.add_vac_title.set()

@dp.message_handler(state=BotStates.add_vac_title)
async def add_vac_t(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(v_title=message.text)
    await message.answer("Linkni yuboring:")
    await BotStates.add_vac_link.set()

@dp.message_handler(state=BotStates.add_vac_link)
async def add_vac_final(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    data = await state.get_data()
    db.add_vacancy(data['v_title'], message.text)
    await message.answer("✅ Vakansiya qo'shildi!", reply_markup=kb.admin_menu())
    await state.finish()

@dp.message_handler(text="➕ Fayl qo'shish", state="*")
async def add_file_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        cats = db.get_categories()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for c in cats: markup.insert(types.KeyboardButton(c))
        markup.add("🏠 Bosh menu")
        await message.answer("Kategoriyani tanlang:", reply_markup=markup)
        await BotStates.add_f_cat.set()

@dp.message_handler(state=BotStates.add_f_cat)
async def add_file_cat(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(f_cat=message.text)
    subs = db.get_subjects()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for s in subs: markup.insert(types.KeyboardButton(s))
    markup.add("🏠 Bosh menu")
    await message.answer("Fanni tanlang:", reply_markup=markup)
    await BotStates.add_f_subj.set()

@dp.message_handler(state=BotStates.add_f_subj)
async def add_file_subj(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(f_subj=message.text)
    data = await state.get_data()
    if "Ish reja" in data['f_cat']:
        qs = db.get_quarters()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for q in qs: markup.insert(types.KeyboardButton(q))
        markup.add("🏠 Bosh menu")
        await message.answer("Chorakni tanlang:", reply_markup=markup)
        await BotStates.add_f_quarter.set()
    else:
        await state.update_data(f_quarter=None)
        await message.answer("Fayl nomini kiriting:", reply_markup=kb.back_menu())
        await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_quarter)
async def add_file_quarter(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(f_quarter=message.text)
    await message.answer("Fayl nomini kiriting:", reply_markup=kb.back_menu())
    await BotStates.add_f_name.set()

@dp.message_handler(state=BotStates.add_f_name)
async def add_file_name(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(f_name=message.text)
    await message.answer("Faylni yuboring (Document):")
    await BotStates.add_f_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_f_file)
async def add_file_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_file(data['f_name'], message.document.file_id, data['f_cat'], data['f_subj'], data.get('f_quarter'))
    await message.answer("✅ Fayl saqlandi!", reply_markup=kb.admin_menu())
    await state.finish()

# --- ADMIN: TEST QO'SHISH ---
@dp.message_handler(text="➕ Test qo'shish", state="*")
async def add_quiz_start(message: types.Message):
    if is_admin_check(message.from_user.id):
        subs = db.get_subjects()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for s in subs: markup.insert(types.KeyboardButton(s))
        markup.add("🏠 Bosh menu")
        await message.answer("Qaysi fan uchun test yuklamoqchisiz?", reply_markup=markup)
        await BotStates.add_q_subj.set()

@dp.message_handler(state=BotStates.add_q_subj)
async def add_quiz_subj(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(q_subj=message.text)
    await message.answer("📂 Test faylini yuboring (.txt formatida):", reply_markup=kb.back_menu())
    await BotStates.add_q_file.set()

@dp.message_handler(content_types=['document'], state=BotStates.add_q_file)
async def add_quiz_final(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # file_id = message.document.file_id # QuizEngine da foydalanish uchun
    await message.answer(f"✅ {data['q_subj']} fani bo'yicha testlar yuklandi!", reply_markup=kb.admin_menu())
    await state.finish()

if __name__ == '__main__':
    if not os.path.exists('downloads'): os.makedirs('downloads')
    executor.start_polling(dp, skip_updates=True)
