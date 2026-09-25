import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.config import settings
from campus_monitoring.services.subscriptions import subs_manager

logger = logging.getLogger(__name__)

class CampusMonitorService:
    def __init__(self, bot: Bot, api_client: School21ApiClient):
        self.bot = bot
        self.api_client = api_client
        self.scheduler = AsyncIOScheduler()
        self._last_workstations: Dict[str, Optional[str]] = {}
        self._last_events: set = set()

    def start(self) -> None:
        # Har 1 daqiqada talabalar joylashuvini tekshirish
        self.scheduler.add_job(
            self.check_tracked_logins_job,
            "interval",
            minutes=1,
            id="check_tracked_logins_job",
        )
        # Har 2 daqiqada peer-review tadbirlarini tekshirish
        self.scheduler.add_job(
            self.check_reviews_job,
            "interval",
            minutes=2,
            id="check_reviews_job",
        )
        self.scheduler.start()
        logger.info("Fon monitoring servisi ishga tushirildi.")

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Fon monitoring servisi to'xtatildi.")

    async def check_tracked_logins_job(self) -> None:
        try:
            tracked = subs_manager.get_all_tracked_logins()
            for login in tracked:
                subscribers = subs_manager.get_all_subscribers_for_login(login)
                if not subscribers:
                    continue
                
                ws_data = await self.api_client.get_participant_workstation(login)
                current_host = ws_data.host if ws_data else None
                
                prev_host = self._last_workstations.get(login)
                
                if current_host != prev_host:
                    if prev_host is None and current_host is not None:
                        msg = f"🚶‍♂️ <b>{login}</b> hozirgina kampusga kirdi va <b>{current_host}</b> kompyuteriga o'tirdi!"
                        await self._notify_users(subscribers, msg)
                    elif prev_host is not None and current_host is None:
                        msg = f"🏃‍♂️ <b>{login}</b> kampusdan chiqib ketdi (oxirgi joyi: <b>{prev_host}</b>)."
                        await self._notify_users(subscribers, msg)
                    elif prev_host is not None and current_host is not None:
                        msg = f"🔄 <b>{login}</b> joyini o'zgartirdi: <b>{prev_host}</b> ➡️ <b>{current_host}</b>"
                        await self._notify_users(subscribers, msg)
                        
                    self._last_workstations[login] = current_host
                    
                await asyncio.sleep(1) # API ni qiynamaslik uchun
        except Exception as e:
            logger.error(f"Error checking tracked logins: {e}")

    async def check_reviews_job(self) -> None:
        try:
            review_subscribers = subs_manager.get_all_review_subscribers()
            if not review_subscribers:
                return
                
            now = datetime.now()
            from_date = now.strftime("%Y-%m-%dT00:00:00.000Z")
            to_date = (now + timedelta(days=7)).strftime("%Y-%m-%dT23:59:59.000Z")
            
            events_data = await self.api_client.get_events(from_date=from_date, to_date=to_date)
            
            current_event_ids = set()
            new_events = []
            
            for event in events_data.events:
                if "peer" in event.name.lower() or "review" in event.name.lower() or "baho" in event.name.lower() or event.type == "PEER_REVIEW":
                    current_event_ids.add(event.id)
                    if event.id not in self._last_events:
                        new_events.append(event)
                        
            # Dastlabki ishga tushishda hamma narsani xabar qilmasligi uchun
            if not self._last_events:
                self._last_events = current_event_ids
                return
                
            for event in new_events:
                time_str = event.startDateTime.replace("T", " ")[:16] if event.startDateTime else "Noma'lum vaqt"
                msg = f"🔔 <b>YANGI PEER-REVIEW!</b>\n\n<b>{event.name}</b>\n⏰ Vaqti: {time_str}"
                await self._notify_users(review_subscribers, msg)
                
            self._last_events = current_event_ids
        except Exception as e:
            logger.error(f"Error checking peer reviews: {e}")

    async def _notify_users(self, chat_ids: List[str], text: str) -> None:
        for cid in chat_ids:
            try:
                await self.bot.send_message(chat_id=cid, text=text, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to send notification to {cid}: {e}")
