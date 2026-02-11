from fastapi import APIRouter, Depends, HTTPException
from app.deps import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.pallet import Pallet
from app.models.dock import Dock
from app.models.shipment import Shipment
from app.schemas.pallet import PalletCreate, PalletResponse, PalletScanToDock
from app.redis_client import redis_client
from app.services.ai_engine import ai_engine

router = APIRouter()

# Używamy @router zamiast @app
@router.post("/", response_model=PalletResponse, tags=["Pallets"])
async def create_pallet(pallet_data: PalletCreate, db: AsyncSession = Depends(get_db)):
# --- LOGIKA REDIS (Ochrona przed Wi-Fi lags) ---
    redis_key = f"scan_lock:{pallet_data.barcode}"
    
    # Próbujemy ustawić klucz w Redisie na 10 sekund (NX = set if not exists)
    is_new_scan = await redis_client.set(redis_key, "locked", ex=10, nx=True)
    
    if not is_new_scan:
        # Jeśli klucz już był, to znaczy że to duplikat wysłany przez skaner
        raise HTTPException(status_code=400, detail="Duplicate scan detected. Please wait.")

    query = select(Pallet).where(Pallet.barcode == pallet_data.barcode)
    result = await db.execute(query)
    existing_pallet = result.scalar_one_or_none()
    
    if existing_pallet:
        raise HTTPException(status_code=400, detail="Barcode already scanned!")

    # 2. Stwórz nową paletę
    new_pallet = Pallet(
        barcode=pallet_data.barcode,
        weight=pallet_data.weight
    )
    
    db.add(new_pallet)
    await db.commit() # Tu fizycznie dane lecą do Postgresa
    await db.refresh(new_pallet) # Pobieramy wygenerowane ID i datę
    
    return new_pallet
    pass 

@router.get("/user")
async def list_shipments(current_user: User = Depends(get_current_user)):
    return {"ok": True, "user": current_user.username}

@router.get("/", response_model=list[PalletResponse], tags=["Pallets"])
async def get_all_pallets(db: AsyncSession = Depends(get_db)):
    query = select(Pallet)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/scan-to-dock", tags=["Pallets"])
async def scan_to_dock(data: PalletScanToDock, db: AsyncSession = Depends(get_db)):
    # REDIS LOCK (Zabezpieczenie przed szybkim dwuklikiem)
    lock_key = f"scan_lock:{data.barcode}"
    if not await redis_client.set(lock_key, "1", ex=5, nx=True):
        raise HTTPException(status_code=400, detail="Skan tej palety jest już przetwarzany...")

    # SQL LOCK (Blokujemy paletę do odczytu i zapisu)
    pallet_query = select(Pallet).where(Pallet.barcode == data.barcode).with_for_update() # Dodaj with_for_update!
    pallet_result = await db.execute(pallet_query)
    pallet = pallet_result.scalar_one_or_none()

    # Pobierz paletę i rampę
    pallet_query = select(Pallet).where(Pallet.barcode == data.barcode)
    pallet = (await db.execute(pallet_query)).scalar_one_or_none()

    # SPRAWDZENIE: Czy paleta już jest na jakiejś rampie?
    if pallet and pallet.current_dock_id is not None:
        raise HTTPException(status_code=400, detail="Ta paleta została już przypisana do rampy!")

    dock_query = select(Dock).where(Dock.number == data.dock_number)
    dock = (await db.execute(dock_query)).scalar_one_or_none()

    if not pallet or not dock:
        raise HTTPException(status_code=404, detail="Paleta lub Rampa nie istnieje")

    # Pobierz trasę przypisaną do tej rampy (jeśli rampa ma przypisany shipment_id)
    if not dock.current_shipment_id:
        raise HTTPException(status_code=400, detail="Rampa nie ma przypisanej aktywnej trasy")

    shipment_query = select(Shipment).where(Shipment.id == dock.current_shipment_id)
    shipment = (await db.execute(shipment_query)).scalar_one_or_none()

    # Obliczamy sumę wag palet już przypisanych do tej trasy
    weight_sum_query = select(func.sum(Pallet.weight)).where(Pallet.shipment_id == shipment.id)
    current_weight = (await db.execute(weight_sum_query)).scalar() or 0
    max_capacity = shipment.max_weight_capacity or 12000
    new_total_weight = current_weight + (pallet.weight or 0)

    if new_total_weight > max_capacity:
        raise HTTPException(
            status_code=400, 
            detail=f"PRZEŁADOWANIE! Obecna waga: {current_weight}kg, Nowa paleta: {pallet.weight}kg. Limit: {shipment.max_weight_capacity}kg"
        )

    # 4. Jeśli waga OK -> Przypisz paletę
    pallet.current_dock_id = dock.id
    pallet.shipment_id = shipment.id # Przypisujemy paletę do trasy
    pallet.status = "LOADING_TO_DOCK"
    
    await db.commit()
    return {
        "message": "Załadunek dozwolony", 
        "current_total_weight": new_total_weight,
        "capacity_left": shipment.max_weight_capacity - new_total_weight
    }

@router.get("/{barcode}/ai-check", tags=["Gen-AI"])
async def ai_check_pallet(barcode: str, db: AsyncSession = Depends(get_db)):
    # 1. Pobierz dane palety z bazy
    query = select(Pallet).where(Pallet.barcode == barcode)
    result = await db.execute(query)
    pallet = result.scalar_one_or_none()
    
    if not pallet:
        raise HTTPException(status_code=404, detail="Paleta nie znaleziona")
    
    # 2. Wywołaj analizę AI (pobiera dane z modelu)
    analysis = await ai_engine.analyze_pallet_safety(
        barcode=pallet.barcode,
        weight=pallet.weight or 0,
        status=pallet.status
    )
    
    return {
        "barcode": barcode,
        "ai_analysis": analysis
    }
