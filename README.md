# ThinkBoard v2 - Collaborative Idea Board

A real-time collaborative platform for creating, discussing, and voting on ideas with built-in WebSocket-based voting system.

## 📋 Project Overview

ThinkBoard is a web application that enables teams to:
- Create boards for idea collection
- Add ideas to boards
- Vote on ideas in real-time via WebSocket
- Manage users and board access
- Receive email notifications on important events

## ✨ Key Features

### Board Management
- ✅ Create/Delete boards
- ✅ Add/Remove users from boards
- ✅ Set favorite boards
- ✅ Manage access (private/public)

### Idea Management
- ✅ Create ideas within boards
- ✅ Delete ideas (author only)
- ✅ Set voting end time
- ✅ Unique idea names within board

### Voting System
- ✅ Real-time voting via WebSocket
- ✅ Countdown timer
- ✅ Automatic voting completion
- ✅ Result notifications

### User Profile
- ✅ Profile editing
- ✅ Avatar upload
- ✅ Password management
- ✅ Account deletion

### Authentication
- ✅ Registration and login
- ✅ Google OAuth integration
- ✅ JWT tokens with refresh mechanism
- ✅ Rate limiting

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async web framework
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Pydantic** - Data validation
- **Celery** - Async tasks
- **Redis** - Caching & message broker

### Database
- **PostgreSQL** - Primary database
- **Redis** - Cache layer

### Development Tools
- **pytest** - Testing framework
- **locust** - Load testing
- **Docker** - Containerization
- **Docker Compose** - Container orchestration

### Security
- **JWT** - Token-based authentication
- **bcrypt** - Password hashing
- **python-slowapi** - Rate limiting

## 🏗️ Architecture

```
app/
├── api/               # API routes
│   └── v1/
│       ├── router.py
│       └── routers/
│           ├── auth.py      # Authentication
│           ├── board.py     # Boards
│           ├── idea.py      # Ideas
│           ├── profile.py   # User profiles
│           └── vote.py      # Voting (WebSocket)
├── crud/              # CRUD operations
├── services/          # Business logic
├── models/            # SQLAlchemy models
├── schemas/           # Pydantic schemas
├── core/              # Configuration & utilities
├── events/            # Event handlers
├── tasks/             # Celery tasks
└── db/                # Database config
```

## 🚀 Setup & Installation

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL
- Redis

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or pip
pip install -r requirements.txt
```

### Run with Docker Compose

```bash
docker-compose up -d
```

This will start:
- PostgreSQL
- Redis
- FastAPI application
- Celery worker

### Run Locally

```bash
# Install dependencies
uv sync

# Run migrations
alembic upgrade head

# Start server
uv run uvicorn app.main:app --reload

# In another terminal, run Celery
uv run celery -A app.core.celery_app worker --loglevel=info
```

## 🧪 Testing

### Run All Tests

```bash
uv run pytest tests/
```

### Run Specific Test Suite

```bash
uv run pytest tests/test_board_servide/
uv run pytest tests/test_idea_service/
uv run pytest tests/test_vote_service/
```

### Load Testing

```bash
# With web UI
uv run locust -f locustfile.py --host http://localhost:8000

# Headless mode (100 users, 10 seconds)
uv run locust -f locustfile.py --host http://localhost:8000 \
    --headless -u 100 -r 10 -t 10s
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user

### Boards
- `POST /api/v1/boards/create` - Create board
- `DELETE /api/v1/boards/{board_id}` - Delete board
- `POST /api/v1/boards/{board_id}/members` - Add user to board
- `DELETE /api/v1/boards/{board_id}/members/{user_id}` - Remove user
- `POST /api/v1/boards/{board_id}/favorite` - Add to favorites

### Ideas
- `POST /api/v1/boards/{board_id}/ideas/create` - Create idea
- `DELETE /api/v1/boards/{board_id}/ideas/{idea_id}` - Delete idea

### Voting (WebSocket)
- `WS /api/v1/boards/{board_id}/ideas/{idea_id}/vote/ws?token={token}` - WebSocket voting

### Profile
- `GET /api/v1/profile/me` - My profile
- `PATCH /api/v1/profile/me` - Update profile
- `POST /api/v1/profile/me/avatar` - Upload avatar
- `GET /api/v1/profile/{username}` - Public profile

## 🔌 WebSocket Implementation

### Connect to Voting

```javascript
const token = 'your_jwt_token';
const ideaId = 'idea-123';
const boardId = 'board-456';

const ws = new WebSocket(
  `ws://localhost:8000/api/v1/boards/${boardId}/ideas/${ideaId}/vote/ws?token=${token}`
);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};

// Vote
ws.send(JSON.stringify({ status: true }));  // Approve
ws.send(JSON.stringify({ status: false })); // Reject
```

### WebSocket Events

- `init` - Initialize voting state
- `vote_updated` - Vote updated
- `voting_already_finished` - Voting already finished
- `voting_finished` - Voting completed

## 📧 Email Notifications

Uses **Celery** for async email sending:
- User registration
- Added to board
- Removed from board
- Idea created
- Voting finished

## 🔐 Security Features

- JWT tokens with expiration
- bcrypt password hashing
- Rate limiting
- CORS configuration
- SQL injection protection (SQLAlchemy)

## 📊 Test Statistics

- ✅ 76 successful tests
- 0 failures
- Coverage: Core business logic

## 🗄️ Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

## 🤝 Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Solomon - Developer

## 📞 Contact

- GitHub: [repository link]
- Email: your_email@example.com

## 🎯 Future Enhancements

### User Management
- [ ] User groups (teams/departments)
- [ ] Friends & follow system
- [ ] Two-factor authentication (2FA via email/SMS)
- [ ] Registration via third-party services:
  - [ ] GitHub OAuth
  - [ ] Microsoft/Outlook OAuth
  - [ ] Apple ID OAuth
  - [ ] Facebook OAuth
- [ ] Session & device management
- [ ] User activity history

### Boards & Ideas
- [ ] Board archiving (with restore capability)
- [ ] Advanced access control:
  - [ ] Private boards (invite-only)
  - [ ] Public boards (open to all)
  - [ ] Password-protected boards
- [ ] Board search (global & by categories)
- [ ] Idea categorization & tags
- [ ] Photo/media attachments for ideas
- [ ] File attachments support
- [ ] Threaded comments on ideas
- [ ] Idea sorting (by rating, time, popularity)
- [ ] Board templates for quick start

### Statistics & Analytics
- [ ] User activity statistics:
  - [ ] Participation charts
  - [ ] Activity timeline
  - [ ] Favorite categories
- [ ] Board analytics:
  - [ ] Idea trends
  - [ ] Top contributors
  - [ ] Voting rankings
- [ ] Report export (PDF, CSV)
- [ ] KPI dashboard

### Voting System
- [ ] Multiple voting types:
  - [ ] Binary (Yes/No)
  - [ ] Rating (1-5 stars)
  - [ ] Multiple choice
  - [ ] Prioritization (drag-and-drop)
- [ ] Anonymous voting
- [ ] Weighted voting (based on role)
- [ ] Real-time voting results with charts

### Integrations
- [ ] Slack integration (idea notifications)
- [ ] Microsoft Teams integration
- [ ] Calendar (Google Calendar, Outlook) for voting
- [ ] GitHub Issues sync
- [ ] Jira integration for task management
- [ ] Webhooks for external systems

### Features
- [ ] AI assistant for idea analysis (keyword extraction, summarization)
- [ ] Similar ideas recommendation
- [ ] Duplicate idea detection
- [ ] Reward & badge system (gamification)
- [ ] Content moderation
- [ ] Tag & hashtag system

### Mobile
- [ ] Native mobile app (iOS/Android)
- [ ] PWA (Progressive Web App)
- [ ] Offline support
- [ ] Push notifications

### Communication
- [ ] WebRTC for video conferencing
- [ ] Real-time chat (Socket.io)
- [ ] Voice comments
- [ ] Live idea discussions
- [ ] Collaborative editing (like Google Docs)

### Security & Compliance
- [ ] GDPR compliance
- [ ] HIPAA for medical teams
- [ ] SSO (Single Sign-On) for enterprises
- [ ] Audit logging
- [ ] Data encryption (E2E for private boards)

---

**Version:** 2.0.0  
**Last Updated:** May 4, 2026
