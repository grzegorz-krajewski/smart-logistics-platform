from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.dock import Dock
from app.schemas.dock import DockCreate, DockResponse
from app.redis_client import redis_client
from app.models.shipment import Shipment


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


@router.patch("/{dock_number}/assign-shipment/{ref_number}", tags=["Docks"])
async def assign_shipment_to_dock(dock_number: str, ref_number: str, db: AsyncSession = Depends(get_db)):
    # 1. Pobierz rampę i trasę
    dock_query = select(Dock).where(Dock.number == dock_number)
    shipment_query = select(Shipment).where(Shipment.reference_number == ref_number)
    
    dock = (await db.execute(dock_query)).scalar_one_or_none()
    shipment = (await db.execute(shipment_query)).scalar_one_or_none()

    if not dock or not shipment:
        raise HTTPException(status_code=404, detail="Rampa lub Trasa nie istnieje")

    # 2. Sprawdź, czy rampa nie jest już zajęta przez inną trasę
    if dock.is_occupied and dock.current_shipment_id != shipment.id:
        raise HTTPException(status_code=400, detail="Rampa jest już zajęta przez inną trasę!")

    # 3. Połącz trasę z rampą
    dock.current_shipment_id = shipment.id
    dock.is_occupied = True

    await db.commit()
    return {"message": f"Trasa {ref_number} została przypisana do rampy {dock_number}"}