from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid

class Pallet(Base):
    __tablename__ = "pallets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    barcode = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="STAGED")
    weight = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    current_dock_id = Column(String, ForeignKey("docks.id"), nullable=True)
    dock = relationship("Dock")
    shipment_id = Column(String, ForeignKey("shipments.id"), nullable=True)

