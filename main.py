from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, CommandObject
import logging, asyncio
from config import BOT_TOKEN
from database import Database
from keyboards import send_channel_urls_button, main_menu
from admin import router
from aiogram.fsm.context import FSMContext
from aiogram.utils.deep_linking import create_start_link, decode_payload
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.exceptions import TelegramBadRequest

dp = Dispatcher()

dp.include_router(router)

db = Database("database.db")

async def get_subscription_statuses(bot: Bot, user_id: int) -> list[str]:
    try:
        statuses = []
        for channel in db.get_channels():
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            statuses.append(member.status)
        return statuses
    except:
        return False

@dp.message(CommandStart())
async def start(message: types.Message, bot: Bot, command: CommandObject):
    channel_urls = await get_subscription_statuses(bot, message.from_user.id)
    if "left" in channel_urls or "kicked" in channel_urls:
        await message.answer("Botdan fodayalnish uchun kanallarga obuna bo'ling", reply_markup=send_channel_urls_button(db.get_channels()))
    else:
        args = command.args
        if args:
            if message.from_user.id != int(args):
                db.add_points(message.from_user.username, 1)
        db.add_user(message.from_user.id, message.from_user.username, "oddiy")
        await message.answer(f"Salom {message.from_user.first_name}!\nDarsning kodini yuboring", reply_markup=main_menu())

@dp.callback_query(F.data.in_(["referal_link", "search_lesson"]))
async def handle_callback(call: types.CallbackQuery, bot: Bot):
    if call.data == "referal_link":
        link = await create_start_link(bot, str(call.from_user.id))
        await call.message.answer(f"Sizning referal linkingiz: {link}")
    elif call.data == "search_lesson":
        await call.message.answer("Bu funksiya hali mavjud emas")
    await call.answer()

@dp.callback_query(F.data == "check_sub")
async def check_subscription(call: types.CallbackQuery, bot: Bot):
    channel_urls = await get_subscription_statuses(bot, call.from_user.id)
    if "left" in channel_urls:
        await call.message.answer("Botdan fodayalnish uchun kanallarga obuna bo'ling", reply_markup=send_channel_urls_button(db.get_channels()))
    else:
        db.add_user(call.from_user.id, call.from_user.username, "oddiy")
        await call.message.answer(f"Botdan foydalanishingiz mumkin", reply_markup=main_menu())
    await call.answer()

@dp.message(F.text.isdigit())
async def handle_digit(message: types.Message, bot: Bot, state: FSMContext):
    state = await state.get_state()
    if state:
        raise SkipHandler()
    else:
        channel_urls = await get_subscription_statuses(bot, message.from_user.id)
        if "left" in channel_urls or "kicked" in channel_urls:
            await message.answer("Botdan fodayalnish uchun kanallarga obuna bo'ling", reply_markup=send_channel_urls_button(db.get_channels()))
        else:
            course = db.get_lesson(int(message.text))
            if course:
                await message.answer_video(course["video"], caption=course.get("name"))
            else:
                await message.answer("darsklik topilmadi")

async def main():
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
