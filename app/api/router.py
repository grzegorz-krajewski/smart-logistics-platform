from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.api.endpoints import pallets, docks, shipments, auth

api_router = APIRouter(prefix="/api")

# PUBLIC
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# PROTECTED
api_router.include_router(
    pallets.router,
    prefix="/pallets",
    tags=["pallets"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    docks.router,
    prefix="/docks",
    tags=["docks"],
    dependencies=[Depends(get_current_user)],
)
api_router.include_router(
    shipments.router,
    prefix="/shipments",
    tags=["shipments"],
    dependencies=[Depends(get_current_user)],
)
