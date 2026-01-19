import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Adres bazy z Twojego Docker Compose (user:password@host:port/dbname)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/logtech_platform"

# create_async_engine to odpowiednik konfiguracji w Symfony (doctrine.yaml)
# echo=True pozwoli nam widzieć w terminalu czyste zapytania SQL - super do nauki!
engine = create_async_engine(DATABASE_URL, echo=True)

# Fabryka sesji - asynchroniczny odpowiednik EntityManager
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Klasa bazowa dla wszystkich naszych modeli
Base = declarative_base()

# To jest Dependency Injection (DI) - FastAPI poda nam sesję do bazy w każdym requeście
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
