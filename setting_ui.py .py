# setting_ui.py
import json

# بارگذاری پیام‌ها
with open("messages.json", "r", encoding="utf-8") as f:
    messages = json.load(f)

buttons = messages["setting_ui"]["buttons"]

def get_admin_settings_menu():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(buttons["change_schedule"], callback_data="change_schedule"),
        InlineKeyboardButton(buttons["change_request_access"], callback_data="change_request_access"),
        InlineKeyboardButton(buttons["view_schedule"], callback_data="view_schedule"),
        InlineKeyboardButton(buttons["back_to_main"], callback_data="back_to_main"),
    )
    return keyboard


def get_request_access_menu(current_mode):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(
            buttons["access_admins"] + (" ✅" if current_mode == "admins" else ""),
            callback_data="access_admins",
        ),
        InlineKeyboardButton(
            buttons["access_everyone"] + (" ✅" if current_mode == "everyone" else ""),
            callback_data="access_everyone",
        ),
        InlineKeyboardButton(buttons["back_to_settings"], callback_data="back_to_settings"),
    )
    return keyboard


def get_time_selector_menu(times_list):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(row_width=2)
    for t in times_list:
        keyboard.insert(
            InlineKeyboardButton(buttons["time_prefix"] + str(t), callback_data=f"toggle_time_{t}")
        )
    keyboard.add(
        InlineKeyboardButton(buttons["save_schedule"], callback_data="save_schedule"),
        InlineKeyboardButton(buttons["back_to_settings"], callback_data="back_to_settings"),
    )
    return keyboard


def get_back_button():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(buttons["back_to_settings"], callback_data="back_to_settings")
    )