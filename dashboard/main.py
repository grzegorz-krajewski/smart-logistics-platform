import streamlit as st
import httpx
import pandas as pd

st.set_page_config(page_title="LogTech Dashboard", layout="wide")

st.title("🚚 Smart Logistics - Real-time Monitor")

# Funkcja do pobierania danych z FastAPI
def get_data(endpoint, timeout=5.0):
    try:
        response = httpx.get(f"http://127.0.0.1:8000{endpoint}", timeout=timeout)
        return response.json()
    except Exception as e:
        st.error(f"Błąd pobierania danych: {e}")
        return None

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
    shipments = get_data("/shipments/")
    if shipments:
        for ship in shipments:
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