# wallet_tt

Асинхронный API-сервис для управления кошельками на Python/FastAPI.

## Описание

Этот проект реализует REST API для работы с пользовательскими кошельками: создание, просмотр баланса, внесение и снятие средств.  
Проект спроектирован с учетом тестируемости, масштабируемости и современного стека Python.

## Технологии

- Python 3.10+  
- FastAPI  
- PostgreSQL  
- Alembic (миграции БД)
- Docker, Docker Compose  
- httpx  
- pytest, pytest-asyncio  
- MagicMock/AsyncMock (моки для тестирования)  
- pydantic (валидация)

## Возможности

- Создание кошелька с начальным балансом
- Получение баланса по UUID кошелька
- Пополнение и списание (операции с кошельком)

## Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/DenisSedovEd/wallet_tt.git

cd wallet_tt
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и при необходимости измените значения:

```
POSTGRES_USER=wallet_user
POSTGRES_PASSWORD=wallet_pass
POSTGRES_DB=wallet_db
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

- Приложение будет доступно на: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

**Миграции alembic применяются автоматически при старте контейнера с помощью `entrypoint.sh` в Dockerfile.**

> Если потребуется применить миграции вручную, используйте:
> ```bash
> docker-compose exec backend alembic upgrade head
> ```

## Примеры запросов

### Создание кошелька

```http
POST /api/v1/wallets/
Content-Type: application/json

{
  "balance": "100.00"
}
```

### Получение баланса

```http
GET /api/v1/wallets/{wallet_uuid}
```

### Операция (пополнение/списание)

```http
POST /api/v1/wallets/{wallet_uuid}/operation?operation_type=DEPOSIT&amount=100
```

## Запуск тестов

```bash
pytest
```

## Структура репозитория

- `api/` — маршруты FastAPI
- `schemas/` — pydantic-схемы
- `models/` — бизнес-модели
- `alembic/` — миграции alembic
- `tests/` — тесты (организованы по роутам и сценариям)
- `docker-compose.yml` — конфигурация для запуска приложения и БД
- `Dockerfile`, `entrypoint.sh` — сборка и запуск контейнера, автоприменение миграций
- `conftest.py` — общие фикстуры для тестов

## Контакты

Автор: [DenisSedovEd](https://github.com/DenisSedovEd)