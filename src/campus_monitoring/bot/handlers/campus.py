import logging
from typing import Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.api.exceptions import NotFoundError, School21ApiError
from campus_monitoring.bot.keyboards.common import get_clusters_inline_keyboard
from campus_monitoring.bot.utils.formatter import format_clusters_overview
from campus_monitoring.config import settings

logger = logging.getLogger(__name__)
router = Router(name="campus_router")


async def resolve_campus_id(api_client: School21ApiClient, explicit_id: Optional[str] = None) -> Optional[str]:
    if explicit_id:
        return explicit_id
    if settings.default_campus_id:
        return settings.default_campus_id

    # Fallback to the first available campus
    try:
        campuses = await api_client.get_campuses()
        if campuses.campuses:
            return campuses.campuses[0].id
    except Exception as e:
        logger.error(f"Failed to fetch campuses fallback: {e}")
    return None


@router.message(Command("campuses"))
async def cmd_campuses(message: Message, api_client: School21ApiClient) -> None:
    try:
        res = await api_client.get_campuses()
        if not res.campuses:
            await message.answer("🏢 Kampuslar ro'yxati bo'sh.")
            return

        lines = ["🏢 <b>School 21 Kampuslari:</b>\n"]
        for c in res.campuses:
            lines.append(f"• <b>{c.shortName}</b>: <code>{c.id}</code>")
        lines.append("\n<i>Klasterlarni ko'rish uchun: <code>/clusters &lt;campus_id&gt;</code></i>")
        await message.answer("\n".join(lines), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Kampuslarni yuklashda xatolik: {e}")


@router.message(Command("clusters"))
@router.message(F.text == "🏢 Klasterlar holati")
async def cmd_clusters(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1) if message.text else []
    explicit_id = args[1].strip() if len(args) > 1 and not message.text.startswith("🏢") else None

    wait_msg = await message.answer("⏳ Klasterlar ma'lumotlari yuklanmoqda...")
    try:
        campus_id = await resolve_campus_id(api_client, explicit_id)
        if not campus_id:
            await wait_msg.edit_text("❌ Kampus ID aniqlanmadi. Iltimos <code>/campuses</code> orqali tekshiring.")
            return

        clusters_res = await api_client.get_campus_clusters(campus_id)
        text = format_clusters_overview(clusters_res.clusters)
        await wait_msg.edit_text(
            text,
            reply_markup=get_clusters_inline_keyboard(campus_id),
            parse_mode="HTML",
        )
    except School21ApiError as e:
        await wait_msg.edit_text(f"⚠️ API xatosi: {e.message}")
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xatolik yuz berdi: {e}")


@router.message(Command("map"))
async def cmd_cluster_map(message: Message, api_client: School21ApiClient) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip().isdigit():
        await message.answer(
            "⚠️ Klaster ID ko'rsatilmadi yoki raqam emas.\nNamuna: <code>/map 824</code>",
            parse_mode="HTML",
        )
        return

    cluster_id = int(args[1].strip())
    wait_msg = await message.answer(f"⏳ Klaster #{cluster_id} xaritasi yuklanmoqda...")
    try:
        cmap = await api_client.get_cluster_map(cluster_id=cluster_id, occupied=True, limit=50)
        if not cmap.clusterMap:
            await wait_msg.edit_text(f"🏢 Klaster #{cluster_id} da hozirda band o'rinlar yo'q yoki klaster bo'sh.")
            return

        lines = [f"🏢 <b>Klaster #{cluster_id} - Band o'rinlar:</b>\n"]
        for wp in cmap.clusterMap[:30]:
            user_login = wp.login or "Noma'lum"
            lines.append(f"• <code>{wp.row.upper()}{wp.number}</code>: 👤 <code>{user_login}</code>")

        if len(cmap.clusterMap) > 30:
            lines.append(f"\n<i>... va yana {len(cmap.clusterMap) - 30} ta o'rindiq band.</i>")

        await wait_msg.edit_text("\n".join(lines), parse_mode="HTML")
    except NotFoundError:
        await wait_msg.edit_text(f"❌ Klaster #{cluster_id} topilmadi.")
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xatolik: {e}")


@router.callback_query(F.data.startswith("campus:clusters:"))
async def cb_refresh_clusters(callback: CallbackQuery, api_client: School21ApiClient) -> None:
    campus_id = callback.data.split(":")[2]
    try:
        clusters_res = await api_client.get_campus_clusters(campus_id)
        text = format_clusters_overview(clusters_res.clusters)
        await callback.message.edit_text(
            text,
            reply_markup=get_clusters_inline_keyboard(campus_id),
            parse_mode="HTML",
        )
        await callback.answer("Klasterlar yangilandi ✅")
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

@router.message(Command("here"))
async def cmd_here(message: Message, api_client: School21ApiClient) -> None:
    wait_msg = await message.answer("⏳ Kampusdagi barcha talabalar qidirilmoqda...")
    try:
        campus_id = await resolve_campus_id(api_client, None)
        if not campus_id:
            await wait_msg.edit_text("❌ Kampus ID topilmadi.")
            return

        clusters_res = await api_client.get_campus_clusters(campus_id)
        if not clusters_res.clusters:
            await wait_msg.edit_text("🏢 Kampusda klasterlar mavjud emas.")
            return
            
        all_lines = ["🏢 <b>Hozir kampusda (Samarkand) o'tirgan talabalar:</b>\n"]
        total_people = 0
        
        for cluster in clusters_res.clusters:
            try:
                cmap = await api_client.get_cluster_map(cluster_id=cluster.id, occupied=True, limit=500)
                if cmap.clusterMap:
                    all_lines.append(f"\n📍 <b>Klaster {cluster.name}:</b>")
                    for wp in cmap.clusterMap:
                        user_login = wp.login or "Noma'lum"
                        all_lines.append(f"• <code>{wp.row.upper()}{wp.number}</code> ➖ 👤 <code>{user_login}</code>")
                        total_people += 1
            except Exception as e:
                logger.error(f"Cluster {cluster.id} xaritasi xatosi: {e}")
                
        if total_people == 0:
            await wait_msg.edit_text("🏢 Hozirda kampusda hech kim yo'q (yoki barcha kompyuterlar bo'sh).")
            return
            
        all_lines.insert(1, f"<i>Jami: {total_people} kishi</i>")
        
        # Telegram message length limit is 4096, we might need to split if it's too long
        final_text = "\n".join(all_lines)
        if len(final_text) > 4000:
            # Chunk the message
            chunks = [final_text[i:i+4000] for i in range(0, len(final_text), 4000)]
            await wait_msg.edit_text(chunks[0], parse_mode="HTML")
            for chunk in chunks[1:]:
                await message.answer(chunk, parse_mode="HTML")
        else:
            await wait_msg.edit_text(final_text, parse_mode="HTML")
            
    except Exception as e:
        await wait_msg.edit_text(f"⚠️ Xatolik yuz berdi: {e}")
