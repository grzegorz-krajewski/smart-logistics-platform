from fastapi import FastAPI

app = FastAPI(
    title="Smart Logistics Platform API",
    description="System do optymalizacji procesów magazynowych i transportowych",
    version="0.1.0"
)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "message": "Logistics Platform is running",
        "version": "0.1.0"
    }

@app.get("/ping", tags=["Health"])
async def ping():
    return {"pong": "Ready to scan pallets!"}
