# 📚 Book Recommender

Сервис для поиска книг по описанию с использованием искусственного интеллекта. Проект выполнен в рамках семестровой работы по курсу "Разработка ML-сервисов".

## 🎯 Функциональность

- 🔍 **Поиск книг** — по текстовому описанию (ИИ находит семантически похожие книги)
- 📖 **Поиск по названию** — точное совпадение или частичное вхождение
- 🎭 **Фильтрация** — по жанру, автору, году издания и рейтингу
- 👤 **Авторизация** — регистрация и вход с хешированием паролей (bcrypt)
- 📜 **История запросов** — просмотр всех предыдущих поисков
- 👑 **Админ-панель** — управление книгами (CRUD) и пользователями

## 🏗 Архитектура
┌─────────────────────────────────────────────────────────────┐
│ Пользователь │
└─────────────────────────────┬───────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│ Flask Web App (порт 5000) │
│ Рендеринг страниц, аутентификация │
└─────────────────────────────┬───────────────────────────────┘
│ HTTP
▼
┌─────────────────────────────────────────────────────────────┐
│ FastAPI ML API (порт 8000) │
│ SentenceTransformer (paraphrase-multilingual) │
└─────────────────────────────┬───────────────────────────────┘
│ SQL
▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL (порт 5432) │
│ Таблицы: users, books, predictions │
└─────────────────────────────────────────────────────────────┘

text

## 🛠 Технологии

| Компонент | Технология |
|-----------|------------|
| Веб-фреймворк | Flask 3.0 |
| ML-фреймворк | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| База данных | PostgreSQL 15 |
| ML-модель | SentenceTransformer (paraphrase-multilingual-MiniLM-L12-v2) |
| Контейнеризация | Docker + Docker Compose |
| Управление зависимостями | uv |
| Линтер/форматтер | ruff |
| Проверка типов | mypy |
| Хеширование паролей | bcrypt |

## 📁 Структура проекта
book-recommender/
├── README.md
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── docker-compose.yml
│
├── flask_app/ # Web-сервис
│ ├── Dockerfile
│ ├── pyproject.toml
│ └── app/
│ ├── init.py
│ ├── config.py
│ ├── database.py
│ ├── models.py
│ ├── routes/
│ │ ├── auth.py
│ │ ├── main.py
│ │ ├── history.py
│ │ └── admin.py
│ ├── services/
│ │ ├── auth_service.py
│ │ ├── prediction_service.py
│ │ ├── ml_client.py
│ │ ├── book_service.py
│ │ └── user_service.py
│ ├── templates/
│ │ ├── base.html
│ │ ├── index.html
│ │ ├── login.html
│ │ ├── register.html
│ │ ├── history.html
│ │ ├── admin.html
│ │ └── edit_book.html
│ └── static/
│ └── style.css
│
├── fastapi_app/ # ML-сервис
│ ├── Dockerfile
│ ├── pyproject.toml
│ └── app/
│ ├── init.py
│ ├── config.py
│ ├── database.py
│ ├── models.py
│ ├── routers/
│ │ ├── predict.py
│ │ ├── health.py
│ │ └── model_info.py
│ ├── services/
│ │ ├── model_service.py
│ │ └── prediction_service.py
│ └── repositories/
│ └── prediction_repository.py
│
└── data/ # Persistent volume для PostgreSQL
└── (файлы БД)

text

## 🚀 Запуск проекта

### Требования

- Docker Desktop
- Git
- 8+ GB RAM (для модели SentenceTransformer)

### Установка и запуск

```bash
# 1. Клонирование репозитория
git clone https://github.com/ваш_username/book-recommender.git
cd book-recommender

# 2. Создание администратора (первый запуск)
python scripts/hash_password.py
# Введите пароль и скопируйте хеш

# 3. Запуск всех сервисов
docker-compose up -d --build

# 4. Создание администратора в БД
docker exec -it book_db psql -U bookuser -d bookdb -c "
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(20) DEFAULT 'user';
INSERT INTO users (username, hashed_password, role) 
VALUES ('admin', 'ваш_хеш_пароля', 'administrator');
"

# 5. Перенос данных книг (если есть SQLite)
python scripts/migrate_sqlite_to_postgres.py
Доступ к сервисам
Сервис	URL	Описание
Веб-интерфейс	http://localhost:5000	Основной сайт
ML API	http://localhost:8000/docs	Документация FastAPI
Админ-панель	http://localhost:5000/admin	Только для администраторов
Создание администратора
Зарегистрируйтесь как обычный пользователь

Зайдите в контейнер БД:

bash
docker exec -it book_db psql -U bookuser -d bookdb
Выполните:

sql
UPDATE users SET role = 'administrator' WHERE username = 'ваш_логин';
🔧 Разработка
Локальный запуск без Docker
bash
# FastAPI
cd fastapi_app
uv run uvicorn app:app --reload --port 8000

# Flask (в другом терминале)
cd flask_app
uv run python -m flask run --port 5000
Запуск тестов
bash
pytest tests/
Проверка типов
bash
mypy flask_app/ fastapi_app/
Линтинг
bash
ruff check flask_app/ fastapi_app/
ruff format flask_app/ fastapi_app/
📊 API Эндпоинты
FastAPI (ML сервис)
Метод	Эндпоинт	Описание
GET	/health	Проверка статуса
GET	/genres	Список всех жанров
GET	/authors	Список авторов
POST	/predict	Поиск похожих книг
Пример запроса к /predict
json
{
  "user_id": 1,
  "description": "роман о любви и войне",
  "title": "Война и мир",
  "genre": "tolstoy",
  "author": "Leo Tolstoy",
  "min_rating": 4.0,
  "max_year": 1900
}
👥 Роли пользователей
Роль	Возможности
Пользователь	Поиск книг, просмотр истории, редактирование профиля
Администратор	Всё из пользователя + управление книгами (CRUD), управление пользователями
🐛 Известные проблемы и решения
Ошибка подключения к ML сервису
bash
docker-compose restart fastapi