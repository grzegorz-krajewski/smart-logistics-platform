from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.pallet import Pallet
from app.schemas.pallet import PalletCreate, PalletResponse
from app.models.dock import Dock
from app.schemas.dock import DockCreate, DockResponse
from app.redis_client import redis_client

app = FastAPI(title="Smart Logistics Platform API")

# Dodaj import na górze
from app.redis_client import redis_client

# Zaktualizuj endpoint POST /pallets/
@app.post("/pallets/", response_model=PalletResponse, tags=["Pallets"])
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

@app.get("/pallets/", response_model=list[PalletResponse], tags=["Pallets"])
async def get_all_pallets(db: AsyncSession = Depends(get_db)):
    query = select(Pallet)
    result = await db.execute(query)
    return result.scalars().all()

@app.post("/docks/", response_model=DockResponse, tags=["Docks"])
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

@app.get("/docks/", response_model=list[DockResponse], tags=["Docks"])
async def get_docks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Dock))
    return result.scalars().all()