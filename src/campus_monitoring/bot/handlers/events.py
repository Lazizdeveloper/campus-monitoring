from datetime import datetime, timedelta, timezone
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.api.exceptions import School21ApiError
from campus_monitoring.bot.utils.formatter import format_events, format_sales

router = Router(name="events_router")


@router.message(Command("sales"))
@router.message(F.text == "🏷 PRP/CRP Savdolari")
async def cmd_sales(message: Message, api_client: School21ApiClient) -> None:
    wait_msg = await message.answer("⏳ Peer-review savdolari holati tekshirilmoqda...")
    try:
        sales_res = await api_client.get_sales()
        text = format_sales(sales_res.sales)
        await wait_msg.edit_text(text, parse_mode="HTML")
    except School21ApiError as e:
        await wait_msg.edit_text(f"⚠️ API xatosi: {e.message}")
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(Command("events"))
@router.message(F.text == "📅 Tadbirlar")
async def cmd_events(message: Message, api_client: School21ApiClient) -> None:
    wait_msg = await message.answer("⏳ Tadbirlar ro'yxati yuklanmoqda...")
    now = datetime.now(timezone.utc)
    from_date = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    to_date = (now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        events_res = await api_client.get_events(from_date=from_date, to_date=to_date, limit=10)
        text = format_events(events_res.events)
        await wait_msg.edit_text(text, parse_mode="HTML")
    except School21ApiError as e:
        await wait_msg.edit_text(f"⚠️ API xatosi: {e.message}")
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xatolik yuz berdi: {e}")
