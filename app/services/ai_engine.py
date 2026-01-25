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
        
        # Adres lokalnej Ollamy na Twoim Macu
        self.ollama_url = "http://127.0.0.1:11434/api/generate"

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

        # 3. TRYB OLLAMA (Lokalnie na M1 - darmowe AI w niedzielę)
        if self.mode == "ollama":
            try:
                async with httpx.AsyncClient() as client:
                    payload = {
                        "model": "llama3",
                        "prompt": f"Jesteś szybkim asystentem WMS. Paleta {barcode}, waga {weight}kg, status {status}. Czy jest OK? Odpowiedz w 5 słowach.",
                        "stream": False,
                        "options": {
                            "num_predict": 20,     # Bardzo krótka odpowiedź = szybka odpowiedź
                            "temperature": 0.2,    # Mniejsza kreatywność = większa szybkość
                            "top_k": 10            # Ogranicza wybór słów
                        }
                    }
                    response = await client.post(self.ollama_url, json=payload, timeout=60.0)
                    if response.status_code == 200:
                        return response.json().get("response")
                    return "Błąd Ollama"
            except Exception as e:
                return f"Błąd połączenia: {str(e)}"
            
        return "Nieznany tryb pracy AI."

# Inicjalizacja silnika - na wyjeździe zostaw "mock"
ai_engine = LogisticsAI(mode="ollama")
