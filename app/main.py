from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.pallet import Pallet
from app.schemas.pallet import PalletCreate, PalletResponse

app = FastAPI(title="Smart Logistics Platform API")

# Twoja pierwsza "produkcyjna" funkcja asynchroniczna
@app.post("/pallets/", response_model=PalletResponse, tags=["Pallets"])
async def create_pallet(pallet_data: PalletCreate, db: AsyncSession = Depends(get_db)):
    # 1. Sprawdź czy paleta o tym barcodzie już istnieje (Unique Check)
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

# Dodajmy też listowanie palet, żebyś widział co jest w bazie
@app.get("/pallets/", response_model=list[PalletResponse], tags=["Pallets"])
async def get_all_pallets(db: AsyncSession = Depends(get_db)):
    query = select(Pallet)
    result = await db.execute(query)
    return result.scalars().all()
