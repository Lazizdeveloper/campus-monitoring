import asyncio
import logging
import sys

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.bot.bot import create_bot, create_dispatcher, setup_bot_commands
from campus_monitoring.config import settings
from campus_monitoring.services.monitor import CampusMonitorService
from campus_monitoring.services.auth import School21Authenticator, update_env_token

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def async_main() -> None:
    if not settings.bot_token or settings.bot_token.startswith("123456789:"):
        logger.error(
            "BOT_TOKEN belgilanmagan! Iltimos, .env faylida o'z Telegram Bot Tokeningizni ko'rsating."
        )
        sys.exit(1)

    logger.info("School 21 Campus Monitoring boti ishga tushirilmoqda...")

    authenticator = School21Authenticator(
        login=settings.school21_login,
        password=settings.school21_password,
    )

    async def auth_callback() -> str:
        new_token = await authenticator.get_token()
        if new_token:
            update_env_token(new_token)
            settings.school21_token = new_token
        return new_token

    api_client = School21ApiClient(
        base_url=settings.school21_api_url,
        token=settings.school21_token,
        auth_callback=auth_callback
    )

    bot = create_bot()
    dp = create_dispatcher(api_client)

    await setup_bot_commands(bot)

    monitor = CampusMonitorService(bot=bot, api_client=api_client)
    monitor.start()

    try:
        logger.info("Bot polling rejimi boshlandi.")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        logger.info("Bot to'xtatilmoqda...")
        monitor.stop()
        await api_client.close()
        await bot.session.close()
        logger.info("Barcha resurslar to'xtatildi.")


def main() -> None:
    try:
        asyncio.run(async_main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")


if __name__ == "__main__":
    main()
