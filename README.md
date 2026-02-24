# Metrics API

REST API для управления метриками и записями метрик с JWT авторизацией, кэшированием и периодическими задачами.

## Стек технологий

- **Python 3.12** / **Django 5.1** / **Django REST Framework 3.15**
- **PostgreSQL 16** — база данных
- **Redis 7** — кэш и брокер сообщений
- **Celery** — фоновые задачи
- **Celery Beat** — периодические задачи
- **drf-spectacular** — Swagger / OpenAPI документация
- **Docker & Docker Compose** — контейнеризация

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone <url>
cd metrics_api
```

### 2. Настройка переменных окружения

Файл `.env` уже содержит настройки по умолчанию для локальной разработки.
При необходимости измените значения:

```
SECRET_KEY=django-insecure-change-me-in-production-x7k9m2p4
DEBUG=1
POSTGRES_DB=metrics_db
POSTGRES_USER=metrics_user
POSTGRES_PASSWORD=metrics_pass
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

При первом запуске автоматически:
- Применяются миграции
- Создаётся суперпользователь (логин/пароль из `.env`)

### 4. Доступные сервисы

| Сервис          | URL                              |
|-----------------|----------------------------------|
| API             | http://localhost:8000/api/       |
| Admin панель    | http://localhost:8000/admin/     |
| Swagger UI      | http://localhost:8000/api/docs/  |
| ReDoc           | http://localhost:8000/api/redoc/ |

## API Эндпоинты

| Метод  | URL                                        | Описание                                        | Авторизация |
|--------|--------------------------------------------|-------------------------------------------------|:-----------:|
| POST   | `/api/token/`                              | Получение JWT токена (access + refresh)         | ✗           |
| POST   | `/api/token/refresh/`                      | Обновление access токена                        | ✗           |
| GET    | `/api/tags/`                               | Список тегов                                    | ✓           |
| POST   | `/api/metrics/`                            | Создание метрики                                | ✓           |
| GET    | `/api/metrics/`                            | Список метрик текущего пользователя             | ✓           |
| GET    | `/api/metrics/{id}/records/`               | Список записей метрики (кэшируется)             | ✓           |
| GET    | `/api/metrics/{id}/records/{record_id}/`   | Детализация одной записи                        | ✓           |
| POST   | `/api/metrics/{id}/records/`               | Создание записи метрики                         | ✓           |

## Аутентификация

Используется JWT (JSON Web Token) через `djangorestframework-simplejwt`.

```bash
# Получить токен
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'

# Использовать токен
curl http://localhost:8000/api/metrics/ \
  -H "Authorization: Bearer <access_token>"
```

## Управление пользователями

1. Войдите в админ панель: http://localhost:8000/admin/
2. Используйте учётные данные суперпользователя из `.env`
3. Добавляйте пользователей через раздел «Users»

## Celery Beat — периодические задачи

Задача `generate_fake_report` выполняется каждые 2 минуты и создаёт/обновляет файл
`reports/fake_report.txt` с общим количеством метрик и записей в базе.

## Запуск тестов

```bash
docker-compose exec web python manage.py test metrics
```

## Линтеры и типизация

```bash
# Форматирование кода
docker-compose exec web black .
docker-compose exec web isort .

# Проверка стиля
docker-compose exec web flake8 .

# Проверка типов
docker-compose exec web mypy .
```

## Структура проекта

```
metrics_api/
├── config/              # Настройки Django, Celery, URL-маршруты
│   ├── settings.py
│   ├── urls.py
│   ├── celery.py
│   └── wsgi.py
├── metrics/             # Основное приложение
│   ├── models.py        # Metric, MetricRecord, Tag
│   ├── serializers.py   # DRF сериализаторы
│   ├── views.py         # API views с кэшированием
│   ├── urls.py          # Маршруты приложения
│   ├── admin.py         # Админ панель
│   ├── tasks.py         # Celery задачи
│   └── tests.py         # Тесты
├── reports/             # Директория для фейк-отчётов
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml       # Конфигурация black, isort, mypy
├── .flake8              # Конфигурация flake8
└── .env                 # Переменные окружения
```

