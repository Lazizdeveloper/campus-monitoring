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

<b>🔔 Savdolar va Tadbirlar:</b>
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
