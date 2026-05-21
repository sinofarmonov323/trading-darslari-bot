from aiogram import Router, types, F
from aiogram.filters import Command, and_f, StateFilter
from config import ADMIN_ID
from database import Database
from keyboards import admin_panel_keyboard
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

router = Router()
db = Database("database.db")

@router.message(and_f(Command("admin"), F.from_user.id == ADMIN_ID))
async def admin_panel(message: types.Message):
    await message.answer("Admin paneliga xush kelibsiz! Bu yerda siz botni boshqarishingiz mumkin.", reply_markup=admin_panel_keyboard())

@router.message(and_f(F.text == "Statistika", F.from_user.id == ADMIN_ID))
async def show_stats(message: types.Message):
    await message.answer(f"Foydalanuvchilar soni: {len(db.get_all_users())}\nDarslar soni: {len(db.get_courses())}")

@router.message(and_f(F.text == "Dars Qo'shish", F.from_user.id == ADMIN_ID))
async def add_course_panel(message: types.Message, state: FSMContext):
    await message.answer("Dars nomini kiriting")
    await state.set_state(AddCourseState.name)

@router.message(and_f(F.text == "Xabar yuborish", F.from_user.id == ADMIN_ID))
async def send_message_panel(message: types.Message, state: FSMContext):
    await message.answer("Yuboriladigan xabar matnini kiriting")
    await state.set_state(Broadcast.message)

@router.message(and_f(F.text == "VIP foydalanuvchilar", F.from_user.id == ADMIN_ID))
async def show_vip_users(message: types.Message):
    vip_users = db.get_vip_users()
    if vip_users:
        user_info = "\n".join([f"ID: {user['user_id']}, Username: {user['username']}" for user in vip_users])
        await message.answer(f"VIP foydalanuvchilar:\n{user_info}")
    else:
        await message.answer("VIP foydalanuvchilar yo'q.")

@router.message(and_f(StateFilter(Broadcast.message), F.from_user.id == ADMIN_ID))
async def broadcast_message(message: types.Message):
    users = db.get_oddiy_users()
    if message.content_type == "text":
        text = message.text
        for user in users:
            try:
                await router.bot.send_message(user['user_id'], text)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
    elif message.content_type == "photo":
        photo = message.photo[-1].file_id
        for user in users:
            try:
                await router.bot.send_photo(user['user_id'], photo, caption=message.caption)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
    await message.answer("Xabar barcha foydalanuvchilarga yuborildi!")

@router.message(and_f(StateFilter(AddCourseState.name), F.from_user.id == ADMIN_ID))
async def add_course_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Dars kodini kiriting")
    await state.set_state(AddCourseState.code)

@router.message(and_f(StateFilter(AddCourseState.code), F.from_user.id == ADMIN_ID))
async def add_course_code(message: types.Message, state: FSMContext):
    await state.update_data(code=message.text)
    await message.answer("Dars video linkini kiriting")
    await state.set_state(AddCourseState.video)

@router.message(and_f(StateFilter(AddCourseState.video), F.from_user.id == ADMIN_ID, F.video))
async def add_course_video(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    code = data.get("code")
    video = message.video.file_id
    db.add_course(name, code, video)
    await message.answer("Dars muvaffaqiyatli qo'shildi!")
    await state.clear()

@router.callback_query(and_f(F.data == "add_vip_user", F.from_user.id == ADMIN_ID))
async def add_vip_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("VIP foydalanuvchi usernamesini kiriting")
    await state.set_state(UpdateUser.user)

@router.message(and_f(StateFilter(UpdateUser.user), F.from_user.id == ADMIN_ID))
async def handle_vip_user(message: types.Message):
    if "@" not in message.text:
        message.text = "@" + message.text
    
    if db.get_user(username=message.text):
        db.promote_user("vip", message.text)
        await message.answer(f"Foydalanuvchi {message.text} VIP qilindi!")
    else:
        await message.answer("Bunday foydalanuvchi topilmadi.")

@router.callback_query(and_f(F.data == "remove_vip_user", F.from_user.id == ADMIN_ID))
async def remove_vip_user(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("VIP foydalanuvchi usernamesini kiriting")
    await state.set_state(UpdateUser.user)

@router.message(and_f(StateFilter(UpdateUser.user), F.from_user.id == ADMIN_ID))
async def handle_remove_vip_user(message: types.Message):
    if "@" not in message.text:
        message.text = "@" + message.text
    
    if db.get_user(username=message.text):
        db.demote_user("oddiy", message.text)
        await message.answer(f"Foydalanuvchi {message.text} VIP dan chiqarildi!")
    else:
        await message.answer("Bunday foydalanuvchi topilmadi.")
