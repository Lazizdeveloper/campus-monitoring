import logging
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.api.exceptions import NotFoundError, School21ApiError, UnauthorizedError
from campus_monitoring.bot.keyboards.common import (
    get_main_keyboard,
    get_participant_inline_keyboard,
)
from campus_monitoring.bot.utils.formatter import (
    format_participant_profile,
    format_participant_projects,
    format_participant_skills,
    format_workstation,
)

logger = logging.getLogger(__name__)
router = Router(name="participant_router")


class ParticipantSearchStates(StatesGroup):
    waiting_for_profile_login = State()
    waiting_for_where_login = State()


# Helper to fetch full participant profile
async def fetch_and_render_profile(api: School21ApiClient, login: str) -> tuple[str, str]:
    participant = await api.get_participant(login)
    workstation = await api.get_participant_workstation(login)
    coalition = await api.get_participant_coalition(login)
    points = None
    try:
        points = await api.get_participant_points(login)
    except Exception as e:
        logger.debug(f"Failed to fetch points for {login}: {e}")

    logtime = None
    try:
        logtime = await api.get_participant_logtime(login)
    except Exception as e:
        logger.debug(f"Failed to fetch logtime for {login}: {e}")

    text = format_participant_profile(
        p=participant,
        ws=workstation,
        coalition=coalition,
        points=points,
        logtime=logtime,
    )
    return text, participant.login


@router.message(F.text == "👤 Talaba qidirish")
async def btn_search_participant(message: Message, state: FSMContext) -> None:
    await state.set_state(ParticipantSearchStates.waiting_for_profile_login)
    await message.answer(
        "🔎 Talabaning loginini kiriting (masalan: <code>bibikov-lukyan</code>):",
        parse_mode="HTML",
    )


@router.message(F.text == "🖥 Qayerda o'tiribdi?")
async def btn_where_participant(message: Message, state: FSMContext) -> None:
    await state.set_state(ParticipantSearchStates.waiting_for_where_login)
    await message.answer(
        "🔎 Ish o'rnini bilmoqchi bo'lgan talaba loginini kiriting:",
        parse_mode="HTML",
    )


@router.message(ParticipantSearchStates.waiting_for_profile_login)
async def process_profile_login(message: Message, state: FSMContext, api_client: School21ApiClient) -> None:
    await state.clear()
    login = message.text.strip()
    await show_user_profile(message, login, api_client)


@router.message(ParticipantSearchStates.waiting_for_where_login)
async def process_where_login(message: Message, state: FSMContext, api_client: School21ApiClient) -> None:
    await state.clear()
    login = message.text.strip()
    await show_user_workstation(message, login, api_client)


@router.message(Command("user"))
@router.message(Command("whois"))
async def cmd_user(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Login ko'rsatilmadi.\nNamuna: <code>/user bibikov-lukyan</code>",
            parse_mode="HTML",
        )
        return
    login = args[1].strip()
    await show_user_profile(message, login, api_client)


@router.message(Command("where"))
async def cmd_where(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Login ko'rsatilmadi.\nNamuna: <code>/where bibikov-lukyan</code>",
            parse_mode="HTML",
        )
        return
    login = args[1].strip()
    await show_user_workstation(message, login, api_client)


@router.message(Command("logtime"))
async def cmd_logtime(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Login ko'rsatilmadi.\nNamuna: <code>/logtime bibikov-lukyan</code>",
            parse_mode="HTML",
        )
        return
    login = args[1].strip()
    try:
        avg_hours = await api_client.get_participant_logtime(login)
        await message.answer(
            f"⏱ <b>{login}</b> uchun haftalik o'rtacha logtime: <b>{avg_hours:.2f}</b> soat/kun",
            parse_mode="HTML",
        )
    except NotFoundError:
        await message.answer(f"❌ <code>{login}</code> loginli talaba topilmadi.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(Command("projects"))
async def cmd_projects(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Login ko'rsatilmadi.\nNamuna: <code>/projects bibikov-lukyan</code>",
            parse_mode="HTML",
        )
        return
    login = args[1].strip()
    try:
        res = await api_client.get_participant_projects(login, limit=15)
        text = format_participant_projects(login, res.projects)
        await message.answer(text, parse_mode="HTML")
    except NotFoundError:
        await message.answer(f"❌ <code>{login}</code> loginli talaba topilmadi.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")


@router.message(Command("skills"))
async def cmd_skills(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Login ko'rsatilmadi.\nNamuna: <code>/skills bibikov-lukyan</code>",
            parse_mode="HTML",
        )
        return
    login = args[1].strip()
    try:
        res = await api_client.get_participant_skills(login)
        text = format_participant_skills(login, res.skills)
        await message.answer(text, parse_mode="HTML")
    except NotFoundError:
        await message.answer(f"❌ <code>{login}</code> loginli talaba topilmadi.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")


async def show_user_profile(message: Message, login: str, api: School21ApiClient) -> None:
    wait_msg = await message.answer(f"⏳ <code>{login}</code> ma'lumotlari yuklanmoqda...", parse_mode="HTML")
    try:
        text, valid_login = await fetch_and_render_profile(api, login)
        await wait_msg.edit_text(
            text,
            reply_markup=get_participant_inline_keyboard(valid_login),
            parse_mode="HTML",
        )
    except NotFoundError:
        await wait_msg.edit_text(f"❌ <code>{login}</code> loginli talaba topilmadi.", parse_mode="HTML")
    except UnauthorizedError:
        await wait_msg.edit_text("🔒 School 21 API tokeni noto'g'ri yoki muddati tugagan.")
    except School21ApiError as e:
        await wait_msg.edit_text(f"⚠️ API xatoligi: {e.message}")
    except Exception as e:
        logger.exception("Unexpected error in show_user_profile")
        await wait_msg.edit_text(f"⚠️ Kutilmagan xatolik yuz berdi: {e}")


async def show_user_workstation(message: Message, login: str, api: School21ApiClient) -> None:
    try:
        ws = await api.get_participant_workstation(login)
        text = format_workstation(login, ws)
        await message.answer(text, parse_mode="HTML")
    except NotFoundError:
        await message.answer(f"❌ <code>{login}</code> loginli talaba topilmadi.", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")


# --- Callback Queries ---
@router.callback_query(F.data.startswith("user:"))
async def handle_user_callback(callback: CallbackQuery, api_client: School21ApiClient) -> None:
    parts = callback.data.split(":")
    if len(parts) < 3:
        await callback.answer("Noto'g'ri so'rov")
        return

    action = parts[1]
    login = parts[2]

    try:
        if action == "ws":
            ws = await api_client.get_participant_workstation(login)
            text = format_workstation(login, ws)
            await callback.message.reply(text, parse_mode="HTML")
            await callback.answer()
        elif action == "proj":
            res = await api_client.get_participant_projects(login, limit=15)
            text = format_participant_projects(login, res.projects)
            await callback.message.reply(text, parse_mode="HTML")
            await callback.answer()
        elif action == "skills":
            res = await api_client.get_participant_skills(login)
            text = format_participant_skills(login, res.skills)
            await callback.message.reply(text, parse_mode="HTML")
            await callback.answer()
        elif action == "logtime":
            avg = await api_client.get_participant_logtime(login)
            await callback.message.reply(
                f"⏱ <b>{login}</b> uchun haftalik o'rtacha logtime: <b>{avg:.2f}</b> soat/kun",
                parse_mode="HTML",
            )
            await callback.answer()
        elif action == "refresh":
            text, valid_login = await fetch_and_render_profile(api_client, login)
            await callback.message.edit_text(
                text,
                reply_markup=get_participant_inline_keyboard(valid_login),
                parse_mode="HTML",
            )
            await callback.answer("Ma'lumotlar yangilandi ✅")
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)
