from aiogram import Bot, Router, types, F
from aiogram.filters import Command, and_f, StateFilter
from config import ADMIN_ID
from database import Database
from keyboards import admin_panel_keyboard, channels_menu_keyboard, vip_user_keyboard, admin_user_keyboard, premium_user_keyboard, lesson_keyboard
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

class RemoveLesson(StatesGroup):
    code = State()

class AddChannel(StatesGroup):
    channel_url = State()

user_type = None

router = Router()
db = Database("database.db")

def is_admin(entity) -> bool:
    db.promote_user("admin", user_id=ADMIN_ID)
    try:
        user_id = entity.from_user.id
    except Exception:
        return False
    return any(adm.get('user_id') == user_id for adm in db.get_admins())

@router.message(and_f(Command("admin"), is_admin))
async def admin_panel(message: types.Message):
    await message.answer("Admin paneliga xush kelibsiz! Bu yerda siz botni boshqarishingiz mumkin.", reply_markup=admin_panel_keyboard())

@router.message(and_f(F.text.in_(["VIP Foydalanuvchilar", "PREMIUM Foydalanuvchilar", "Adminlar", "Statistika", "Darslar", "Xabar yuborish", "Majburiy obuna qo'shish"]), is_admin))
async def show_vip_users(message: types.Message, state: FSMContext):
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
            admins = " ".join([f"@{user['username']}" for user in admin_users])
            await message.answer(f"Adminlar: {admins}", reply_markup=admin_user_keyboard())
        else:
            await message.answer("Adminlar yo'q.", reply_markup=admin_user_keyboard())
    elif message.text == "Statistika":
        await message.answer(f"Foydalanuvchilar soni: {len(db.get_all_users())}\nDarslar soni: {db.get_lessons_count()}")
    elif message.text == "Darslar":
        await message.answer(f"Darslar soni: {db.get_lessons_count()}", reply_markup=lesson_keyboard())
    elif message.text == "Xabar yuborish":
        await message.answer("Yuboriladigan xabar matnini kiriting")
        await state.set_state(Broadcast.message)
    elif message.text == "Majburiy obuna qo'shish":
        await message.answer(f"Majburiy obuna qo'shish bo'limi", reply_markup=channels_menu_keyboard())

@router.callback_query(and_f(F.data.in_(["add_channel", "remove_channels", "view_channels"]), is_admin))
async def handle_channel_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == "add_channel":
        await call.message.answer("Kanalning manzilini kiriting (misol: @kanal_username)")
        await state.set_state(AddChannel.channel_url)
    elif call.data == "remove_channels":
        db.remove_channels()
        await call.message.answer("Barcha kanallar ro'yxatdan o'chirildi.")
    elif call.data == "view_channels":
        channels = ", ".join([channel for channel in db.get_channels()])
        if channels:
            await call.message.answer(f"Majburiy obuna uchun kanallar ro'yxati: {channels}")
        else:
            await call.message.answer("Majburiy azo uchun kanallar yo'q")
    await call.answer()

@router.callback_query(and_f(F.data.in_(["add_lesson", "remove_lesson"]), is_admin))
async def handle_lesson_callback(call: types.CallbackQuery, state: FSMContext):
    if call.data == "add_lesson":
        await call.message.answer("Dars nomini kiriting")
        await state.set_state(AddCourseState.name)
    elif call.data == "remove_lesson":
        await call.message.answer("O'chiriladigan dars kodini kiriting")
        await state.set_state(RemoveLesson.code)

@router.callback_query(and_f(F.data.in_(["add_vip_user", "add_premium_user", "remove_vip_user", "remove_premium_user", "remove_admin", "add_admin"]), is_admin))
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
    elif call.data == "view_admins":
        await call.message.answer("Adminlar ro'yxati:")
        admin_users = db.get_admins()
        if admin_users:
            admins_username = " ".join([f"@{user['username']}" for user in admin_users])
            await call.message.answer(f"Adminlar: {admins_username}")
        else:
            await call.message.answer("Adminlar yo'q.")
        await call.answer()
        return
    await call.answer()
    await state.set_state(UpdateUser.user)

@router.message(and_f(StateFilter(Broadcast.message), is_admin))
async def broadcast_message(message: types.Message, bot: Bot, state: FSMContext):
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
    await state.clear()

@router.message(and_f(StateFilter(AddCourseState.name), is_admin))
async def add_course_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Dars kodini kiriting")
    await state.set_state(AddCourseState.code)

@router.message(and_f(StateFilter(AddCourseState.code), is_admin))
async def add_course_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Video yuboring")
    await state.set_state(AddCourseState.video)

@router.message(and_f(StateFilter(AddCourseState.video), is_admin, F.video))
async def add_course_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    code = data.get("code")
    video = message.video.file_id
    db.add_lesson(name, code, video)
    await message.answer("Dars muvaffaqiyatli qo'shildi!")
    await state.clear()

@router.message(and_f(StateFilter(UpdateUser.user), is_admin))
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

@router.message(and_f(StateFilter(RemoveLesson.code), is_admin))
async def handle_remove_lesson(message: types.Message, state: FSMContext):
    code = message.text.strip()
    if db.check_code(code):
        db.remove_lesson(code)
        await message.answer(f"{code} kodli dars o'chirildi!")
    else:
        await message.answer(f"{code} kodli dars topilmadi.")
    await state.clear()

@router.message(and_f(StateFilter(AddChannel.channel_url), is_admin))
async def handle_add_channel(message: types.Message):
    channels = [channel.strip() for channel in message.text.split(", ")]
    fixed_channels = [channel if channel.startswith("@") else f"@{channel}" for channel in channels]
    for channel in fixed_channels:
        db.add_channel(channel)
    await message.answer("Kanallar qo'shildi")
