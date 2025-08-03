import json
import sqlite3

SUPERUSERS_FILE = 'superusers.json'
ADMINS_DB = 'permissions.db'

def _init_admin_db():
    with sqlite3.connect(ADMINS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                PRIMARY KEY (chat_id, user_id)
            )
        ''')
        conn.commit()

def is_admin_in_db(chat_id: int, user_id: int) -> bool:
    with sqlite3.connect(ADMINS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT EXISTS(SELECT 1 FROM admins WHERE chat_id = ? AND user_id = ?)", (chat_id, user_id))
        return cursor.fetchone()[0] == 1

def add_admin_to_db(chat_id: int, user_id: int):
    with sqlite3.connect(ADMINS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO admins (chat_id, user_id) VALUES (?, ?)", (chat_id, user_id))
        conn.commit()

def remove_admin_from_db(chat_id: int, user_id: int):
    with sqlite3.connect(ADMINS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM admins WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        conn.commit()

def _load_superusers():
    try:
        with open(SUPERUSERS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            masters = {int(k): v for k, v in data.get("masters", {}).items()}
            owners = {int(k): v for k, v in data.get("owners", {}).items()}
            return masters, owners

    except (FileNotFoundError, json.JSONDecodeError):
        return {}, {}

def _save_superusers(masters, owners):
    with open(SUPERUSERS_FILE, 'w', encoding='utf-8') as f:
        data = {"masters": masters, "owners": owners}
        json.dump(data, f, indent=4)

_init_admin_db()
MasterList, OwnerList = _load_superusers()

def get_user_role(user_id: int, chat_id: int) -> str:
    if user_id in MasterList:
        return "master"
    
    if chat_id in OwnerList and user_id in OwnerList.get(chat_id, []):
        return "owner"
    
    if is_admin_in_db(chat_id, user_id):
        return "admin"

    return "user"

def can_manage_settings(user_id: int, chat_id: int) -> bool:
    return get_user_role(user_id, chat_id) in ["owner", "master"]

def can_announce_prices(user_id: int, chat_id: int) -> bool:
    return get_user_role(user_id, chat_id) in ["admin", "owner", "master"]

def is_master(user_id: int) -> bool:
    return user_id in MasterList

def add_owner(chat_id: int, user_id: int):
    OwnerList.setdefault(chat_id, [])
    if user_id not in OwnerList[chat_id]:
        OwnerList[chat_id].append(user_id)
        _save_superusers(MasterList, OwnerList) # ذخیره در JSON

def remove_owner(chat_id: int, user_id: int):
    if chat_id in OwnerList and user_id in OwnerList[chat_id]:
        OwnerList[chat_id].remove(user_id)
        if not OwnerList[chat_id]:
            del OwnerList[chat_id]

        _save_superusers(MasterList, OwnerList) # ذخیره در JSON

def add_admin(chat_id: int, user_id: int):
    add_admin_to_db(chat_id, user_id) # ذخیره در SQLite

def remove_admin(chat_id: int, user_id: int):
    remove_admin_from_db(chat_id, user_id) # حذف از SQLite
