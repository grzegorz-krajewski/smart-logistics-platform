from fastapi import FastAPI
from app.api.router import api_router

app = FastAPI(
    title="Smart Logistics Platform",
    description="System optymalizacji TSL (WMS/TMS)",
    version="0.2.1"
)

# Rejestrujemy wszystkie routery jednym poleceniem
app.include_router(api_router)