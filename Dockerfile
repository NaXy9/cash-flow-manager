# =============================================================
# Cash Flow Manager — Dockerfile
# Python 3.14 + Django 6.0 (актуальные версии на июнь 2026)
# SQLite database живёт на именованном Docker volume.
# =============================================================
FROM python:3.14-slim

# Unbuffered output — логи сразу видны в `docker compose logs`
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Системные зависимости (gcc нужен для компиляции некоторых пакетов)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Зависимости устанавливаются отдельным слоем —
# пересборка не требуется если изменился только исходный код
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Директория для SQLite (volume перекроет её в рантайме)
RUN mkdir -p db

# Собираем статику (Bootstrap через CDN; здесь только custom.css)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# entrypoint.sh: migrate → seed при первом запуске → runserver
CMD ["sh", "entrypoint.sh"]
