# 🚚 Smart Logistics Platform (LogTech)

System backendowy klasy TMS/WMS zbudowany w **FastAPI** i **Python 3.12**, rozwiązujący krytyczne problemy operacyjne w branży TSL przy użyciu nowoczesnych technologii, w tym **Generative AI**.

![alt text](https://github.com/grzegorz-krajewski/smart-logistics-platform/releases/download/0.3.0/Dashboard.png)

## 🚀 Rozwiązywane Problemy (Case Studies)

Projekt powstał w oparciu o rozwijające się potrzeby w logistyce transportu ciężkiego.

1.  **Resilient Scanner (Problem Wi-Fi):** Mechanizm ochrony przed duplikatami skanów przy zrywającym się połączeniu (implementacja **Redis Idempotency**).
2.  **Real-time Handover:** Precyzyjne zarządzanie relacją Paleta-Rampa (Fine-grained Locking) zapobiegające "wyścigom" danych (Race Conditions).
3.  **Weight Guard Engine:** Automatyczna kontrola masy całkowitej ładunku, zapobiegająca przeładowaniu pojazdów (Data Integrity).
4.  **Gen-AI Assistant (v0.6.0):** Inteligentny asystent analizujący bezpieczeństwo palet i statusy operacyjne w czasie rzeczywistym (Llama 3 / GPT-4o).

## 🛠 Tech Stack

*   **Backend:** FastAPI (Asynchronous Python 3.12)
*   **AI Engine:** LangChain + Ollama (Lokalna Llama 3) / OpenAI SDK
*   **Frontend/UI:** Streamlit (Real-time Dashboard)
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