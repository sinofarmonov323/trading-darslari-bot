from aiogram import Bot, Router, types, F
from aiogram.filters import Command, and_f, StateFilter
from config import ADMIN_ID
from database import Database
from keyboards import admin_panel_keyboard, vip_user_keyboard, admin_user_keyboard, premium_user_keyboard
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class AddCourseState(StatesGroup):
    name = State()
    code = State()
    video = State()

class Broadcast(StatesGroup):
    message = State()

class UpdateUser(StatesGroup):
    user = State()

user_type = None

router = Router()
db = Database("database.db")

db.promote_user("admin", user_id=ADMIN_ID)

ADMINS_ID = [admin['user_id'] for admin in db.get_admins()]

@router.message(and_f(Command("admin"), F.from_user.id.in_(ADMINS_ID)))
async def admin_panel(message: types.Message):
    await message.answer("Admin paneliga xush kelibsiz! Bu yerda siz botni boshqarishingiz mumkin.", reply_markup=admin_panel_keyboard())

@router.message(and_f(F.text == "Statistika", F.from_user.id.in_(ADMINS_ID)))
async def show_stats(message: types.Message):
    await message.answer(f"Foydalanuvchilar soni: {len(db.get_all_users())}\nDarslar soni: {db.get_lessons_count()}")

@router.message(and_f(F.text == "Dars Qo'shish", F.from_user.id.in_(ADMINS_ID)))
async def add_course_panel(message: types.Message, state: FSMContext):
    await message.answer("Dars nomini kiriting")
    await state.set_state(AddCourseState.name)

@router.message(and_f(F.text == "Xabar yuborish", F.from_user.id.in_(ADMINS_ID)))
async def send_message_panel(message: types.Message, state: FSMContext):
    await message.answer("Yuboriladigan xabar matnini kiriting")
    await state.set_state(Broadcast.message)

@router.message(and_f(F.text.in_(["VIP Foydalanuvchilar", "PREMIUM Foydalanuvchilar", "Adminlar"]), F.from_user.id.in_(ADMINS_ID)))
async def show_vip_users(message: types.Message):
    if message.text == "VIP Foydalanuvchilar":
        vip_users = db.get_vip_users()
        if vip_users:
            await message.answer(f"VIP foydalanuvchilar soni: {len(vip_users)}", reply_markup=vip_user_keyboard())
        else:
            await message.answer("VIP foydalanuvchilar yo'q.", reply_markup=vip_user_keyboard())
    elif message.text == "PREMIUM Foydalanuvchilar":
        premium_users = db.get_premium_users()
        if premium_users:
            await message.answer(f"PREMIUM foydalanuvchilar soni: {len(premium_users)}", reply_markup=premium_user_keyboard())
        else:
            await message.answer("PREMIUM foydalanuvchilar yo'q.", reply_markup=premium_user_keyboard())
    elif message.text == "Adminlar":
        admin_users = db.get_admins()
        if admin_users:
            admins_username = "@ ".join([user['username'] for user in admin_users])
            await message.answer(f"Adminlar: {admins_username}", reply_markup=admin_user_keyboard())
        else:
            await message.answer("Adminlar yo'q.", reply_markup=admin_user_keyboard())

@router.callback_query(and_f(F.data.in_(["add_vip_user", "add_premium_user", "remove_vip_user", "remove_premium_user", "remove_admin", "add_admin"]), F.from_user.id.in_(ADMINS_ID)))
async def update_user_type(call: types.CallbackQuery, state: FSMContext):
    global user_type
    if call.data == "add_vip_user":
        await call.message.answer("VIP foydalanuvchi usernameini kiriting")
        user_type = "vip"
    elif call.data == "add_premium_user":
        await call.message.answer("PREMIUM foydalanuvchi usernameini kiriting")
        user_type = "premium"
    elif call.data == "remove_vip_user":
        await call.message.answer("VIP foydalanuvchi usernameini kiriting")
        user_type = "oddiy"
    elif call.data == "remove_premium_user":
        await call.message.answer("PREMIUM foydalanuvchi usernameini kiriting")
        user_type = "oddiy"
    elif call.data == "add_admin":
        await call.message.answer("Admin usernameini kiriting")
        user_type = "admin"
    elif call.data == "remove_admin":
        await call.message.answer("Admin usernameini kiriting")
        user_type = "oddiy"
    await call.answer()
    await state.set_state(UpdateUser.user)

@router.message(and_f(StateFilter(Broadcast.message), F.from_user.id.in_(ADMINS_ID)))
async def broadcast_message(message: types.Message, bot: Bot):
    users = db.get_oddiy_users()
    if message.content_type == "text":
        text = message.text
        for user in users:
            try:
                await bot.send_message(user['user_id'], text)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
    elif message.content_type == "photo":
        photo = message.photo[-1].file_id
        for user in users:
            try:
                await bot.send_photo(user['user_id'], photo, caption=message.caption)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
    await message.answer("Xabar barcha foydalanuvchilarga yuborildi!")

@router.message(and_f(StateFilter(AddCourseState.name), F.from_user.id.in_(ADMINS_ID)))
async def add_course_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Dars kodini kiriting")
    await state.set_state(AddCourseState.code)

@router.message(and_f(StateFilter(AddCourseState.code), F.from_user.id.in_(ADMINS_ID)))
async def add_course_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Video yuboring")
    await state.set_state(AddCourseState.video)

@router.message(and_f(StateFilter(AddCourseState.video), F.from_user.id.in_(ADMINS_ID), F.video))
async def add_course_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    code = data.get("code")
    video = message.video.file_id
    db.add_lesson(name, code, video)
    await message.answer("Dars muvaffaqiyatli qo'shildi!")
    await state.clear()

@router.message(and_f(StateFilter(UpdateUser.user), F.from_user.id.in_(ADMINS_ID)))
async def handle_update_user(message: types.Message, state: FSMContext):
    username = message.text.strip()
    if username.startswith("@"):
        username = username[1:]

    user = db.get_user(username=username)
    if not user:
        await message.answer("Bunday foydalanuvchi topilmadi.")
        return

    if user_type == "oddiy":
        db.demote_user(user_type, username)
        await message.answer(f"Foydalanuvchi @{username} {user_type} qilindi!")
    else:
        db.promote_user(user_type, username)
        await message.answer(f"Foydalanuvchi @{username} {user_type} qilindi!")

    await state.clear()
