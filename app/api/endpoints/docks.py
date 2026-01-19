from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.dock import Dock
from app.schemas.dock import DockCreate, DockResponse
from app.redis_client import redis_client

router = APIRouter()

@router.post("/", response_model=DockResponse, tags=["Docks"])
async def create_dock(dock_data: DockCreate, db: AsyncSession = Depends(get_db)):
    # Sprawdź czy numer rampy się nie powtarza
    query = select(Dock).where(Dock.number == dock_data.number)
    result = await db.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dock number already exists")

    new_dock = Dock(**dock_data.model_dump())
    db.add(new_dock)
    await db.commit()
    await db.refresh(new_dock)
    return new_dock

@router.get("/", response_model=list[DockResponse], tags=["Docks"])
async def get_docks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dock))
    return result.scalars().all()
