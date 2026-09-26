import logging
from typing import Optional
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from campus_monitoring.api.client import School21ApiClient
from campus_monitoring.api.exceptions import NotFoundError, School21ApiError
from campus_monitoring.bot.keyboards.common import get_clusters_inline_keyboard, get_cluster_selection_keyboard, get_cluster_back_keyboard, get_campus_selection_keyboard, get_campus_selection_clusters_keyboard
from campus_monitoring.bot.utils.formatter import format_clusters_overview
from campus_monitoring.config import settings

logger = logging.getLogger(__name__)
router = Router(name="campus_router")


async def resolve_campus_id(api_client: School21ApiClient, explicit_id: Optional[str] = None) -> Optional[str]:
    if explicit_id:
        return explicit_id
    if settings.default_campus_id:
        return settings.default_campus_id

    # Fallback to Samarkand if possible, else the first one
    try:
        campuses = await api_client.get_campuses()
        for c in campuses.campuses:
            if "Samarkand" in c.shortName or "Samarqand" in c.shortName:
                return c.id
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
    text = "🏢 <b>Klasterlar holati:</b> Qaysi kampusni tanlaysiz?"
    await message.answer(
        text,
        reply_markup=get_campus_selection_clusters_keyboard(),
        parse_mode="HTML"
    )


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
        for wp in cmap.clusterMap:
            user_login = wp.login or "Noma'lum"
            lines.append(f"• <code>{wp.row.upper()}{wp.number}</code>: 👤 <code>{user_login}</code>")

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
        
        all_lines = ["🏢 <b>Klasterlar holati:</b>\n"]
        total_seats = 0
        total_available = 0
        
        for cl in clusters_res.clusters:
            total_seats += cl.capacity
            total_available += cl.availableCapacity
            
            all_lines.append(f"🔹 <b>Qavat {cl.name}</b>")
            try:
                cmap = await api_client.get_cluster_map(cluster_id=cl.id, occupied=True, limit=500)
                if cmap.clusterMap:
                    for wp in cmap.clusterMap:
                        user_login = wp.login or "Noma'lum"
                        # Format: Qavat tillakori: ti-a5 nick
                        all_lines.append(f"Qavat {cl.name}: {wp.row.lower()}{wp.number} {user_login}")
                else:
                    all_lines.append("<i>Bo'sh</i>")
            except Exception as e:
                all_lines.append("<i>Ma'lumot olinmadi</i>")
            
            all_lines.append("") # Bo'sh qator

        occupied = total_seats - total_available
        pct = (occupied / total_seats * 100) if total_seats > 0 else 0
        all_lines.append(f"📈 <b>Jami kampus bo'yicha:</b>")
        all_lines.append(f"Jami o'rinlar: {total_seats}")
        all_lines.append(f"Bo'sh o'rinlar: {total_available}")
        all_lines.append(f"Bandlik: {pct:.1f}%")

        final_text = "\n".join(all_lines)
        
        if len(final_text) > 4000:
            chunks = [final_text[i:i+4000] for i in range(0, len(final_text), 4000)]
            await callback.message.edit_text(chunks[0], parse_mode="HTML")
            for chunk in chunks[1:]:
                await callback.message.answer(chunk, parse_mode="HTML")
        else:
            await callback.message.edit_text(final_text, reply_markup=get_clusters_inline_keyboard(campus_id), parse_mode="HTML")
        
        await callback.answer("Klasterlar yangilandi ✅")
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

@router.message(Command("here"))
@router.message(F.text == "📍 Barcha o'tirganlar")
async def cmd_here(message: Message) -> None:
    text = "🏢 <b>Qaysi kampusni tanlaysiz?</b>\n\nPastdagi tugmalardan birini tanlang:"
    await message.answer(
        text, 
        reply_markup=get_campus_selection_keyboard, get_campus_selection_clusters_keyboard(), 
        parse_mode="HTML"
    )

@router.callback_query(F.data == "map:start")
async def cb_map_start(callback: CallbackQuery) -> None:
    await callback.answer()
    text = "🏢 <b>Qaysi kampusni tanlaysiz?</b>\n\nPastdagi tugmalardan birini tanlang:"
    await callback.message.edit_text(
        text, 
        reply_markup=get_campus_selection_keyboard, get_campus_selection_clusters_keyboard(), 
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("map:campus:"))
async def cb_map_campus(callback: CallbackQuery, api_client: School21ApiClient) -> None:
    campus_id = callback.data.split(":")[2]
    await callback.answer("⏳ Klasterlar ro'yxati yuklanmoqda...", show_alert=False)
    try:
        clusters_res = await api_client.get_campus_clusters(campus_id)
        if not clusters_res.clusters:
            await callback.message.edit_text("🏢 Bu kampusda klasterlar mavjud emas.")
            return
            
        text = "🏢 <b>Kampusdagi klasterlar ro'yxati:</b>\n\nQaysi klasterdagi talabalarni ko'rmoqchisiz? Pastdagi tugmalardan birini tanlang:"
        
        await callback.message.edit_text(
            text, 
            reply_markup=get_cluster_selection_keyboard(clusters_res.clusters, campus_id), 
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

@router.callback_query(F.data.startswith("map:cl:"))
async def cb_map_cluster(callback: CallbackQuery, api_client: School21ApiClient) -> None:
    parts = callback.data.split(":")
    cluster_id = int(parts[2])
    campus_id = parts[3]
    await callback.answer("⏳ Klaster xaritasi yuklanmoqda...", show_alert=False)
    try:
        # To get the cluster name, we need to fetch all clusters again since we only have ID
        clusters_res = await api_client.get_campus_clusters(campus_id)
        cluster_name = str(cluster_id)
        for c in clusters_res.clusters:
            if c.id == cluster_id:
                cluster_name = c.name
                break
                
        cmap = await api_client.get_cluster_map(cluster_id=cluster_id, occupied=True, limit=500)
        
        all_lines = [f"📍 <b>Klaster {cluster_name.capitalize()}:</b>\n"]
        if cmap.clusterMap:
            for wp in cmap.clusterMap:
                user_login = wp.login or "Noma'lum"
                all_lines.append(f"• <code>{wp.row.upper()}{wp.number}</code> ➖ 👤 <code>{user_login}</code>")
        else:
            all_lines.append("<i>Hech kim yo'q (Bo'sh)</i>")
            
        final_text = "\n".join(all_lines)
        if len(final_text) > 4000:
            final_text = final_text[:3900] + "\n\n... (xabar juda uzun, qisqartirildi)"
            
        await callback.message.edit_text(
            final_text, 
            reply_markup=get_cluster_back_keyboard(campus_id), 
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"Xatolik: {e}", show_alert=True)

@router.callback_query(F.data == "clusters:start")
async def cb_clusters_start(callback: CallbackQuery) -> None:
    await callback.answer()
    text = "🏢 <b>Klasterlar holati:</b> Qaysi kampusni tanlaysiz?"
    await callback.message.edit_text(
        text,
        reply_markup=get_campus_selection_clusters_keyboard(),
        parse_mode="HTML"
    )
