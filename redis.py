# redis.py
import redis
import json

class CacheManager:
    def __init__(self, redis_host='localhost', redis_port=6379, db=0):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    # کش لیست مالک‌ها
    def set_owner_list(self, owner_ids):
        self.redis.sadd('owner_list', *owner_ids)

    def get_owner_list(self):
        return self.redis.smembers('owner_list')

    # کش ادمین‌ها per chat
    def set_admins(self, chat_id, admin_ids):
        key = f"admins:{chat_id}"
        self.redis.delete(key)
        if admin_ids:
            self.redis.sadd(key, *admin_ids)

    def get_admins(self, chat_id):
        key = f"admins:{chat_id}"
        return self.redis.smembers(key)

    # کش لیست بن شده‌ها
    def set_banned_users(self, user_ids):
        self.redis.delete('banned_users')
        if user_ids:
            self.redis.sadd('banned_users', *user_ids)

    def get_banned_users(self):
        return self.redis.smembers('banned_users')

    # کش تنظیمات چت (hash map)
    def set_chat_settings(self, chat_id, settings_dict):
        key = f"chat_settings:{chat_id}"
        self.redis.hmset(key, settings_dict)

    def get_chat_settings(self, chat_id):
        key = f"chat_settings:{chat_id}"
        return self.redis.hgetall(key)

    # پاک کردن کش یک چت (برای invalidate)
    def delete_chat_settings(self, chat_id):
        key = f"chat_settings:{chat_id}"
        self.redis.delete(key)

# نمونه استفاده
if __name__ == "__main__":
    cache = CacheManager()

    cache.set_owner_list([12345, 67890])
    print("Owners:", cache.get_owner_list())

    cache.set_admins(1111, [111, 222, 333])
    print("Admins in chat 1111:", cache.get_admins(1111))

    cache.set_banned_users([555, 666])
    print("Banned users:", cache.get_banned_users())

    cache.set_chat_settings(1111, {'allow_price_requests': 'True', 'price_announcement_interval_minutes': '60'})
    print("Chat 1111 settings:", cache.get_chat_settings(1111))