from typing import List, Optional
import html

from campus_monitoring.api.models import (
    CampusV1DTO,
    ClusterMapV1DTO,
    ClusterV1DTO,
    EventV1DTO,
    ParticipantBadgeV1DTO,
    ParticipantCoalitionV1DTO,
    ParticipantPointsV1DTO,
    ParticipantProjectV1DTO,
    ParticipantSkillV1DTO,
    ParticipantV1DTO,
    ParticipantWorkstationV1DTO,
    SaleV1DTO,
)


def escape(text: Optional[str]) -> str:
    if text is None:
        return ""
    return html.escape(str(text))


def format_participant_profile(
    p: ParticipantV1DTO,
    ws: Optional[ParticipantWorkstationV1DTO] = None,
    coalition: Optional[ParticipantCoalitionV1DTO] = None,
    points: Optional[ParticipantPointsV1DTO] = None,
    logtime: Optional[float] = None,
) -> str:
    status_icon = "🟢" if p.status == "Active" else "⚪"
    level_str = f"<b>Level:</b> {p.level or 0} ({p.expValue or 0} XP)"
    if p.expToNextLevel:
        level_str += f" | <i>Keyingi levelgacha: {p.expToNextLevel} XP</i>"

    campus_name = escape(p.campus.shortName) if p.campus else "Noma'lum"
    wave = escape(p.className) if p.className else "-"
    parallel = escape(p.parallelName) if p.parallelName else "-"

    lines = [
        f"{status_icon} <b>Ishtirokchi:</b> <code>{escape(p.login)}</code>",
        f"📍 <b>Kampus:</b> {campus_name}",
        f"🏷 <b>Guruh (Wave):</b> {wave} ({parallel})",
        f"⭐ {level_str}",
    ]

    if coalition:
        lines.append(f"🛡 <b>Koalitsiya:</b> {escape(coalition.name)} (O'rin: #{coalition.rank or '-'})")

    if ws and ws.clusterName:
        lines.append(f"🖥 <b>Hozirgi joyi:</b> <code>{escape(ws.location_str)}</code>")
    else:
        lines.append("🖥 <b>Hozirgi joyi:</b> <i>Klasterda emas (Offline)</i>")

    if points:
        lines.append(
            f"💰 <b>Ballar:</b> PRP: <code>{points.peerReviewPoints}</code> | "
            f"CRP: <code>{points.codeReviewPoints}</code> | Coins: <code>{points.coins}</code>"
        )

    if logtime is not None:
        lines.append(f"⏱ <b>Haftalik o'rtacha logtime:</b> <code>{logtime:.2f}</code> soat/kun")

    return "\n".join(lines)


def format_workstation(login: str, ws: Optional[ParticipantWorkstationV1DTO]) -> str:
    safe_login = escape(login)
    if ws and ws.clusterName:
        return (
            f"🖥 <b>Talaba joylashuvi:</b>\n\n"
            f"👤 <b>Login:</b> <code>{safe_login}</code>\n"
            f"🏢 <b>Klaster:</b> <b>{escape(ws.clusterName)}</b>\n"
            f"🪑 <b>O'rindiq:</b> <code>{escape(ws.row.upper())}{ws.number}</code>"
        )
    return (
        f"👤 <b>Login:</b> <code>{safe_login}</code>\n"
        f"❌ Talaba ayni paytda hech qaysi ish stoliga login qilmagan (Offline)."
    )


def format_participant_projects(login: str, projects: List[ParticipantProjectV1DTO]) -> str:
    safe_login = escape(login)
    if not projects:
        return f"📂 <code>{safe_login}</code> uchun loyihalar topilmadi."

    status_emojis = {
        "ACCEPTED": "✅",
        "FAILED": "❌",
        "IN_PROGRESS": "⏳",
        "IN_REVIEWS": "🔍",
        "REGISTERED": "📝",
        "ASSIGNED": "📌",
    }

    lines = [f"📁 <b><code>{safe_login}</code> loyihalari ro'yxati:</b>\n"]
    for proj in projects[:15]:
        emoji = status_emojis.get(proj.status, "▪️")
        score = f" - <b>{proj.finalPercentage}%</b>" if proj.finalPercentage is not None else ""
        lines.append(f"{emoji} <b>{escape(proj.title)}</b> [{proj.status}]{score}")

    return "\n".join(lines)


def format_participant_skills(login: str, skills: List[ParticipantSkillV1DTO]) -> str:
    safe_login = escape(login)
    if not skills:
        return f"📊 <code>{safe_login}</code> uchun ko'nikmalar topilmadi."

    lines = [f"📊 <b><code>{safe_login}</code> ko'nikmalari:</b>\n"]
    for s in skills:
        bar_len = min(10, max(1, s.points // 100)) if s.points else 0
        bar = "🟩" * bar_len + "⬜" * (10 - bar_len)
        lines.append(f"• <b>{escape(s.name)}:</b> {s.points} ball\n  {bar}")

    return "\n".join(lines)


def format_clusters_overview(clusters: List[ClusterV1DTO], campus_name: str = "") -> str:
    if not clusters:
        return "🏢 Mavjud klasterlar topilmadi."

    title = f"🏢 <b>{escape(campus_name)} klasterlari holati:</b>\n" if campus_name else "🏢 <b>Klasterlar holati:</b>\n"
    lines = [title]

    total_seats = 0
    total_available = 0

    for cl in clusters:
        total_seats += cl.capacity
        total_available += cl.availableCapacity
        occupied = cl.capacity - cl.availableCapacity
        pct = (occupied / cl.capacity * 100) if cl.capacity > 0 else 0
        lines.append(
            f"🔹 <b>{escape(cl.name)}</b> (Qavat: {cl.floor or '-'})\n"
            f"   Band: <code>{occupied}/{cl.capacity}</code> ({pct:.1f}%) | "
            f"Bo'sh: <b>{cl.availableCapacity}</b> ta joy\n"
        )

    lines.append(
        f"📈 <b>Jami kampus bo'yicha:</b>\n"
        f"   Jami o'rinlar: <b>{total_seats}</b>\n"
        f"   Bo'sh o'rinlar: <b>{total_available}</b>\n"
        f"   Bandlik: <b>{((total_seats - total_available) / total_seats * 100) if total_seats > 0 else 0:.1f}%</b>"
    )
    return "\n".join(lines)


def format_sales(sales: List[SaleV1DTO]) -> str:
    if not sales:
        return "🏷 Hozirda faol yoki rejalashtirilgan peer-review savdolari (sales) yo'q."

    lines = ["🏷 <b>Peer-review savdolari (Sales):</b>\n"]
    for s in sales:
        status_badge = {
            "ACTIVE": "🟢 FAOL",
            "PLANNED": "🟡 REJALASHTIRILGAN",
            "NON_ACTIVE": "⚪ NOFAOL",
        }.get(s.status, s.status)

        start_time = s.startDateTime.replace("T", " ").replace("Z", " UTC") if s.startDateTime else "-"
        progress = f" ({s.progressPercentage}%)" if s.progressPercentage is not None else ""
        lines.append(
            f"• <b>Turi:</b> {s.type}\n"
            f"  <b>Holati:</b> {status_badge}{progress}\n"
            f"  <b>Boshlanish vaqti:</b> {start_time}\n"
        )
    return "\n".join(lines)


def format_events(events: List[EventV1DTO]) -> str:
    if not events:
        return "📅 Yaqin orada tadbirlar yoki imtihonlar topilmadi."

    lines = ["📅 <b>Yaqin kunlardagi tadbirlar:</b>\n"]
    for ev in events[:10]:
        time_str = ev.startDateTime.replace("T", " ").replace("Z", "") if ev.startDateTime else "-"
        loc = f" | 📍 {escape(ev.location)}" if ev.location else ""
        lines.append(
            f"▫️ <b>{escape(ev.name)}</b> ({escape(ev.type or 'Event')})\n"
            f"   ⏰ {time_str}{loc}\n"
            f"   👥 Qatnashuvchilar: {ev.registerCount or 0}/{ev.capacity or '-'}\n"
        )
    return "\n".join(lines)
