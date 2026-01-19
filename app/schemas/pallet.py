from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PalletScanToDock(BaseModel):
    barcode: str
    dock_number: str
    
# To, co skaner wysyła do nas
class PalletCreate(BaseModel):
    barcode: str
    weight: Optional[int] = None

# To, co API wysyła z powrotem do skanera (z ID i datą)
class PalletResponse(BaseModel):
    id: str
    barcode: str
    status: str
    weight: Optional[int] = None
    current_dock_id: Optional[str] = None
    shipment_id: Optional[str] = None 
    created_at: datetime

    class Config:
        from_attributes = True
