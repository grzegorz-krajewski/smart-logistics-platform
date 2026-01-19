from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Pallet(Base):
    __tablename__ = "pallets"

    # Używamy UUID jako ID - w logistyce to bezpieczniejsze niż zwykłe cyfry (1, 2, 3)
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Barcode to unikalny numer, który będziesz skanował iPhonem
    barcode = Column(String, unique=True, index=True, nullable=False)
    
    # Statusy: STAGED (na buforze), IN_TRANSIT (na aucie), DELIVERED (u klienta)
    status = Column(String, default="STAGED")
    
    # Kiedy paleta weszła do systemu
    created_at = Column(DateTime(timezone=True), server_default=func.now())
