# HobbyHeaven

HobbyHeaven — это платформа для публикации и обмена хобби. Проект представляет собой полноценное веб-приложение с REST API, построенное на современном стеке технологий.

---

## Основные возможности

*   **Web UI:** Интерфейс для просмотра, создания, редактирования и удаления постов (CRUD).
*   **REST API:** Программный доступ к данным с автоматической Swagger-документацией.
*   **Загрузка изображений:** Поддержка прикрепления фотографий к постам.
*   **Reverse Proxy:** Использование Nginx для повышения производительности и безопасности.
*   **Docker Ready:** Запуск всей инфраструктуры одной командой через Docker Compose.

---

## Стек технологий

*   **Backend:** FastAPI (Python 3.12)
*   **Database:** PostgreSQL
*   **ORM:** SQLAlchemy
*   **Templates:** Jinja2
*   **Infrastructure:** Docker, Docker Compose
*   **Web Server:** Nginx

---

## Структура проекта

```text
hobbyheaven/
├── app/
│   ├── main.py          # Точка входа и маршруты FastAPI
│   ├── models.py        # Модели SQLAlchemy (БД)
│   ├── schemas.py       # Схемы Pydantic (валидация данных)
│   ├── database.py      # Настройка подключения к PostgreSQL
│   ├── templates/       # HTML шаблоны (Jinja2)
│   ├── static/          # Статические файлы (CSS, JS)
│   └── uploads/         # Загруженные изображения пользователей
├── nginx/
│   └── nginx.conf       # Конфигурация Reverse Proxy
├── Dockerfile           # Инструкции для сборки образа приложения
└── docker-compose.yml   # Оркестрация сервисов (web, db, nginx)
```

---

## Быстрый старт (Docker)

Для запуска проекта в контейнеризированной среде выполните следующие шаги:

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/yourusername/hobbyheaven.git
    cd hobbyheaven
    ```

2.  **Запустите сервисы:**
    ```bash
    docker-compose up --build
    ```

3.  **Приложение будет доступно по адресу:** [http://localhost](http://localhost)

---

## Локальная разработка (без Docker)

1.  **Настройте виртуальное окружение:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Настройте базу данных:**
    Создайте БД в PostgreSQL и укажите строку подключения в переменной окружения `DATABASE_URL` или отредактируйте `app/database.py`.

3.  **Запустите сервер:**
    ```bash
    uvicorn app.main:app --reload
    ```

---

## Документация API

После запуска проекта доступна интерактивная документация:

*   **Swagger UI:** [http://localhost/docs](http://localhost/docs)
*   **ReDoc:** [http://localhost/redoc](http://localhost/redoc)

---

## Архитектура системы

Проект построен на базе микросервисной архитектуры с использованием Docker Compose:

```text
[ Пользователь ]
      │
      ▼
[ Nginx (Reverse Proxy) ] ──┐
      │                     │
      ▼                     │ (Static Files)
[ FastAPI (Uvicorn) ] <─────┘
      │
      ▼
[ PostgreSQL (Database) ]
```

### Компоненты:
1.  **Nginx:** Единая точка входа. Занимается проксированием запросов и быстрой отдачей статических файлов (изображений) из папки `uploads/`.
2.  **FastAPI:** Ядро приложения. Обрабатывает маршруты, валидирует данные через Pydantic и рендерит HTML-шаблоны.
3.  **PostgreSQL:** Реляционная база данных для хранения постов.
4.  **Alembic:** Инструмент для миграций, обеспечивающий версионность структуры базы данных.

---

## Быстрый старт (Docker)


**Dr.Aculushka** - [GitHub Profile](https://github.com/draculushka)
