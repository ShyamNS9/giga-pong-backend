# Giga Pong - Backend

Real-time multiplayer Pong game backend built with FastAPI and WebSockets.

**Live Demo:** https://giga-pong-backend.onrender.com
**Frontend:** https://giga-pong.netlify.app

## Features

- **Real-time WebSocket communication** for multiplayer gameplay
- **60 FPS game loop** with server-authoritative game state
- **4-directional paddle movement** (WASD + Arrow keys)
- **Ball physics** with randomized trajectories and collision detection
- **PostgreSQL database** with SQLAlchemy ORM
- **FastAPI framework** with automatic API documentation
- **Alembic migrations** for database version control
- **CORS middleware** for frontend integration
- **Health check endpoints** for monitoring

## Project Structure

```
giga_fastapi/
├── alembic/                # Database migrations
│   ├── versions/           # Migration files
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/  # API endpoints
│   │       │   └── health.py
│   │       └── api.py      # API router
│   ├── core/               # Core functionality
│   │   └── config.py       # Configuration
│   ├── db/                 # Database
│   │   └── base.py         # Database session
│   ├── models/             # SQLAlchemy models
│   │   └── user.py
│   ├── schemas/            # Pydantic schemas
│   │   └── user.py
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   └── main.py             # Application entry point
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .gitignore
├── alembic.ini             # Alembic configuration
├── requirements.txt
└── README.md
```

## Local Development Setup

### 1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables

Copy `.env.example` to `.env` and update the values:
```bash
cp .env.example .env
```

Required environment variables:
- `POSTGRES_SERVER` - Database hostname (localhost for local)
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password
- `POSTGRES_DB` - Database name
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `BACKEND_CORS_ORIGINS` - Allowed frontend URLs

### 4. Start PostgreSQL database

Make sure PostgreSQL is running locally:
```bash
# macOS (with Homebrew)
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
# Start PostgreSQL from Services
```

### 5. Create database:
```bash
createdb giga_db
```

### 6. Run database migrations:
```bash
alembic upgrade head
```

### 7. Run the application:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at http://localhost:8000

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback migrations:
```bash
alembic downgrade -1
```

## Health Checks

- Application: http://localhost:8000/api/v1/health/
- Database: http://localhost:8000/api/v1/health/db

## Production Deployment (Render.com)

### Prerequisites
- GitHub account
- Render.com account (free tier)

### Steps

1. **Create PostgreSQL Database on Render**
   - Go to https://dashboard.render.com
   - Click "New" → "PostgreSQL"
   - Name: `giga-pong-db`
   - Select free tier
   - Click "Create Database"
   - Copy the **Internal Database URL**

2. **Create Web Service on Render**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name:** `giga-pong-backend`
     - **Build Command:** `pip install -r requirements.txt`
     - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**

   Go to Environment tab and add:
   ```
   API_V1_STR=/api/v1
   PROJECT_NAME=Giga FastAPI
   BACKEND_CORS_ORIGINS=["https://giga-pong.netlify.app"]
   POSTGRES_SERVER=<from-render-db-hostname>
   POSTGRES_USER=<from-render-db>
   POSTGRES_PASSWORD=<from-render-db>
   POSTGRES_DB=<from-render-db>
   POSTGRES_PORT=5432
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (3-5 minutes)
   - Your backend will be live!

### Keep Backend Alive (Prevent Sleep)

Render free tier sleeps after 15 minutes of inactivity. Use cron-job.org to keep it alive:

1. Go to https://console.cron-job.org/
2. Create new cron job:
   - **URL:** `https://giga-pong-backend.onrender.com/api/v1/health/`
   - **Interval:** Every 12 minutes
3. Save and enable

## Game Architecture

### WebSocket Endpoints

- `/api/v1/game/ws/{player_id}` - WebSocket connection for players
  - `player_id`: "player1" or "player2"

### Message Types

**Client → Server:**
```json
{
  "type": "input",
  "action": "UP" | "DOWN" | "LEFT" | "RIGHT"
}
```

```json
{
  "type": "reset"
}
```

**Server → Client:**
```json
{
  "type": "game_state",
  "data": {
    "paddle1": {"x": 10, "y": 250, "width": 10, "height": 100},
    "paddle2": {"x": 780, "y": 250, "width": 10, "height": 100},
    "ball": {"x": 400, "y": 300, "radius": 8, "dx": 5, "dy": 3},
    "score1": 0,
    "score2": 0,
    "canvas_width": 800,
    "canvas_height": 600
  }
}
```

## Tech Stack

- **FastAPI** - Modern Python web framework
- **WebSockets** - Real-time bidirectional communication
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Relational database
- **Alembic** - Database migration tool
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## License

MIT
