from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.db.dependencies import get_db

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/database")
def check_database(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "ok"}

