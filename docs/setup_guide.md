# Smart Logistics Platform - Setup Guide

Dokumentacja techniczna dla deweloperów. System zbudowany w oparciu o FastAPI, PostgreSQL i Redis, zoptymalizowany pod architekturę Apple Silicon (M1/M2).

## 🚀 Szybki Start

### 1. Przygotowanie środowiska Python
```bash
# Stworzenie środowiska wirtualnego
python3 -m venv .venv

# Aktywacja środowiska
source .venv/bin/activate

# Aktualizacja pip i instalacja bibliotek
pip install --upgrade pip
pip install -r requirements.txt

# Uruchomienie bazy danych (Postgres 16) i Redisa (7.0)
docker compose up -d

# Sprawdzenie czy kontenery działają (logtech_db, logtech_redis, logtech_adminer)
docker ps

# Ustawienie ścieżki (jeśli jesteś w głównym folderze)
export PYTHONPATH=$PYTHONPATH:.

# Aktualizacja bazy danych do najnowszej wersji
alembic upgrade head

# Generowanie nowej migracji (tylko przy zmianach w kodzie modeli)
# alembic revision --autogenerate -m "Description of changes"

# Start serwera z automatycznym przeładowaniem kodu
uvicorn app.main:app --reload

# Standardowy workflow commita połączonego z taskiem na tablicy
git add .
git commit -m "feat: short description #task_number"
git push origin main

### Dokumentacja:
1. W VS Code stwórz plik `docs/setup_guide.md`.
2. Wklej powyższą treść i zapisz.
3. W terminalu: 
   ```bash
   git add docs/setup_guide.md
   git commit -m "docs: create comprehensive setup guide for development"
   git push origin main