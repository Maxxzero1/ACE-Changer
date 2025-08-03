import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def load_menus(file_path="owner_ui.json"):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading menu file: {e}")

owner_ui_data = load_menus()

def create_menu_from_json(menu_key, dynamic_list=None):
    menu_data = owner_ui_data.get(menu_key)
    if not menu_data:
        return InlineKeyboardMarkup()
    
    keyboard = InlineKeyboardMarkup(row_width=menu_data["row_width"])    
    for btn in menu_data["buttons"]:
        keyboard.add(InlineKeyboardButton(btn["text"], callback_data=btn["callback_data"]))
    
    if menu_key == "get_group_list_menu" and dynamic_list:
        for group_id, group_name in dynamic_list.items():
            keyboard.add(InlineKeyboardButton(group_name, callback_data=f"view_group_{group_id}"))
        keyboard.add(InlineKeyboardButton("بازگشت 🔙", callback_data="owner_main"))
    
    return keyboard
