from typing import Set, List, Dict, Union
import redis

class CacheManager:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=db, decode_responses=True)

    def _update_set(self, key: str, item_ids: Union[List, Set]):
        pipe = self.redis.pipeline()
        pipe.delete(key)
        if item_ids:
            pipe.sadd(key, *item_ids)

        pipe.execute()

    def set_owner_list(self, owner_ids: Union[List, Set]):
        self._update_set('owner_list', owner_ids)

    def get_owner_list(self) -> Set[str]:
        return self.redis.smembers('owner_list')

    def set_admins(self, chat_id: int, admin_ids: Union[List, Set]):
        self._update_set(f"admins:{chat_id}", admin_ids)

    def get_admins(self, chat_id: int) -> Set[str]:
        return self.redis.smembers(f"admins:{chat_id}")

    def set_banned_users(self, user_ids: Union[List, Set]):
        self._update_set('banned_users', user_ids)

    def get_banned_users(self) -> Set[str]:
        return self.redis.smembers('banned_users')

    def set_chat_settings(self, chat_id: int, settings_dict: Dict):
        key = f"chat_settings:{chat_id}"
        if settings_dict:
            self.redis.hset(key, mapping=settings_dict)

    def get_chat_settings(self, chat_id: int) -> Dict:
        return self.redis.hgetall(f"chat_settings:{chat_id}")

    def delete_chat_cache(self, chat_id: int):
        pipe = self.redis.pipeline()
        pipe.delete(f"admins:{chat_id}")
        pipe.delete(f"chat_settings:{chat_id}")
        pipe.execute()
