# Giga FastAPI

A professional FastAPI boilerplate with PostgreSQL integration.

## Features

- FastAPI framework
- PostgreSQL database with SQLAlchemy ORM
- Alembic for database migrations
- Pydantic for data validation
- Environment-based configuration
- CORS middleware
- Health check endpoints
- Modular structure

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

## Setup

1. Create and activate virtual environment:
```bash
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file

4. Run database migrations:
```bash
alembic upgrade head
```

5. Run the application:
```bash
uvicorn app.main:app --reload
```

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

- Application: http://localhost:8000/health
- Database: http://localhost:8000/api/v1/health/db
