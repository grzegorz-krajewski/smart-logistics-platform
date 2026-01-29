import os
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

class LogisticsAI:
    def __init__(self, mode="mock"):
        """
        mode: 'mock' (testy), 'openai' (chmura), 'ollama' (lokalnie na M1)
        """
        self.mode = mode
        
        # Klient OpenAI (zadziała, gdy w .env podasz klucz)
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Adres lokalnej Ollamy
        self.ollama_url = "http://localhost:11434/api/generate"

    async def analyze_pallet_safety(self, barcode: str, weight: int, status: str):
        # 1. TRYB MOCK (Na wyjazd - zero transferu, zero kosztów)
        if self.mode == "mock":
            return f"[MOCK AI] Analiza palety {barcode}: Parametry w normie. Status {status} poprawny dla wagi {weight}kg."

        # 2. TRYB OPENAI (Chmura - wymaga klucza API w .env)
        if self.mode == "openai":
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Jesteś ekspertem logistyki WMS."},
                        {"role": "user", "content": f"Oceń bezpieczeństwo palety {barcode}, waga {weight}kg, status {status}."}
                    ],
                    max_tokens=100
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Błąd OpenAI: {str(e)}"

        if self.mode == "ollama":
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "model": "llama3",
                        "prompt": f"Jesteś ekspertem logistyki. Czy paleta {barcode} ({weight}kg) jest bezpieczna? Odpowiedz krótko.",
                        "stream": False
                    }
                    response = await client.post(self.ollama_url, json=payload, timeout=30.0)
                    if response.status_code == 200:
                        return response.json().get("response")
                    return "Ollama jest zainstalowana, ale model Llama3 nie jest uruchomiony."
            except Exception:
                return "Błąd: Nie znaleziono lokalnego serwera Ollama. Czy jest włączony?"

        return "Nieznany tryb pracy AI."

    async def analyze_warehouse_state(self, docks_data: list, shipments_data: list):
        docks_info = "\n".join([f"- Rampa {d.number}: {'ZAJĘTA' if d.is_occupied else 'WOLNA'}" for d in docks_data])
        ship_info = "\n".join([f"- Trasa {s.reference_number} do {s.destination}: {s.status}" for s in shipments_data])

        prompt = f"""
        [INST] Jesteś ekspertem logistyki i kierownikiem polskiego magazynu. 
        Przeanalizuj poniższy stan obiektu i odpowiedz WYŁĄCZNIE W JĘZYKU POLSKIM.
        
        RAMPY:
        {docks_info}
        
        AKTYWNE TRASY:
        {ship_info}
        
        Zrób krótką analizę (max 3 konkretne punkty):
        1. Czy są wąskie gardła (brak wolnych ramp) (weź pod uwadę rampe oznaczoną WOLNA)?
        2. Czy trasy oczekujące mają przypisane miejsce?
        3. Jaki jest najważniejszy krok na teraz? [/INST]
        """

        async with httpx.AsyncClient() as client:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 200, 
                    "temperature": 0.2
                }
            }
            response = await client.post(self.ollama_url, json=payload, timeout=60.0)
            return response.json().get("response") if response.status_code == 200 else "Błąd: AI nie odpowiedziało."

# Inicjalizacja silnika - na wyjeździe zostaw "mock"
ai_engine = LogisticsAI(mode="mock")
