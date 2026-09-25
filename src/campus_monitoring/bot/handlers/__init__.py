from campus_monitoring.bot.handlers.campus import router as campus_router
from campus_monitoring.bot.handlers.common import router as common_router
from campus_monitoring.bot.handlers.events import router as events_router
from campus_monitoring.bot.handlers.participant import router as participant_router

__all__ = [
    "common_router",
    "participant_router",
    "campus_router",
    "events_router",
]
