# 🏫 School 21 Campus Monitoring Telegram Bot

School 21 o'quv platformasi (`platform.21-school.ru`) uchun kampus, klasterlar, talabalar va tadbirlarni qulay kuzatib boruvchi Telegram bot.

---

## 🚀 Asosiy Imkoniyatlar

1. **👤 Talabalar Monitoringi:**
   - **Profil:** Login bo'yicha talabaning umumiy darajasi (Level), XP, keyingi darajagacha qolgan ballar, guruh (Wave) va koalitsiyasi.
   - **Ish joyi (Workstation):** Talaba ayni paytda qaysi klasterda va qaysi stolda (`Ocean - A24` kabi) o'tirganini aniqlash.
   - **Loyihalar:** Talabaning joriy, topshirilgan (`ACCEPTED`) yoki tekshiruvdagi loyihalari va foizlari.
   - **Logtime:** Haftalik o'rtacha kampusda bo'lgan vaqti (soat/kun).
   - **Ko'nikmalar:** Soft-skill va texnik mahorat ballari vizual progress-barlar bilan.

2. **🏢 Klasterlar va Kampus:**
   - **Klasterlar holati:** Klasterlarning umumiy sig'imi, band o'rinlar va mavjud bo'sh joylar soni, bandlik foizi.
   - **Klaster xaritasi:** Qaysi o'rindiqda kim o'tirganini ko'rish.
   - **Bir nechta kampuslarni qo'llab-quvvatlash:** Moskva, Qozon, Toshkent va boshqa barcha School 21 kampuslari.

3. **🏷 Peer-Review Savdolari (Sales):**
   - PRP va CRP peer-review ballari savdolari (sales) holati (Faol, Rejalashtirilgan).
   - O'zgarishlar haqida fon monitoringi orqali avtomatik bildirishnoma yuborish.

4. **📅 Tadbirlar va Imtihonlar (Events):**
   - Kampusdagi yaqin kunlardagi workshoplar, testlar va imtihonlar ro'yxati.

---

## 🛠 O'rnatish va Ishga Tushirish

### 1. Talablar
- Python `>= 3.12`
- [`uv`](https://github.com/astral-sh/uv) (tavsiya etiladi) yoki `pip`

### 2. Sozlash (`.env` fayli)
Loyihada `.env.example` faylidan nusxa olib `.env` faylini yarating:

```bash
cp .env.example .env
```

`.env` faylini oching va kerakli parametrlarni kiriting:

```env
# Telegram Bot Token (@BotFather dan olingan)
BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# School 21 API
SCHOOL21_API_URL=https://platform.21-school.ru/services/21-school/api
SCHOOL21_TOKEN=sizning_school21_jwt_yoki_api_tokeningiz

# Asosiy kampus ID (ixtiyoriy, UUID)
DEFAULT_CAMPUS_ID=

# Admin telegram ID lari (vergul bilan ajratilgan, ixtiyoriy)
ADMIN_IDS=12345678,87654321
```

### 3. Bog'liqliklarni o'rnatish
```bash
uv sync
```

### 4. Botni ishga tushirish
```bash
uv run campus-monitoring
# yoki
uv run python main.py
```

### 5. Testlarni ishga tushirish
```bash
uv run pytest
```

---

## 📱 Bot Buyruqlari

| Buyruq | Tavsif |
|---|---|
| `/start` | Botni ishga tushirish va asosiy menyuni ochish |
| `/help` | Bot buyruqlari haqida to'liq qo'llanma |
| `/user <login>` | Talabaning to'liq profili va ballari |
| `/where <login>` | Talaba hozir qaysi stolda o'tirganini ko'rish |
| `/logtime <login>` | Haftalik o'rtacha logtime |
| `/projects <login>` | Talaba loyihalari holati |
| `/skills <login>` | Ko'nikmalar ro'yxati |
| `/campuses` | Barcha School 21 kampuslar ro'yxati |
| `/clusters` | Klasterlardagi bo'sh/band o'rinlar monitoringi |
| `/map <cluster_id>` | Klaster bandlik xaritasi |
| `/sales` | PRP/CRP savdolari holati |
| `/events` | Yaqin kunlardagi tadbirlar va imtihonlar |

---

## 📂 Loyiha Tuzilmasi

```text
campus-monitoring/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── main.py
├── tests/
│   ├── test_api_models.py
│   └── test_formatter.py
└── src/
    └── campus_monitoring/
        ├── __init__.py
        ├── config.py           # Pydantic Settings sozlamalari
        ├── main.py             # Asosiy ishga tushiruvchi modul
        ├── api/
        │   ├── client.py       # School 21 API asinxron mijozi (aiohttp)
        │   ├── models.py       # Pydantic javob modellari (OpenAPI v1)
        │   └── exceptions.py   # Xatoliklar boshqaruvi
        ├── bot/
        │   ├── bot.py          # Aiogram bot va dispatcher sozlash
        │   ├── handlers/       # Xabarlar va buyruqlar ishlovchilari
        │   ├── keyboards/      # Inline va Reply tugmalar
        │   ├── middlewares/    # API mijozini in'yeksiya qilish middleware
        │   └── utils/          # Telegram HTML formatlash utilitalari
        └── services/
            └── monitor.py      # Fon monitoring servisi (APScheduler)
```
