FROM mcr.microsoft.com/playwright/python:v1.43.0-jammy

# Kerakli muhit o'zgaruvchilari
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Ishchi papkani o'rnatamiz
WORKDIR /app

# Loyihani nusxalaymiz
COPY . /app/

# UV paket menejerini o'rnatamiz va bog'liqliklarni yuklaymiz
RUN pip install uv && \
    uv venv && \
    uv pip install -e .

# Playwright brauzerlarini o'rnatamiz (asosan chromium yetarli)
RUN uv run playwright install chromium

# Botni ishga tushirish buyrug'i
CMD ["uv", "run", "campus-monitoring"]
