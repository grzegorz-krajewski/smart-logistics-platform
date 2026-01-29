import enum
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid

class ShipmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COLLECTED = "COLLECTED" 
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"

class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    reference_number = Column(String, unique=True, index=True, nullable=False) # Numer zlecenia
    origin = Column(String, nullable=False)      # Punkt A
    destination = Column(String, nullable=False) # Punkt B
    status = Column(SQLEnum(ShipmentStatus), default=ShipmentStatus.PENDING)
    max_weight_capacity = Column(Integer, default=12000, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
