from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Referal havola", callback_data="referal_link"), InlineKeyboardButton(text="tugma 2", callback_data="button_2")],
            [InlineKeyboardButton(text="tugma 3", callback_data="button_3"), InlineKeyboardButton(text="tugma 4", callback_data="button_4")],
        ]
    )

def send_channel_urls_button(channels: list[dict]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Obuna Bo'lish", url=channel['channel_url'])] for channel in channels
        ] + [
            [InlineKeyboardButton(text="Tekshirish", callback_data="check_sub")]
        ]
    )

def admin_panel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Statistika"), KeyboardButton(text="Dars Qo'shish")],
            [KeyboardButton(text="Xabar yuborish")],
            [KeyboardButton(text="VIP Foydalanuvchilar"), KeyboardButton(text="PREMIUM Foydalanuvchilar")],
            [KeyboardButton(text="Adminlar")]
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
            [InlineKeyboardButton(text="Admin qo'shish", callback_data="add_admin"), InlineKeyboardButton(text="Admin o'chirish", callback_data="remove_admin"), InlineKeyboardButton(text="Adminlarni ko'rish", callback_data="view_admins")]
        ]
    )

def premium_user_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="PREMIUM foydalanuvchi qo'shish", callback_data="add_premium_user"), InlineKeyboardButton(text="PREMIUM foydalanuvchi o'chirish", callback_data="remove_premium_user")]
        ]
    )
