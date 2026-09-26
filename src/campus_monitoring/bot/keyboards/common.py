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
                    text="🔄 Yangilash",
                    callback_data=f"campus:clusters:{campus_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Kampuslar",
                    callback_data="clusters:start",
                )
            ]
        ]
    )

def get_campus_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📍 Samarqand", callback_data="map:campus:667a42af-5469-4a33-9858-677d9d20956a"),
                InlineKeyboardButton(text="📍 Toshkent", callback_data="map:campus:bad03b39-ffd4-4217-9d24-65535fe1f293")
            ]
        ]
    )

def get_cluster_selection_keyboard(clusters: list, campus_id: str) -> InlineKeyboardMarkup:
    kb = []
    # Create rows of 2 buttons each
    for i in range(0, len(clusters), 2):
        row = []
        for cl in clusters[i:i+2]:
            row.append(InlineKeyboardButton(text=f"📍 {cl.name.capitalize()}", callback_data=f"map:cl:{cl.id}:{campus_id}"))
        kb.append(row)
    
    # Back button to campus selection
    kb.append([InlineKeyboardButton(text="🔙 Kampus tanlashga qaytish", callback_data="map:start")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_cluster_back_keyboard(campus_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Klasterlar ro'yxatiga qaytish", callback_data=f"map:campus:{campus_id}")]
        ]
    )

def get_campus_selection_clusters_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📍 Samarqand", callback_data="campus:clusters:667a42af-5469-4a33-9858-677d9d20956a"),
                InlineKeyboardButton(text="📍 Toshkent", callback_data="campus:clusters:bad03b39-ffd4-4217-9d24-65535fe1f293")
            ]
        ]
    )
