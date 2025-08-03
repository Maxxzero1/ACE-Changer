from permissions import can_manage_settings
from typing import List, Dict
import json

SCHEDULE_FILE = 'schedules.json'
MESSAGES_FILE = 'messages.json'

def _load_json_data(file_path: str) -> Dict:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if all(key.lstrip('-').isdigit() for key in data.keys()):
                return {int(k): v for k, v in data.items()}

            return data

    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def _save_schedules(data: Dict):
    with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

messages = _load_json_data(MESSAGES_FILE)
scheduleConfig = _load_json_data(SCHEDULE_FILE)


def update_schedule(chat_id: int, user_id: int, hours: List[int]) -> str:
    if not can_manage_settings(user_id, chat_id):
        return messages.get("no_permission", "شما اجازه انجام این کار را ندارید.")

    if not all(isinstance(h, int) and 0 <= h < 24 for h in hours):
        return messages.get("invalid_hours", "ساعات وارد شده معتبر نیستند. لطفاً از اعداد 0 تا 23 استفاده کنید.")

    if len(hours) > 24:
        return messages.get("too_many_hours", "تعداد ساعات وارد شده بیش از حد مجاز است.")

    unique_sorted_hours = sorted(list(set(hours)))
    scheduleConfig[chat_id] = unique_sorted_hours
    _save_schedules(scheduleConfig)
    return messages.get("success_update", "زمان‌بندی با موفقیت به‌روز شد: {}").format(unique_sorted_hours)

def should_announce_now(chat_id: int, current_hour: int) -> bool:
    return current_hour in scheduleConfig.get(chat_id, [])
