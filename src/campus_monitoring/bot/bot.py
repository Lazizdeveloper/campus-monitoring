import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.bot.handlers import (
    campus_router,
    common_router,
    events_router,
    participant_router,
)
from campus_monitoring.bot.middlewares import ApiClientMiddleware
from campus_monitoring.config import settings

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    return Bot(token=settings.bot_token)


def create_dispatcher(api_client: School21ApiClient) -> Dispatcher:
    dp = Dispatcher()

    # Register middleware
    api_middleware = ApiClientMiddleware(api_client)
    dp.message.middleware(api_middleware)
    dp.callback_query.middleware(api_middleware)

    # Include routers
    dp.include_router(common_router)
    dp.include_router(participant_router)
    dp.include_router(campus_router)
    dp.include_router(events_router)

    return dp


async def setup_bot_commands(bot: Bot) -> None:
    commands = [
        BotCommand(command="user", description="Talaba profili va ma'lumotlari"),
        BotCommand(command="where", description="Talabaning joriy ish o'rni"),
        BotCommand(command="clusters", description="Klasterlar va bo'sh o'rinlar"),
        BotCommand(command="map", description="Klaster bandlik xaritasi"),
        BotCommand(command="sales", description="PRP/CRP savdolari holati"),
        BotCommand(command="events", description="Kampus tadbirlari va imtihonlar"),
        BotCommand(command="campuses", description="Barcha kampuslar ro'yxati"),
        BotCommand(command="help", description="Yordam va qo'llanma"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning(f"Could not set bot commands: {e}")
