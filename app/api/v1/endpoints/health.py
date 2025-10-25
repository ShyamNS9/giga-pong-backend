from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.base import get_db

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status": "healthy", "service": "Giga FastAPI"}


@router.get("/db")
async def database_health_check(db: Session = Depends(get_db)):
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
