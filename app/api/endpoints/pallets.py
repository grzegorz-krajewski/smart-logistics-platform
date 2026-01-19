from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.pallet import Pallet
from app.models.dock import Dock
from app.schemas.pallet import PalletCreate, PalletResponse, PalletScanToDock
from app.redis_client import redis_client

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

@router.get("/", response_model=list[PalletResponse], tags=["Pallets"])
async def get_all_pallets(db: AsyncSession = Depends(get_db)):
    query = select(Pallet)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/scan-to-dock", tags=["Pallets"])
async def scan_to_dock(data: PalletScanToDock, db: AsyncSession = Depends(get_db)):
    # 1. Pobierz paletę
    pallet_query = select(Pallet).where(Pallet.barcode == data.barcode)
    pallet = (await db.execute(pallet_query)).scalar_one_or_none()
    
    # 2. Pobierz rampę
    dock_query = select(Dock).where(Dock.number == data.dock_number)
    dock = (await db.execute(dock_query)).scalar_one_or_none()

    if not pallet or not dock:
        raise HTTPException(status_code=404, detail="Paleta lub Rampa nie istnieje")

    # 3. Double Scan Protection (którą dodaliśmy na końcu)
    if pallet.current_dock_id is not None:
        raise HTTPException(
            status_code=400, 
            detail=f"Paleta jest już przypisana do innej rampy"
        )

    # 4. Logika biznesowa
    pallet.current_dock_id = dock.id
    pallet.status = "LOADING_TO_DOCK"
    dock.is_occupied = True 
    
    await db.commit()
    await db.refresh(pallet)
    
    return {"message": f"Paleta {pallet.barcode} przypisana do rampy {dock.number}"}
