# ДДС — Веб-сервис управления движением денежных средств

Веб-приложение для учёта финансовых операций: создание, редактирование,
удаление и фильтрация записей ДДС с управлением справочниками.

## Демо

Доступна демонстрационная версия приложения: **https://igor-pryanikov.ru:5000**

---

| Слой | Технология |
|---|---|
| Backend | Python 3.14, Django 6.0.6, Django REST Framework 3.17.1 |
| База данных | SQLite (через Django ORM) |
| Frontend | Bootstrap 5.3 (CDN), Bootstrap Icons, Vanilla JS |
| Тесты | pytest 8, pytest-django 4.8 |
| Контейнеризация | Docker + Docker Compose (образ `python:3.14-slim`) |

---

## Быстрый старт

### Вариант 1 — Docker Compose (рекомендуется)

```bash
git clone https://github.com/NaXy9/cash-flow-manager
cd cash_flow_manager

docker compose up --build
```

Приложение доступно на `http://localhost:8000`.  
Миграции и seed-данные применяются автоматически при запуске.

---

### Вариант 2 — локальная среда

**1. Установка зависимостей**

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**2. Настройка окружения**

```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

**3. Инициализация базы данных**

```bash
python manage.py migrate
python manage.py seed_data   # загружает начальные справочники из ТЗ
```

**4. Запуск сервера**

```bash
python manage.py runserver
```

Приложение: `http://127.0.0.1:8000`  
Django Admin: `http://127.0.0.1:8000/admin/`

**5. Создание суперпользователя (для Admin)**

```bash
python manage.py createsuperuser
```

---

## Запуск тестов

```bash
# Все тесты с подробным выводом
pytest tests/ -v

# С отчётом покрытия
pytest tests/ -v --cov=apps --cov-report=term-missing
```

Тестовое покрытие: **43 теста** — модели, сервис бизнес-логики, REST API.

---

## Структура проекта

```
cash_flow_manager/
├── config/                  # Django project (settings, urls, wsgi)
│   └── settings/base.py
├── apps/
│   ├── references/          # Справочники: Status, TransactionType, Category, Subcategory
│   │   ├── models.py        # ORM-модели с PROTECT и unique_together
│   │   ├── serializers.py   # DRF serializers
│   │   ├── api_views.py     # ViewSets + cascade @action endpoints
│   │   ├── views.py         # Django CBV (hub page fallback)
│   │   └── management/commands/seed_data.py
│   └── transactions/        # Основная сущность — записи ДДС
│       ├── models.py
│       ├── services.py      # validate_cascade_chain() — единый источник бизнес-правил
│       ├── serializers.py   # DRF + вызов services
│       ├── forms.py         # Django Form + вызов services
│       ├── filters.py       # FilterSet (дата, статус, тип, категория)
│       ├── api_views.py     # TransactionViewSet
│       ├── views.py         # TransactionListView (SPA entry point)
│       └── templatetags/cash_filters.py  # rubles, rubles_signed, query_transform
├── templates/
│   ├── base.html            # HTML shell, CDN links
│   └── transactions/list.html  # Одностраничное приложение
├── static/css/custom.css    # Переопределения Bootstrap + кастомные компоненты
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── unit/                # Модели, сервис
│   └── integration/         # REST API (cascade, CRUD, 409 Protect)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## REST API

Базовый URL: `/api/v1/`

| Метод | Endpoint | Описание |
|---|---|---|
| GET/POST | `/transactions/` | Список / создание |
| GET/PATCH/DELETE | `/transactions/{id}/` | Детали / обновление / удаление |
| GET | `/types/{id}/categories/` | **Каскад**: категории для типа |
| GET | `/categories/{id}/subcategories/` | **Каскад**: подкатегории для категории |
| GET/POST/PATCH/DELETE | `/statuses/`, `/types/`, `/categories/`, `/subcategories/` | CRUD справочников |

Попытка удалить справочник, используемый в транзакции, возвращает **409 Conflict**.
