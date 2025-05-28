# permissions.py

# لیست مالک‌ها (فقط دستی قابل تغییره)
MasterList = {
    # user_id: "name"
    # مثال:
    # 123456789: "Abtin",
}

# لیست اونرها: مشخص برای هر گروه یا کانال
OwnerList = {
    # group_id: [user_id1, user_id2, ...]
    # مثال:
    # -100111222333: [111, 222],
}

# لیست ادمین‌ها: مشخص برای هر گروه یا کانال
AdminList = {
    # group_id: [user_id1, user_id2, ...]
    # مثال:
    # -100111222333: [333, 444],
}


# نقش کاربر رو مشخص می‌کنه
def get_user_role(user_id: int, chat_id: int) -> str:
    if user_id in MasterList:
        return "master"
    elif chat_id in OwnerList and user_id in OwnerList[chat_id]:
        return "owner"
    elif chat_id in AdminList and user_id in AdminList[chat_id]:
        return "admin"
    else:
        return "user"


# چک می‌کنه که آیا این یارو اجازه انجام کاری داره یا نه
def can_manage_settings(user_id: int, chat_id: int) -> bool:
    role = get_user_role(user_id, chat_id)
    return role in ["owner", "master"]


def can_announce_prices(user_id: int, chat_id: int) -> bool:
    role = get_user_role(user_id, chat_id)
    return role in ["admin", "owner", "master"]


def can_request_prices(user_id: int, chat_id: int, only_admin_can_request: bool) -> bool:
    role = get_user_role(user_id, chat_id)
    if only_admin_can_request:
        return role in ["admin", "owner", "master"]
    else:
        return True


# فقط مستر بتونه ببینه عضو کجاها هستیم
def is_master(user_id: int) -> bool:
    return user_id in MasterList


# برای اضافه کردن Owner جدید به گروه خاص
def add_owner(chat_id: int, user_id: int):
    OwnerList.setdefault(chat_id, [])
    if user_id not in OwnerList[chat_id]:
        OwnerList[chat_id].append(user_id)


# برای اضافه کردن Admin جدید به گروه خاص
def add_admin(chat_id: int, user_id: int):
    AdminList.setdefault(chat_id, [])
    if user_id not in AdminList[chat_id]:
        AdminList[chat_id].append(user_id)