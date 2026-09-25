from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from campus_monitoring.bot.keyboards.common import get_main_keyboard

router = Router(name="common_router")

HELP_TEXT = """
🤖 <b>School 21 Campus Monitoring Bot</b>

Quyidagi buyruqlardan foydalanishingiz mumkin:

<b>👤 Talaba ma'lumotlari:</b>
• <code>/user &lt;login&gt;</code> — Talabaning to'liq profili (XP, level, ballar, joyi)
• <code>/where &lt;login&gt;</code> — Talaba ayni paytda qaysi klaster va stolda o'tirganini ko'rish
• <code>/logtime &lt;login&gt;</code> — Haftalik o'rtacha logtime (kampusda o'tkazgan vaqti)
• <code>/projects &lt;login&gt;</code> — Talabaning loyihalari holati
• <code>/skills &lt;login&gt;</code> — Talabaning ko'nikma ballari

<b>🏢 Kampus va Klasterlar:</b>
• <code>/campuses</code> — Barcha kampuslar ro'yxati
• <code>/clusters</code> — Klasterlardagi bo'sh va band o'rinlar monitoringi
• <code>/map &lt;cluster_id&gt;</code> — Klaster xaritasi va band joylar

<b>🔔 Xabarnomalar (Bildirishnomalar):</b>
• <code>/track &lt;login&gt;</code> — Talaba kampusga kirgani/chiqqani haqida bildirishnoma yoqish
• <code>/untrack &lt;login&gt;</code> — Talaba kuzatuvini to'xtatish
• <code>/reviews on|off</code> — Sizga peer-review tushganda avtomatik xabar berishni yoqish/o'chirish

<b>📊 Savdolar va Tadbirlar:</b>
• <code>/sales</code> — PRP va CRP peer-review savdolari (sales) holati
• <code>/events</code> — Yaqin kunlardagi kampus tadbirlari va imtihonlar

<i>Pastdagi tugmalar orqali ham buyruqlarni qulay tanlashingiz mumkin!</i>
"""


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "<b>School 21 Campus Monitoring</b> botiga xush kelibsiz.\n"
        "Ushbu bot orqali kampus klasterlaridagi bo'sh joylar, talabalar qayerda o'tirgani, "
        "loyihalar, ballar va peer-review savdolarini qulay kuzatib borishingiz mumkin.\n\n"
        "Boshlash uchun pastdagi menyudan foydalaning yoki <code>/help</code> buyrug'ini yuboring."
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard(), parse_mode="HTML")


@router.message(Command("help"))
@router.message(F.text == "ℹ️ Yordam")
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Bekor qilinadigan faol amal yo'q.", reply_markup=get_main_keyboard())
        return
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=get_main_keyboard())

from campus_monitoring.services.subscriptions import subs_manager

@router.message(Command("track"))
async def cmd_track(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Iltimos, talaba loginini kiriting: `/track <login>`", parse_mode="Markdown")
        return
    login = parts[1].strip().lower()
    subs_manager.add_track(message.chat.id, login)
    await message.answer(f"✅ <b>{login}</b> qamrovga olindi!\n\nEndi u kampusga kirganda, joyini o'zgartirganda yoki kampusdan chiqqanda bot avtomatik ravishda xabar yuboradi.", parse_mode="HTML")

@router.message(Command("untrack"))
async def cmd_untrack(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Iltimos, talaba loginini kiriting: `/untrack <login>`", parse_mode="Markdown")
        return
    login = parts[1].strip().lower()
    subs_manager.remove_track(message.chat.id, login)
    await message.answer(f"❌ <b>{login}</b> kuzatuvdan olib tashlandi.", parse_mode="HTML")

@router.message(Command("reviews"))
async def cmd_reviews(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or parts[1].lower() not in ["on", "off"]:
        await message.answer("Iltimos, holatni kiriting: `/reviews on` yoki `/reviews off`", parse_mode="Markdown")
        return
    
    state = parts[1].lower() == "on"
    subs_manager.set_reviews(message.chat.id, state)
    
    if state:
        await message.answer("✅ <b>Peer-review xabarnomalari yoqildi!</b>\n\nSizga yangi baholash (peer-review) tushganda yoki agendangizda yangi baholash paydo bo'lganda bot darhol xabar beradi.", parse_mode="HTML")
    else:
        await message.answer("❌ <b>Peer-review xabarnomalari o'chirildi.</b>", parse_mode="HTML")
