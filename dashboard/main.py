import streamlit as st
import httpx
import pandas as pd

st.set_page_config(page_title="LogTech Dashboard", layout="wide")

st.title("🚚 Smart Logistics - Real-time Monitor")

BASE_URL = "http://127.0.0.1:8000"

# Funkcja do pobierania danych z FastAPI
def get_data(endpoint, timeout=5.0):
    try:
        response = httpx.get(f"{BASE_URL}{endpoint}", timeout=timeout)
        # Sprawdzamy, czy status jest OK (200)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API zwróciło błąd {response.status_code} dla {endpoint}")
            return [] # Zwracamy pustą listę zamiast None
    except Exception as e:
        st.error(f"Błąd połączenia: {e}")
        return [] # Zwracamy pustą listę w przypadku awarii

# Funkcja realizująca zadanie z FastAPI
def post_data(endpoint):
    """Uniwersalna funkcja do wysyłania komend do API (POST)"""
    try:
        response = httpx.post(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Błąd API: {response.status_code}"
    except Exception as e:
        return False, str(e)
        
# --- SIDEBAR: Statystyki Ogólne ---
st.sidebar.header("System Status")
st.sidebar.success("API: Online")
st.sidebar.info(f"Ostatnia aktualizacja: {pd.Timestamp.now().strftime('%H:%M:%S')}")

# --- KOLUMNA 1: Zajętość Ramp ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏢 Status Ramp (Docks)")
    docks = get_data("/docks/")
    if docks:
        for dock in docks:
            status_color = "🔴 Zajęta" if dock['is_occupied'] else "🟢 Wolna"
            st.info(f"**Rampa {dock['number']}** | Typ: {dock['dock_type']} | Status: {status_color}")
    else:
        st.warning("Brak skonfigurowanych ramp.")

# --- KOLUMNA 2: Weight Guard Monitor ---
with col2:
    st.subheader("⚖️ Załadunek Tras (Weight Guard)")
    all_shipments = get_data("/shipments/")
    loading_shipments = [s for s in all_shipments if s['status'] in ['LOADING', 'IN_PROGRESS']]

    # Sekcja 2: Twoja kluczowa sekcja - WERYFIKACJA ODBIORU (Ghost Pickup Prevention)
    pickup_verification = [s for s in all_shipments if s['status'] == 'COLLECTED']

    if pickup_verification:
        for ship in pickup_verification:
            # Tu możemy pobrać palety dla danej trasy
            pallets = get_data("/pallets/")
            current_weight = sum(p.get('weight') or 0 for p in pallets if p.get('shipment_id') == ship['id'])
            max_cap = ship.get('max_weight_capacity') or 12000 
            
            percent = min(current_weight / max_cap, 1.0) if max_cap > 0 else 0
            
            st.write(f"**Trasa: {ship['reference_number']}** ({ship['origin']} -> {ship['destination']})")
            st.progress(percent)
            st.caption(f"Waga: {current_weight}kg / {max_cap}kg ({(percent*100):.1f}%)")
    else:
        st.write("Brak aktywnych tras.")

st.divider()
st.subheader("🚚 Zarządzanie Odjazdami")

# Pobieramy trasy, które są w trakcie ładowania (zakładając, że masz taką listę)
# Jeśli nie, możemy pobrać wszystkie aktywne doki
docks = get_data("/docks/") # Twoja funkcja pobierająca dane

occupied_docks = [d for d in docks if d['is_occupied'] and d['current_shipment_id']]

if not occupied_docks:
    st.write("Brak aktywnych załadunków.")
else:
    for d in occupied_docks:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Rampa **{d['number']}**: Trasa w trakcie ładowania")
        with col2:
            shipment_id = d['current_shipment_id']
            if st.button(f"Wypuść {d['number']}", key=f"release_{d['number']}"):
                success, message = post_data(f"/shipments/{shipment_id}/release")
                
                if success:
                    st.success(f"Rampa {d['number']} została pomyślnie zwolniona!")
                    st.rerun()
                else:
                    st.error(f"Nie udało się zwolnić rampy: {message}")

# --- TABELA: Ostatnie Palety ---
st.divider()
st.subheader("📦 Ostatnio zeskanowane palety")
pallets_data = get_data("/pallets/")
if pallets_data:
    df = pd.DataFrame(pallets_data)
    st.table(df[['barcode', 'status', 'weight', 'created_at']].tail(10))

# --- SEKCJA: AUDYT STRATEGICZNY AI ---
st.divider()
st.subheader("🤖 Audyt Magazynu (Llama)")
if st.button('Uruchom Audyt AI'):
    with st.spinner('Llama 3 analizuje dane...'):
        audit_data = get_data("/shipments/ai-audit", timeout=60.0)
        
        if audit_data and 'warehouse_health_check' in audit_data:
            st.info(audit_data['warehouse_health_check'])
            st.caption(f"Analiza wygenerowana: {audit_data.get('timestamp')}")
        else:
            st.error("Nie udało się pobrać audytu AI.")