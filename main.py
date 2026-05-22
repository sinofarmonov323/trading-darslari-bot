from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, CommandObject
import logging, asyncio
from config import BOT_TOKEN
from database import Database
from keyboards import send_channel_urls_button, main_menu
from admin import router
from aiogram.utils.deep_linking import create_start_link, decode_payload

dp = Dispatcher()

dp.include_router(router)

db = Database("database.db")

db.create_tables()

@dp.message(CommandStart())
async def start(message: types.Message, bot: Bot, command: CommandObject):
    unsubbed_channels = [channel for channel in db.get_channels() if "left" in await bot.get_chat_member(message.from_user.id, channel["channel_url"]).status]
    if unsubbed_channels:
        await message.answer("Botdan fodayalnish uchun kanallarga obuna bo'ling", reply_markup=send_channel_urls_button(unsubbed_channels))
    else:
        args = command.args
        if args:
            if message.from_user.id != int(args):
                db.add_points(message.from_user.username, 1)
        db.add_user(message.from_user.id, message.from_user.username, "oddiy")
        await message.answer(f"Salom {message.from_user.first_name}!\nTrading Darslari botiga xush kelibsiz", reply_markup=main_menu())

@dp.callback_query(F.data == "referal_link")
async def handle_callback(call: types.CallbackQuery, bot: Bot):
    link = await create_start_link(bot, str(call.from_user.id))
    await call.message.answer(f"Sizning referal linkingiz: {link}")

@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery, bot: Bot):
    unsubbed_channels = [channel for channel in db.get_channels() if "left" in await bot.get_chat_member(callback.from_user.id, channel["channel_url"]).status]
    if unsubbed_channels:
        await callback.message.answer("Botdan fodayalnish uchun kanallarga obuna bo'ling", reply_markup=send_channel_urls_button(unsubbed_channels))
    else:
        db.add_user(callback.from_user.id, callback.from_user.username, "oddiy")
        await callback.message.answer(f"Botdan foydalanishingiz mumkin", reply_markup=main_menu())

@dp.message(F.text.isdigit())
async def handle_digit(message: types.Message):
    course = db.get_course(int(message.text))
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
