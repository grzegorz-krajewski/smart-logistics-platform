from fastapi import APIRouter
from app.api.endpoints import pallets, docks, shipments

api_router = APIRouter()

api_router.include_router(pallets.router, prefix="/pallets", tags=["Pallets"])
api_router.include_router(docks.router, prefix="/docks", tags=["Docks"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["Shipments"])
