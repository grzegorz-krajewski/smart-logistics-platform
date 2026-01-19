from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.redis_client import redis_client
from app.models.shipment import Shipment, ShipmentStatus
from app.schemas.shipment import ShipmentCreate, ShipmentResponse

router = APIRouter()

@router.get("/check-pickup/{ref_number}", tags=["Shipments"])
async def check_pickup_status(ref_number: str, db: AsyncSession = Depends(get_db)):
    query = select(Shipment).where(Shipment.reference_number == ref_number)
    shipment = (await db.execute(query)).scalar_one_or_none()

    if not shipment:
        raise HTTPException(status_code=404, detail="Nie znaleziono takiego zlecenia.")

    if shipment.status == ShipmentStatus.COLLECTED:
        return {
            "alert": "STOP! Towar już odebrany przez innego kierowcę!",
            "status": shipment.status,
            "can_proceed": False
        }
    
    return {
        "message": "Zlecenie wolne. Możesz jechać.",
        "status": shipment.status,
        "can_proceed": True
    }

# Dodawanie nowej trasy (Shipment)
@router.post("/", response_model=ShipmentResponse, tags=["Shipments"])
async def create_shipment(data: ShipmentCreate, db: AsyncSession = Depends(get_db)):
    # Sprawdź czy numer referencyjny jest unikalny
    query = select(Shipment).where(Shipment.reference_number == data.reference_number)
    existing = (await db.execute(query)).scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=400, detail="Shipment with this ref number already exists")

    new_shipment = Shipment(**data.model_dump())
    db.add(new_shipment)
    await db.commit()
    await db.refresh(new_shipment)
    return new_shipment

# Pobieranie listy wszystkich tras
@router.get("/", response_model=list[ShipmentResponse], tags=["Shipments"])
async def get_shipments(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Shipment))
    return result.scalars().all()

# "Ghost Pickup Finder" - aktualizacja statusu (symulacja odbioru przez kogoś innego)
@router.patch("/collect/{ref_number}", tags=["Shipments"])
async def mark_as_collected(ref_number: str, db: AsyncSession = Depends(get_db)):
    query = select(Shipment).where(Shipment.reference_number == ref_number)
    shipment = (await db.execute(query)).scalar_one_or_none()
    
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
        
    shipment.status = ShipmentStatus.COLLECTED
    await db.commit()
    return {"message": f"Shipment {ref_number} marked as COLLECTED by another driver"}

