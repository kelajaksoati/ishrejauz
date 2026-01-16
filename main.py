import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN, ADMIN_ID
from database import Database
from quiz_engine import QuizEngine 
import keyboards as kb
import functions as func
from generator import generate_certificate_pdf

# --- LOGGING VA ASOSIY SOZLAMALAR ---
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot, storage=MemoryStorage())
db = Database('ebaza_ultimate.db')
qe = QuizEngine()

# --- ADMIN TEKSHIRUV ---
def is_admin_check(user_id):
    return str(user_id) == str(ADMIN_ID)

# --- FSM (HOLATLAR) ---
class BotStates(StatesGroup):
    # Oylik hisoblash zanjiri
    calc_toifa = State(); calc_soat = State(); calc_sinf = State()
    calc_u_soni = State(); calc_daftar = State(); calc_kabinet = State()
    calc_sertifikat = State(); calc_staj = State(); calc_olis = State()
    
    # Vakansiya joylash zanjiri
    vac_muassasa = State(); vac_manzil = State(); vac_fan = State()
    
    # Aloqa va Sozlamalar
    waiting_for_feedback = State()
    waiting_for_price = State()
    reklama = State()

# --- 1. START VA ASOSIY MENU ---
@dp.message_handler(commands=['start'], state="*")
@dp.message_handler(text="🏠 Bosh menu", state="*")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    db.add_user(user_id, message.from_user.full_name)
    
    settings = db.get_settings()
    year = settings.get('study_year', '2024-2025')
    
    text = (
        f"👋 Salom, {message.from_user.first_name}!\n\n"
        f"📅 **O'quv yili:** {year}\n"
        f"📌 Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=kb.main_menu(is_admin_check(user_id)))

# --- 2. ULTRA OYLIK HISOBLASH (LOGIK ZANJIR) ---
@dp.message_handler(text="💰 Oylik hisoblash", state="*")
async def salary_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Toifangizni tanlang:", reply_markup=kb.toifa_menu())
    await BotStates.calc_toifa.set()

@dp.message_handler(state=BotStates.calc_toifa)
async def salary_toifa(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(toifa=message.text)
    await message.answer("Haftalik dars soatingizni kiriting (masalan: 18):")
    await BotStates.calc_soat.set()

@dp.message_handler(state=BotStates.calc_soat)
async def salary_soat(message: types.Message, state: FSMContext):
    if not message.text.replace('.', '', 1).isdigit():
        return await message.answer("❌ Iltimos, faqat raqam kiriting!")
    await state.update_data(soat=message.text)
    await message.answer("Sinf rahbarligingiz bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sinf.set()

@dp.message_handler(state=BotStates.calc_sinf)
async def salary_sinf(message: types.Message, state: FSMContext):
    if message.text == "Ha":
        await state.update_data(sinf_rahbar=True)
        await message.answer("Sinfingizda necha nafar o'quvchi bor?")
        await BotStates.calc_u_soni.set()
    else:
        await state.update_data(sinf_rahbar=False, uquvchi_soni=0)
        await message.answer("Daftar tekshirish ustamasi bormi?", reply_markup=kb.yes_no_menu())
        await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_u_soni)
async def salary_u_soni(message: types.Message, state: FSMContext):
    await state.update_data(uquvchi_soni=message.text)
    await message.answer("Daftar tekshirish ustamasi bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_daftar.set()

@dp.message_handler(state=BotStates.calc_daftar)
async def salary_daftar(message: types.Message, state: FSMContext):
    await state.update_data(daftar=(message.text == "Ha"))
    await message.answer("Kabinet mudirligi bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_kabinet.set()

@dp.message_handler(state=BotStates.calc_kabinet)
async def salary_kabinet(message: types.Message, state: FSMContext):
    await state.update_data(kabinet=(message.text == "Ha"))
    await message.answer("C1/Sertifikat (20%) ustamasi bormi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_sertifikat.set()

@dp.message_handler(state=BotStates.calc_sertifikat)
async def salary_sert(message: types.Message, state: FSMContext):
    await state.update_data(sertifikat=(message.text == "Ha"))
    await message.answer("Olis hududda dars berasizmi?", reply_markup=kb.yes_no_menu())
    await BotStates.calc_olis.set()

@dp.message_handler(state=BotStates.calc_olis)
async def salary_olis_hudud(message: types.Message, state: FSMContext):
    if message.text == "Ha":
        await state.update_data(olis_hudud=True)
        await message.answer("Pedagogik stajingizni kiriting (yil):")
        await BotStates.calc_staj.set()
    else:
        await state.update_data(olis_hudud=False, staj=0)
        data = await state.get_data()
        await message.answer(func.calculate_salary_final(data, db), reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
        await state.finish()

@dp.message_handler(state=BotStates.calc_staj)
async def salary_staj_final(message: types.Message, state: FSMContext):
    await state.update_data(staj=message.text)
    data = await state.get_data()
    await message.answer(func.calculate_salary_final(data, db), reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 3. VAKANSIYA JOYLASHTIRISH ---
@dp.message_handler(text="➕ Vakansiya joylash", state="*")
async def vac_1(message: types.Message):
    await message.answer("🏫 Muassasa nomi va raqami?", reply_markup=kb.back_menu())
    await BotStates.vac_muassasa.set()

@dp.message_handler(state=BotStates.vac_muassasa)
async def vac_2(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    await state.update_data(muassasa=message.text)
    await message.answer("📍 Manzil (Viloyat, tuman)?")
    await BotStates.vac_manzil.set()

@dp.message_handler(state=BotStates.vac_manzil)
async def vac_3(message: types.Message, state: FSMContext):
    await state.update_data(manzil=message.text)
    await message.answer("📚 Qaysi fan o'qituvchisi kerak?")
    await BotStates.vac_fan.set()

@dp.message_handler(state=BotStates.vac_fan)
async def vac_4(message: types.Message, state: FSMContext):
    data = await state.get_data()
    db.add_vacancy(
        muassasa=data['muassasa'],
        manzil=data['manzil'],
        fan=message.text,
        user_id=message.from_user.id
    )
    await message.answer("✅ Vakansiya muvaffaqiyatli qo'shildi!", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- 4. TEST VA REYTING ---
@dp.message_handler(text="📝 Onlayn Test", state="*")
async def quiz_menu(message: types.Message):
    db.add_activity(message.from_user.id, "Test")
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🚀 Testni boshlash", callback_data="start_quiz"),
        InlineKeyboardButton("🏆 Top 10 Reyting", callback_data="show_rating")
    )
    await message.answer("📝 Onlayn test va haftalik reyting bo'limi:", reply_markup=markup)

@dp.callback_query_handler(text="show_rating")
async def rating_call(call: types.CallbackQuery):
    top = db.get_top_rating()
    if not top:
        return await call.answer("Hozircha natijalar yo'q", show_alert=True)
    
    text = "🏆 **Haftalik Top O'qituvchilar:**\n\n"
    for i, r in enumerate(top, 1):
        text += f"{i}. {r[0]} - {r[1]}%\n"
    await call.message.answer(text)

# --- 5. ADMIN VA ALOQA ---
@dp.message_handler(text="📊 Statistika")
async def admin_stat(message: types.Message):
    if not is_admin_check(message.from_user.id): return
    u, active = db.get_stats()
    text = (
        f"📈 **Bot statistikasi:**\n\n"
        f"👤 Jami foydalanuvchilar: {u} ta\n"
        f"🔥 Eng faol bo'lim: {active[0] if active else 'Yoq'}"
    )
    await message.answer(text)

@dp.message_handler(text="✍️ Adminga murojaat", state="*")
async def feedback(message: types.Message):
    await message.answer("📝 Xabaringizni yozing:", reply_markup=kb.back_menu())
    await BotStates.waiting_for_feedback.set()

@dp.message_handler(state=BotStates.waiting_for_feedback)
async def feedback_send(message: types.Message, state: FSMContext):
    if message.text == "🏠 Bosh menu": return await cmd_start(message, state)
    db.add_feedback(message.from_user.id, message.text)
    await bot.send_message(ADMIN_ID, f"📩 **Yangi murojaat!**\nID: `{message.from_user.id}`\n\n{message.text}")
    await message.answer("✅ Xabaringiz yuborildi.", reply_markup=kb.main_menu(is_admin_check(message.from_user.id)))
    await state.finish()

# --- ADMIN: SOZLAMALAR ---
@dp.callback_query_handler(lambda c: c.data.startswith('set_'))
async def set_price(callback: types.CallbackQuery, state: FSMContext):
    key = callback.data.replace('set_', '')
    await state.update_data(setting_key=key)
    await callback.message.answer(f"🔢 {key} uchun yangi qiymat (raqam) kiriting:")
    await BotStates.waiting_for_price.set()

@dp.message_handler(state=BotStates.waiting_for_price)
async def save_price(message: types.Message, state: FSMContext):
    if not message.text.isdigit(): return await message.answer("❌ Faqat raqam kiriting!")
    data = await state.get_data()
    db.update_setting(data['setting_key'], message.text)
    await message.answer(f"✅ Saqlandi: {data['setting_key']} = {message.text}", reply_markup=kb.admin_menu())
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
