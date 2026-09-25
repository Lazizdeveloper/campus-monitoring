import asyncio
import logging
from typing import Dict, List, Optional
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.bot.utils.formatter import format_sales
from campus_monitoring.config import settings

logger = logging.getLogger(__name__)


class CampusMonitorService:
    def __init__(self, bot: Bot, api_client: School21ApiClient):
        self.bot = bot
        self.api_client = api_client
        self.scheduler = AsyncIOScheduler()
        self._last_sales_status: Dict[str, str] = {}

    def start(self) -> None:
        if not settings.admin_ids:
            logger.info("ADMIN_IDS bo'sh bo'lgani sababli fon monitoring xabarnomalari o'chirilgan.")

        self.scheduler.add_job(
            self.check_sales_job,
            "interval",
            minutes=settings.check_sales_interval_minutes,
            id="check_sales_job",
        )
        self.scheduler.start()
        logger.info("Fon monitoring servisi ishga tushirildi.")

    def stop(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Fon monitoring servisi to'xtatildi.")

    async def notify_admins(self, text: str) -> None:
        for admin_id in settings.admin_ids:
            try:
                await self.bot.send_message(chat_id=admin_id, text=text, parse_mode="HTML")
            except Exception as e:
                logger.error(f"Failed to send notification to admin {admin_id}: {e}")

    async def check_sales_job(self) -> None:
        try:
            sales_res = await self.api_client.get_sales()
            if not sales_res.sales:
                return

            notify = False
            for sale in sales_res.sales:
                prev_status = self._last_sales_status.get(sale.type)
                if prev_status and prev_status != sale.status and sale.status in ("ACTIVE", "PLANNED"):
                    notify = True
                self._last_sales_status[sale.type] = sale.status

            if notify:
                msg = f"🔔 <b>DIQQAT! Peer-review savdolarida o'zgarish:</b>\n\n{format_sales(sales_res.sales)}"
                await self.notify_admins(msg)
        except Exception as e:
            logger.error(f"Error checking sales in background job: {e}")
