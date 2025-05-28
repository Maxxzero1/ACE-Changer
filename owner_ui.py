# owner_ui.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# تعریف JSON منوها به صورت دیکشنری پایتون (مثلاً از فایل یا دیتا بیس هم می‌تونی بیاری)
owner_ui_json = {
    "get_owner_main_menu": {
        "row_width": 2,
        "buttons": [
            {"text": "مدیریت ادمین‌ها 👮‍♂️", "callback_data": "owner_manage_admins"},
            {"text": "بن/آزادسازی کاربران 🚫", "callback_data": "owner_manage_ban"},
            {"text": "مشاهده گروه‌ها و کانال‌ها 📡", "callback_data": "owner_view_groups"},
            {"text": "بازگشت ⬅️", "callback_data": "owner_back"},
        ]
    },
    "get_admin_management_menu": {
        "row_width": 1,
        "buttons": [
            {"text": "افزودن ادمین ➕", "callback_data": "add_admin"},
            {"text": "حذف ادمین ➖", "callback_data": "remove_admin"},
            {"text": "بازگشت 🔙", "callback_data": "owner_main"},
        ]
    },
    "get_ban_menu": {
        "row_width": 1,
        "buttons": [
            {"text": "بن کردن کاربر 🚫", "callback_data": "ban_user"},
            {"text": "آزادسازی کاربر ✅", "callback_data": "unban_user"},
            {"text": "بازگشت 🔙", "callback_data": "owner_main"},
        ]
    }
}

def create_menu_from_json(menu_key, dynamic_list=None):
    menu_data = owner_ui_json.get(menu_key)
    if not menu_data:
        return InlineKeyboardMarkup()
    
    keyboard = InlineKeyboardMarkup(row_width=menu_data["row_width"])
    
    for btn in menu_data["buttons"]:
        keyboard.add(InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]))
    
    # اگه منوی لیست گروه‌ها هست و داینامیک است
    if menu_key == "get_group_list_menu" and dynamic_list:
        for group_id, group_name in dynamic_list.items():
            keyboard.add(InlineKeyboardButton(group_name, callback_data=f"view_group_{group_id}"))
        keyboard.add(InlineKeyboardButton("بازگشت 🔙", callback_data="owner_main"))
    
    return keyboard

# استفاده توی کد:
# main_menu_keyboard = create_menu_from_json("get_owner_main_menu")
# admin_menu_keyboard = create_menu_from_json("get_admin_management_menu")
# ban_menu_keyboard = create_menu_from_json("get_ban_menu")
# group_list_keyboard = create_menu_from_json("get_group_list_menu", dynamic_list={"123": "گروه 1", "456": "کانال 2"})