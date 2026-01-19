# 🚚 Smart Logistics Platform (LogTech)

System backendowy klasy TMS/WMS zbudowany w **FastAPI** i **Python 3.12**, rozwiązujący krytyczne problemy operacyjne w branży TSL.

![alt text](https://github.com/grzegorz-krajewski/smart-logistics-platform/releases/download/0.3.0/Dashboard.png)

## 🚀 Rozwiązywane Problemy (Case Studies)

Projekt powstał w oparciu o 13-letnie doświadczenie w IT oraz praktykę w logistyce transportu ciężkiego (Cat. C).

1.  **Resilient Scanner (Problem Wi-Fi):** Mechanizm ochrony przed duplikatami skanów przy zrywającym się połączeniu (implementacja **Redis Idempotency**).
2.  **Real-time Handover:** Precyzyjne zarządzanie relacją Paleta-Rampa (Fine-grained Locking) zapobiegające "wyścigom" danych (Race Conditions).
3.  **Ghost Pickup Prevention:** (W trakcie) System powiadomień o zduplikowanych odbiorach towaru w czasie rzeczywistym.

## 🛠 Tech Stack

*   **Backend:** FastAPI (Asynchronous Python)
*   **Database:** PostgreSQL 16 + SQLAlchemy 2.0 (Async)
*   **Cache:** Redis 7.0 (Idempotency Locks)
*   **Migrations:** Alembic
*   **Infrastructure:** Docker & Docker Compose (M1/ARM64 Optimized)

## 🔧 Szybki Start

Instrukcja instalacji znajduje się w folderze [docs/setup_guide.md](./docs/setup_guide.md).

```bash
docker compose up -d
source .venv/bin/activate
uvicorn app.main:app --reload
