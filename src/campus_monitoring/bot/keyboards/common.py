from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [
            KeyboardButton(text="👤 Talaba qidirish"),
            KeyboardButton(text="🖥 Qayerda o'tiribdi?"),
        ],
        [
            KeyboardButton(text="🏢 Klasterlar holati"),
            KeyboardButton(text="📍 Barcha o'tirganlar"),
        ],
        [
            KeyboardButton(text="📅 Tadbirlar"),
            KeyboardButton(text="🏷 PRP/CRP Savdolari"),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_participant_inline_keyboard(login: str) -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🖥 Ish joyi", callback_data=f"user:ws:{login}"),
            InlineKeyboardButton(text="📂 Loyihalar", callback_data=f"user:proj:{login}"),
        ],
        [
            InlineKeyboardButton(text="📊 Ko'nikmalar", callback_data=f"user:skills:{login}"),
            InlineKeyboardButton(text="⏱ Logtime", callback_data=f"user:logtime:{login}"),
        ],
        [
            InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"user:refresh:{login}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def get_clusters_inline_keyboard(campus_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Klasterlarni yangilash",
                    callback_data=f"campus:clusters:{campus_id}",
                )
            ]
        ]
    )

def get_cluster_selection_keyboard(clusters: list) -> InlineKeyboardMarkup:
    kb = []
    # Create rows of 2 buttons each
    for i in range(0, len(clusters), 2):
        row = []
        for cl in clusters[i:i+2]:
            row.append(InlineKeyboardButton(text=f"📍 {cl.name.capitalize()}", callback_data=f"map:cl:{cl.id}"))
        kb.append(row)
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_cluster_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga (Klasterlar ro'yxati)", callback_data="map:back")]
        ]
    )
