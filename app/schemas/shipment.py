from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.shipment import ShipmentStatus

class ShipmentCreate(BaseModel):
    reference_number: str
    origin: str
    destination: str
    status: Optional[ShipmentStatus] = ShipmentStatus.PENDING

class ShipmentResponse(BaseModel):
    id: str
    reference_number: str
    origin: str
    destination: str
    status: ShipmentStatus
    max_weight_capacity: int
    created_at: datetime

    class Config:
        from_attributes = True
