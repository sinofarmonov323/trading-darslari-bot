from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Referal havola", callback_data="referal_link"), InlineKeyboardButton(text="Dars qidirish", callback_data="search_lesson")],
        ]
    )

def send_channel_urls_button(channels: list[dict]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Obuna Bo'lish", url=channel.replace("@", "https://t.me/"))] for channel in channels
        ] + [
            [InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
        ]
    )

def admin_panel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika"), KeyboardButton(text="Darslar")],
            [KeyboardButton(text="Xabar yuborish")],
            [KeyboardButton(text="VIP Foydalanuvchilar"), KeyboardButton(text="PREMIUM Foydalanuvchilar")],
            [KeyboardButton(text="Adminlar"), KeyboardButton(text="Majburiy obuna qo'shish")]
        ]
    )

def vip_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="VIP foydalanuvchi qo'shish", callback_data="add_vip_user"), InlineKeyboardButton(text="VIP foydalanuvchi o'chirish", callback_data="remove_vip_user")],
        ]
    )

def admin_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Admin qo'shish", callback_data="add_admin"), InlineKeyboardButton(text="Admin o'chirish", callback_data="remove_admin")]
        ]
    )

def premium_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="PREMIUM foydalanuvchi qo'shish", callback_data="add_premium_user"), InlineKeyboardButton(text="PREMIUM foydalanuvchi o'chirish", callback_data="remove_premium_user")]
        ]
    )

def lesson_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Dars qo'shish", callback_data="add_lesson"), InlineKeyboardButton(text="Dars o'chirish", callback_data="remove_lesson")]
        ]
    )

def channels_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Kanallarni ko'rish", callback_data="view_channels"), InlineKeyboardButton(text="Kanal qo'shish", callback_data="add_channel"), InlineKeyboardButton(text="Kanallarni o'chirish", callback_data="remove_channels")],
        ]
    )
