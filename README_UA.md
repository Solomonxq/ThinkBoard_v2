# ThinkBoard v2 - Колаборативна дошка ідей

Платформа для створення, обговорення та голосування за ідеї в реальному часі з вбудованою системою голосування через WebSocket.

## 📋 Огляд проекту

ThinkBoard - це веб-додаток, який дозволяє командам:
- Створювати дошки для збору ідей
- Додавати ідеї до дошок
- Голосувати за ідеї в реальному часі через WebSocket
- Управляти користувачами та доступом до дошок
- Отримувати сповіщення електронною поштою про важливі события

## ✨ Основні можливості

### Управління дошками
- ✅ Створення/видалення дошок
- ✅ Додавання/видалення користувачів з дошок
- ✅ Встановлення улюблених дошок
- ✅ Керування доступом (приватна/публічна)

### Управління ідеями
- ✅ Створення ідей у дошці
- ✅ Видалення ідей (тільки автором)
- ✅ Встановлення часу завершення голосування
- ✅ Унікальні назви ідей у межах дошки

### Система голосування
- ✅ Real-time голосування через WebSocket
- ✅ Таймер зворотного відліку
- ✅ Автоматичне завершення голосування
- ✅ Сповіщення про результати голосування

### Профіль користувача
- ✅ Редагування профілю
- ✅ Завантаження аватара
- ✅ Оновлення пароля
- ✅ Видалення акаунту

### Аутентифікація
- ✅ Реєстрація та вхід
- ✅ OAuth Google інтеграція
- ✅ JWT токени з refresh механізмом
- ✅ Rate limiting

## 🛠️ Технологічний стек

### Backend
- **FastAPI** - асинхронний веб-фреймворк
- **SQLAlchemy** - ORM для роботи з базою даних
- **Alembic** - міграції БД
- **Pydantic** - валідація даних
- **Celery** - асинхронні завдання
- **Redis** - кеш та брокер повідомлень

### База даних
- **PostgreSQL** - основна база даних
- **Redis** - кеш

### Інструменти розробки
- **pytest** - тестування
- **locust** - тестування навантаження
- **Docker** - контейнеризація
- **Docker Compose** - оркестрація контейнерів

### Безпека
- **JWT** - токен-базована аутентифікація
- **bcrypt** - хешування паролів
- **python-slowapi** - rate limiting

## 🏗️ Архітектура

```
app/
├── api/               # API маршрути
│   └── v1/
│       ├── router.py
│       └── routers/
│           ├── auth.py      # Аутентифікація
│           ├── board.py     # Дошки
│           ├── idea.py      # Ідеї
│           ├── profile.py   # Профіль
│           └── vote.py      # Голосування (WebSocket)
├── crud/              # CRUD операції
│   ├── board.py
│   ├── idea.py
│   ├── user.py
│   └── vote.py
├── services/          # Бізнес-логіка
│   ├── auth_service.py
│   ├── board_service.py
│   ├── ideas_service.py
│   ├── profile_service.py
│   ├── vote_service.py
│   └── oauth.py
├── models/            # SQLAlchemy моделі
│   ├── user.py
│   ├── board.py
│   ├── idea.py
│   └── vote.py
├── schemas/           # Pydantic схеми
│   ├── user.py
│   ├── board.py
│   ├── idea.py
│   └── vote.py
├── core/              # Конфігурація та утиліти
│   ├── config.py      # Налаштування
│   ├── security.py    # JWT, хешування
│   ├── redis.py       # Redis клієнт
│   ├── celery_app.py  # Celery конфіг
│   ├── ws_manager.py  # WebSocket менеджер
│   └── limiter.py     # Rate limiting
├── events/            # Обробники подій
│   ├── auth_event.py
│   ├── idea_events.py
│   ├── profile_event.py
│   └── voting_events.py
├── tasks/             # Celery завдання
│   └── email_tasks.py
└── db/                # Конфіг БД
    ├── session.py
    └── init_db.py
```

## 🚀 Налаштування та запуск

### Передумови
- Python 3.12+
- Docker та Docker Compose
- PostgreSQL
- Redis

### Встановлення залежностей

```bash
# За допомогою uv (рекомендується)
uv sync

# Або pip
pip install -r requirements.txt
```

### Запуск з Docker Compose

```bash
docker-compose up -d
```

Це запустить:
- PostgreSQL
- Redis
- FastAPI додаток
- Celery worker

### Запуск локально

```bash
# Встановити залежності
uv sync

# Запустити міграції
alembic upgrade head

# Запустити сервер
uv run uvicorn app.main:app --reload

# У іншому терміналі запустити Celery
uv run celery -A app.core.celery_app worker --loglevel=info
```

## 🧪 Тестування

### Запуск всіх тестів

```bash
uv run pytest tests/
```

### Запуск конкретного набору тестів

```bash
# Тести дошок
uv run pytest tests/test_board_servide/

# Тести ідей
uv run pytest tests/test_idea_service/

# Тести голосування
uv run pytest tests/test_vote_service/

# Тести аутентифікації
uv run pytest tests/test_unit_auth_sevice/
```

### Тестування навантаження

```bash
# З веб-інтерфейсом
uv run locust -f locustfile.py --host http://localhost:8000

# Headless режим (100 користувачів, 10 сек)
uv run locust -f locustfile.py --host http://localhost:8000 \
    --headless -u 100 -r 10 -t 10s
```

## 📡 API кінцеві точки

### Аутентифікація
- `POST /api/v1/auth/register` - Реєстрація
- `POST /api/v1/auth/login` - Вхід
- `POST /api/v1/auth/refresh` - Оновлення токену
- `GET /api/v1/auth/me` - Поточний користувач

### Дошки
- `POST /api/v1/boards/create` - Створити дошку
- `DELETE /api/v1/boards/{board_id}` - Видалити дошку
- `POST /api/v1/boards/{board_id}/members` - Додати користувача
- `DELETE /api/v1/boards/{board_id}/members/{user_id}` - Видалити користувача
- `POST /api/v1/boards/{board_id}/favorite` - Додати у вибрані

### Ідеї
- `POST /api/v1/boards/{board_id}/ideas/create` - Створити ідею
- `DELETE /api/v1/boards/{board_id}/ideas/{idea_id}` - Видалити ідею

### Голосування (WebSocket)
- `WS /api/v1/boards/{board_id}/ideas/{idea_id}/vote/ws?token={token}` - WebSocket для голосування

### Профіль
- `GET /api/v1/profile/me` - Мій профіль
- `PATCH /api/v1/profile/me` - Оновити профіль
- `POST /api/v1/profile/me/avatar` - Завантажити аватар
- `GET /api/v1/profile/{username}` - Публічний профіль

## 🔌 WebSocket реалізація

### Підключення до голосування

```javascript
const token = 'your_jwt_token';
const ideaId = 'idea-123';
const boardId = 'board-456';

const ws = new WebSocket(
  `ws://localhost:8000/api/v1/boards/${boardId}/ideas/${ideaId}/vote/ws?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data); // { event, idea_id, approve, reject, ... }
};

// Голосування
ws.send(JSON.stringify({ status: true })); // За ідею
ws.send(JSON.stringify({ status: false })); // Проти ідеї
```

### События WebSocket

- `init` - Ініціалізація стану голосування
- `vote_updated` - Голос оновлено
- `voting_already_finished` - Голосування вже завершено
- `voting_finished` - Голосування завершено

## 📧 Email сповіщення

Проект використовує **Celery** для асинхронної відправки email:

- Реєстрація користувача
- Додавання до дошки
- Видалення з дошки
- Створення ідеї
- Завершення голосування

## 🔐 Безпека

- JWT токени з експіраційним часом
- Bcrypt хешування паролів
- Rate limiting на ендпоінтах
- CORS налаштування
- SQL injection захист (SQLAlchemy)

## 📊 Структура тестів

```
tests/
├── test_board_servide/        # Тести сервісу дошок
├── test_idea_service/         # Тести сервісу ідей
├── test_profile_service/      # Тести профілю
├── test_unit_auth_sevice/     # Тести аутентифікації
├── test_vote_service/         # Тести голосування
└── conftest.py                # Спільні фікстури
```

**Статистика:**
- ✅ 76 успішних тестів
- 0 помилок
- Покриття: основна бізнес-логіка

## 🗄️ Міграції БД

```bash
# Створити нову міграцію
alembic revision --autogenerate -m "Add new column"

# Застосувати міграції
alembic upgrade head

# Откотити останню міграцію
alembic downgrade -1
```

## 📝 Файлові конфігурації

### `pyproject.toml`
- Залежності проекту
- Конфіг tools (pytest, black, isort)

### `.env`
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost/thinkboard
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
EMAIL=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

### `docker-compose.yml`
- PostgreSQL сервіс
- Redis сервіс
- FastAPI додаток
- Celery worker

## 🤝 Контрибуції

1. Fork проекту
2. Створіть фічу (`git checkout -b feature/AmazingFeature`)
3. Коміт змін (`git commit -m 'Add some AmazingFeature'`)
4. Push до бренча (`git push origin feature/AmazingFeature`)
5. Відкрийте Pull Request

## 📄 Ліцензія

MIT License - див. LICENSE файл

## 👨‍💻 Автор

Solomon - розробник

## 📞 Контакти

- GitHub: [посилання на репозиторій]
- Email: your_email@example.com

## 🎯 Майбутні покращення

### Управління користувачами
- [ ] Групи користувачів (teams/departments)
- [ ] Система друзів та підписок
- [ ] Двофакторна верифікація (2FA via email/SMS)
- [ ] Реєстрація через інші сервіси:
  - [ ] GitHub OAuth
  - [ ] Microsoft/Outlook OAuth
  - [ ] Apple ID OAuth
  - [ ] Facebook OAuth
- [ ] Управління сеансами та пристроями
- [ ] Історія активності користувача

### Дошки та ідеї
- [ ] Архівування дошок (з можливістю відновлення)
- [ ] Більш детальне керування доступом:
  - [ ] Приватні дошки (тільки запрошені)
  - [ ] Відкриті дошки (для всіх)
  - [ ] Дошки з кодом доступу
- [ ] Пошук дошок (глобальний та за категоріями)
- [ ] Категоризація та теги для ідей
- [ ] Можливість додавання фото/медіа до ідей
- [ ] Вкладення файлів до ідей
- [ ] Коментарі до ідей з деревом обговорення
- [ ] Сортування ідей (за рейтингом, часом, популярністю)
- [ ] Шаблони дошок для швидкого старту

### Статистика та аналітика
- [ ] Статистика активності користувача:
  - [ ] Графіки участі
  - [ ] Час активності
  - [ ] Улюблені категорії
- [ ] Аналітика дошок:
  - [ ] Тренди ідей
  - [ ] Найпопулярніші учасники
  - [ ] Рейтинги за голосами
- [ ] Експорт звітів (PDF, CSV)
- [ ] Дашборд з KPI

### Система голосування
- [ ] Різні типи голосування:
  - [ ] Бінарне (За/Проти)
  - [ ] Рейтинг (1-5 зірок)
  - [ ] Множинний вибір
  - [ ] Пріоритизація (drag-and-drop)
- [ ] Анонімне голосування
- [ ] Завдання ваги голосам (на основі ролі)
- [ ] Результати голосування в реальному часі з графіками

### Інтеграції
- [ ] Інтеграція з Slack (повідомлення про нові ідеї)
- [ ] Інтеграція з Microsoft Teams
- [ ] Календар (Google Calendar, Outlook) для голосування
- [ ] GitHub Issues синхронізація
- [ ] Jira інтеграція для управління завданнями
- [ ] Webhook для зовнішніх систем

### Функціональність
- [ ] AI асистент для аналізу ідей (видобуток ключових слів, резюме)
- [ ] Рекомендація схожих ідей
- [ ] Повідомлення про дублікати ідей
- [ ] Система нагород та значків (gamification)
- [ ] Модерація контенту
- [ ] Система тегів та хештегів

### Мобільність
- [ ] Нативний мобільний додаток (iOS/Android)
- [ ] PWA (Progressive Web App)
- [ ] Offline підтримка
- [ ] Push-повідомлення

### Комунікація
- [ ] WebRTC для відеоконференцій
- [ ] Чат у реальному часі (Socket.io)
- [ ] Голосові коментарі
- [ ] Live обговорення ідей
- [ ] Синхронне редагування (як Google Docs)

### Безпека та дотримання
- [ ] GDPR компліанс
- [ ] HIPAA для медичних команд
- [ ] SSO (Single Sign-On) для підприємств
- [ ] Аудит логування
- [ ] Шифрування даних (E2E для приватних дошок)

---

**Версія:** 2.0.0  
**Дата оновлення:** 4 травня 2026 р.
