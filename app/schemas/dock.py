from pydantic import BaseModel
from typing import Optional
from app.models.dock import DockType

class DockCreate(BaseModel):
    number: str
    dock_type: DockType = DockType.STANDARD

class DockResponse(BaseModel):
    id: str
    number: str
    dock_type: DockType
    is_occupied: bool
    current_shipment_id: Optional[str] = None

    class Config:
        from_attributes = True