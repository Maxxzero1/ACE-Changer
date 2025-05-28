# schedule.py
from datetime import datetime
import json
from typing import List

# دیکشنری زمان‌بندی: key = chatId, value = list of allowed hours (int: 0-23)
scheduleConfig = {}

# لیست مالک‌ها: key = userId, value = name
ownerList = {
    # مثلا: 123456789: "Abtin"
}

# لیست ادمین‌ها: key = chatId, value = list of admin userIds
adminList = {
    # مثلا: -1001122334455: [111, 222, 333]
}

# بارگذاری پیام‌ها از فایل JSON
def load_messages(file_path='messages.json') -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

messages = load_messages()

def canManageSchedule(userId: int, chatId: int) -> bool:
    """بررسی می‌کنه که آیا این کاربر اجازه تغییر زمان‌بندی در این چت رو داره یا نه"""
    return userId in ownerList or (chatId in adminList and userId in adminList[chatId])

def updateSchedule(chatId: int, userId: int, hours: List[int]) -> str:
    """تنظیم زمان‌بندی جدید توسط ادمین یا مالک"""
    if not canManageSchedule(userId, chatId):
        return messages["no_permission"]

    if not all(isinstance(h, int) and 0 <= h < 24 for h in hours):
        return messages["invalid_hours"]

    if len(hours) > 24:
        return messages["too_many_hours"]

    scheduleConfig[chatId] = sorted(list(set(hours)))  # حذف تکراری‌ها و مرتب‌سازی
    return messages["success_update"].format(scheduleConfig[chatId])

def shouldAnnounceNow(chatId: int, currentHour: int) -> bool:
    """بررسی کنه الان طبق برنامه اجازه ارسال داریم یا نه"""
    return currentHour in scheduleConfig.get(chatId, [])

# 📦 تست دستی:
if __name__ == "__main__":
    testChatId = -1001234567890
    testUserId = 111
    ownerList[999] = "BossMan"
    adminList[testChatId] = [111, 222]

    # تست تغییر توسط ادمین
    print(updateSchedule(testChatId, 111, [9, 12, 15, 18]))  # ✅

    # تست تغییر توسط کاربر معمولی
    print(updateSchedule(testChatId, 555, [10, 20]))  # ❌

    # تست تغییر توسط مالک
    print(updateSchedule(testChatId, 999, list(range(24))))  # ✅

    # تست اجازه اعلان در ساعت فعلی
    currentHour = datetime.now().hour
    print(f"در ساعت {currentHour} باید اعلان انجام بشه؟", shouldAnnounceNow(testChatId, currentHour))