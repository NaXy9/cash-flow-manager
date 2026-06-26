set -e

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

# Seed demo data only on first run
python manage.py shell -c "
import sys
from apps.transactions.models import Transaction
sys.exit(0 if Transaction.objects.exists() else 1)
" && echo "[entrypoint] Demo data present — skipping seed." \
  || (echo "[entrypoint] Fresh database — seeding demo data..." \
      && python manage.py seed_data)

if [ "${DEBUG:-False}" = "True" ]; then
    echo "[entrypoint] Starting Django dev server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    WORKERS="${GUNICORN_WORKERS:-2}"
    echo "[entrypoint] Starting Gunicorn (workers=${WORKERS})..."
    exec gunicorn config.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers "$WORKERS" \
        --timeout 60 \
        --access-logfile - \
        --error-logfile -
fi
