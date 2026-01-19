import enum
from sqlalchemy import Column, String, Boolean, Enum as SQLEnum
from app.database import Base
import uuid

# Definiujemy typy ramp jako Enum
class DockType(str, enum.Enum):
    STANDARD = "STANDARD"
    COLD_CHAIN = "COLD_CHAIN"  # Chłodnia
    VAN_ACCESS = "VAN_ACCESS"  # Dla mniejszych aut / busów

class Dock(Base):
    __tablename__ = "docks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    number = Column(String, unique=True, index=True, nullable=False) # Np. "R-01"
    dock_type = Column(SQLEnum(DockType), default=DockType.STANDARD, nullable=False)
    is_occupied = Column(Boolean, default=False)
    current_shipment_id = Column(String, nullable=True)