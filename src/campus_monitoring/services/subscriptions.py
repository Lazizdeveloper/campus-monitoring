import json
import os
import logging
from typing import Dict, List, Set
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

SUBSCRIPTIONS_FILE = "subscriptions.json"

class UserSubscription(BaseModel):
    track_logins: List[str] = Field(default_factory=list)
    notify_reviews: bool = False

class SubscriptionManager:
    def __init__(self):
        self.subs: Dict[str, UserSubscription] = {}
        self.load()

    def load(self):
        if os.path.exists(SUBSCRIPTIONS_FILE):
            try:
                with open(SUBSCRIPTIONS_FILE, "r") as f:
                    data = json.load(f)
                    self.subs = {k: UserSubscription(**v) for k, v in data.items()}
            except Exception as e:
                logger.error(f"Xatolik subscriptions.json o'qishda: {e}")

    def save(self):
        try:
            with open(SUBSCRIPTIONS_FILE, "w") as f:
                json.dump({k: v.model_dump() for k, v in self.subs.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Xatolik subscriptions.json yozishda: {e}")

    def get_user_sub(self, chat_id: int) -> UserSubscription:
        cid = str(chat_id)
        if cid not in self.subs:
            self.subs[cid] = UserSubscription()
        return self.subs[cid]

    def add_track(self, chat_id: int, login: str):
        sub = self.get_user_sub(chat_id)
        if login not in sub.track_logins:
            sub.track_logins.append(login)
            self.save()

    def remove_track(self, chat_id: int, login: str):
        sub = self.get_user_sub(chat_id)
        if login in sub.track_logins:
            sub.track_logins.remove(login)
            self.save()

    def set_reviews(self, chat_id: int, enable: bool):
        sub = self.get_user_sub(chat_id)
        sub.notify_reviews = enable
        self.save()

    def get_all_subscribers_for_login(self, login: str) -> List[str]:
        return [cid for cid, sub in self.subs.items() if login in sub.track_logins]

    def get_all_review_subscribers(self) -> List[str]:
        return [cid for cid, sub in self.subs.items() if sub.notify_reviews]

    def get_all_tracked_logins(self) -> Set[str]:
        logins = set()
        for sub in self.subs.values():
            for login in sub.track_logins:
                logins.add(login)
        return logins

subs_manager = SubscriptionManager()
