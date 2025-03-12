import asyncio
import json
import logging
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

# Logging sozlamasi
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Bot tokeni
TOKEN = "7920158290:AAGHF0oNivVsHN6aehc9j32KYn3zkWjVt-Q"  # Haqiqiy tokenni qo‘ying

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Ma'lumotlarni saqlash uchun fayl nomi
USERS_FILE = "users.json"

# Asosiy menyu klaviaturasi
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Izlash")],
            [KeyboardButton(text="📊 Statistika")]
        ],
        resize_keyboard=True
    )

# "Bekor qilish" tugmasini qo‘shish uchun yordamchi funksiya
def add_cancel_button(keyboard):
    keyboard.append([KeyboardButton(text="❌ Bekor qilish")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Foydalanuvchilarni fayldan yuklash
def load_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            logging.info(f"Fayldan yuklangan foydalanuvchilar: {data}")
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        logging.info("Fayl topilmadi yoki bo‘sh, bo‘sh ro‘yxat qaytarildi")
        return []

# Foydalanuvchilarni faylga saqlash
def save_users(users):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
            logging.info(f"Faylga saqlangan foydalanuvchilar: {users}")
    except Exception as e:
        logging.error(f"Faylga saqlashda xato: {e}")

users = load_users()  # Boshlang'ich foydalanuvchilar ro'yxati

# 📜 Holatlar
class Registration(StatesGroup):
    age = State()
    gender = State()
    location = State()
    purpose = State()
    contact = State()

class Search(StatesGroup):
    gender = State()
    age = State()

# 📝 Boshlang'ich xush kelibsiz xabari va ro‘yxatdan o‘tish
@dp.message(Command("start"))
async def send_welcome(message: types.Message, state: FSMContext):
    name = message.from_user.full_name
    markup = [
        [KeyboardButton(text="17 yoshgacha"), KeyboardButton(text="18-20 yosh")],
        [KeyboardButton(text="21-25 yosh"), KeyboardButton(text="26-30 yosh")],
        [KeyboardButton(text="30 yoshdan katta")]
    ]
    await message.answer(f"Xush kelibsiz, {name}! Ro‘yxatdan o‘ting:\n📝 Yoshingizni tanlang:", reply_markup=add_cancel_button(markup))
    await state.set_state(Registration.age)

# 📅 Ro‘yxatdan o‘tish uchun yoshni tanlash
@dp.message(Registration.age)
async def process_age(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Ro‘yxatdan o‘tish bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_ages = ["17 yoshgacha", "18-20 yosh", "21-25 yosh", "26-30 yosh", "30 yoshdan katta"]
    user_input = message.text.strip()
    logging.info(f"Ro‘yxatdan o‘tishda kiritilgan yosh: '{user_input}'")
    
    if user_input not in valid_ages:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        logging.warning(f"Noto‘g‘ri yosh kiritildi: '{user_input}'")
        return
    
    await state.update_data(age=user_input)
    logging.info(f"Yosh saqlandi: {user_input}")
    markup = [[KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]]
    await message.answer("🚻 Jinsingizni tanlang:", reply_markup=add_cancel_button(markup))
    await state.set_state(Registration.gender)

# 🚻 Jinsni tanlash
@dp.message(Registration.gender)
async def process_gender(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Ro‘yxatdan o‘tish bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_genders = ["Erkak", "Ayol"]
    if message.text not in valid_genders:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        return
    await state.update_data(gender=message.text)
    markup = [
        [KeyboardButton(text="Urganch"), KeyboardButton(text="Xiva")],
        [KeyboardButton(text="Qo‘shko‘pir"), KeyboardButton(text="Yangiariq")],
        [KeyboardButton(text="Xonqa"), KeyboardButton(text="Bog‘ot")],
        [KeyboardButton(text="Xazarasp"), KeyboardButton(text="Tuproqqala")],
        [KeyboardButton(text="Shovot"), KeyboardButton(text="Gurlan")],
        [KeyboardButton(text="Yangibozor")]
    ]
    await message.answer("📍 Hududingizni tanlang:", reply_markup=add_cancel_button(markup))
    await state.set_state(Registration.location)

# 📍 Hududni tanlash
@dp.message(Registration.location)
async def process_location(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Ro‘yxatdan o‘tish bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_locations = ["Urganch", "Xiva", "Qo‘shko‘pir", "Yangiariq", "Xonqa", "Bog‘ot", "Xazarasp", "Tuproqqala", "Shovot", "Gurlan", "Yangibozor"]
    if message.text not in valid_locations:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        return
    await state.update_data(location=message.text)
    markup = [
        [KeyboardButton(text="Sevgi"), KeyboardButton(text="Do‘stlik")],
        [KeyboardButton(text="Oila qurish"), KeyboardButton(text="Muloqot")]
    ]
    await message.answer("🎯 Tanishuvdan maqsadingizni tanlang:", reply_markup=add_cancel_button(markup))
    await state.set_state(Registration.purpose)

# 🎯 Maqsadni tanlash
@dp.message(Registration.purpose)
async def process_purpose(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Ro‘yxatdan o‘tish bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_purposes = ["Sevgi", "Do‘stlik", "Oila qurish", "Muloqot"]
    if message.text not in valid_purposes:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        return
    await state.update_data(purpose=message.text)
    
    # Kontakt kiritish uchun faqat "Bekor qilish" tugmasi bo‘lgan klaviatura
    markup = [[KeyboardButton(text="❌ Bekor qilish")]]
    await message.answer("📞 Bog‘lanish uchun username (@username) yoki telefon raqamingizni kiriting:", reply_markup=add_cancel_button(markup))
    await state.set_state(Registration.contact)

# ✅ Kontaktni qayta ishlash va ro‘yxatdan o‘tish yakuni
@dp.message(Registration.contact)
async def process_contact(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Ro‘yxatdan o‘tish bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    contact = message.text
    phone_pattern = r"^\+?\d{9,15}$"
    if not (contact.startswith("@") or re.match(phone_pattern, contact)):
        await message.answer("Iltimos, to‘g‘ri username (@username) yoki telefon raqamini kiriting!")
        return
    user_data = await state.get_data()
    user_data["contact"] = contact
    user_data["user_id"] = message.from_user.id
    user_data["name"] = message.from_user.full_name
    global users
    users = [u for u in users if u["user_id"] != message.from_user.id]
    users.append(user_data)
    save_users(users)
    await message.answer("✅ Ro‘yxatdan muvaffaqiyatli o‘tdingiz! Endi izlash mumkin:", reply_markup=get_main_menu())
    await state.clear()

# 🔍 Izlash bo‘limi
@dp.message(lambda message: message.text == "🔍 Izlash")
async def start_search(message: types.Message, state: FSMContext):
    markup = [[KeyboardButton(text="Erkak"), KeyboardButton(text="Ayol")]]
    await message.answer("👤 Kimni izlayapsiz?", reply_markup=add_cancel_button(markup))
    await state.set_state(Search.gender)

# 🚻 Izlash uchun jins tanlash
@dp.message(Search.gender)
async def process_search_gender(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Izlash bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_genders = ["Erkak", "Ayol"]
    user_input = message.text.strip()
    logging.info(f"Izlashda kiritilgan jins: '{user_input}'")
    
    if user_input not in valid_genders:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        logging.warning(f"Noto‘g‘ri jins kiritildi: '{user_input}'")
        return
    
    await state.update_data(gender=user_input)
    logging.info(f"Jins saqlandi: {user_input}")
    markup = [
        [KeyboardButton(text="17 yoshgacha"), KeyboardButton(text="18-20 yosh")],
        [KeyboardButton(text="21-25 yosh"), KeyboardButton(text="26-30 yosh")],
        [KeyboardButton(text="30 yoshdan katta")]
    ]
    await message.answer("📅 Yosh toifasini tanlang:", reply_markup=add_cancel_button(markup))
    await state.set_state(Search.age)

# 📅 Izlash uchun yoshni tanlash va natijalarni chiqarish
@dp.message(Search.age)
async def process_search_age(message: types.Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await message.answer("Izlash bekor qilindi.", reply_markup=get_main_menu())
        await state.clear()
        return
    
    valid_ages = ["17 yoshgacha", "18-20 yosh", "21-25 yosh", "26-30 yosh", "30 yoshdan katta"]
    user_input = message.text.strip()
    logging.info(f"Izlashda kiritilgan yosh: '{user_input}'")
    
    if user_input not in valid_ages:
        await message.answer("Iltimos, faqat berilgan variantlardan birini tanlang!")
        logging.warning(f"Izlashda noto‘g‘ri yosh kiritildi: '{user_input}'")
        return
    
    await state.update_data(age=user_input)
    logging.info(f"Izlashda yosh saqlandi: {user_input}")
    search_data = await state.get_data()
    logging.info(f"Joriy users ro‘yxati: {users}")
    results = [
        user for user in users
        if user["gender"] == search_data["gender"] and user["age"] == search_data["age"]
    ]
    logging.info(f"Izlash natijalari: {results}")
    await state.update_data(results=results)
    
    # Natijalarni ko‘rsatish
    if results:
        anketa_text = f"<b>📜 Natijalar ({len(results)} ta):</b>\n\n"
        for i, user in enumerate(results, 1):
            anketa_text += (
                f"<b>{i}. Anketa:</b>\n"
                f"🧑 <b>Ismi:</b> {user.get('name', 'Noma’lum')}\n"
                f"👤 <b>Jinsi:</b> {user['gender']}\n"
                f"📅 <b>Yoshi:</b> {user['age']}\n"
                f"📍 <b>Hududi:</b> {user['location']}\n"
                f"🎯 <b>Maqsadi:</b> {user['purpose']}\n"
                f"📞 <b>Bog‘lanish:</b> {user['contact']}\n\n"
            )
        await message.answer(anketa_text, parse_mode="HTML")
    else:
        await message.answer("❌ Hozircha mos anketalar yo‘q.")
    
    # Natijalardan so‘ng asosiy menyuga qaytish
    await message.answer("Asosiy menyuga qaytdingiz:", reply_markup=get_main_menu())
    await state.clear()

# 📊 Statistika ko‘rsatish komandasi
@dp.message(Command("stats"))
async def show_stats(message: types.Message):
    global users
    users = load_users()
    
    if not users:
        await message.answer("Hozircha ro‘yxatdan o‘tgan foydalanuvchilar yo‘q.")
        return
    
    total_users = len(users)
    male_count = sum(1 for user in users if user["gender"] == "Erkak")
    female_count = sum(1 for user in users if user["gender"] == "Ayol")
    
    age_groups = {
        "17 yoshgacha": 0,
        "18-20 yosh": 0,
        "21-25 yosh": 0,
        "26-30 yosh": 0,
        "30 yoshdan katta": 0
    }
    for user in users:
        age_groups[user["age"]] += 1
    
    stats_text = (
        "📊 <b>Foydalanuvchilar Statistikasi</b>\n\n"
        f"👥 <b>Umumiy foydalanuvchilar soni:</b> {total_users} ta\n"
        f"👨 <b>Erkaklar:</b> {male_count} ta ({male_count/total_users*100:.1f}%)\n"
        f"👩 <b>Ayollar:</b> {female_count} ta ({female_count/total_users*100:.1f}%)\n\n"
        "📅 <b>Yosh bo‘yicha taqsimot:</b>\n"
    )
    
    for age_group, count in age_groups.items():
        stats_text += f"  • {age_group}: {count} ta ({count/total_users*100:.1f}%)\n"
    
    await message.answer(stats_text, parse_mode="HTML")

# 📊 Statistika tugmasi uchun handler
@dp.message(lambda message: message.text == "📊 Statistika")
async def stats_button(message: types.Message):
    await show_stats(message)

# Asosiy ishga tushirish
if __name__ == "__main__":
    try:
        asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logging.info("Bot foydalanuvchi tomonidan to‘xtatildi")
    except Exception as e:
        logging.error(f"Xato yuz berdi: {e}")