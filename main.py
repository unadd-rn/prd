import streamlit as st
import folium
from streamlit_folium import st_folium
import requests

# ======================
# SETUP PAGE CONFIG
# ======================
st.set_page_config(
    page_title="Disaster Matcher", 
    page_icon="🚨", 
    layout="wide"
)

# ======================
# CUSTOM CSS (Premium Dark Mode UI)
# ======================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif !important; 
        color: #ffffff !important;
    }
    
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    [data-testid="stAppViewContainer"] {
        background-color: #0e1117; 
    }

    h1, h2, h3, h4, h5, h6, p, span, label, .st-bb {
        color: #ffffff !important; 
    }

    div[data-testid="stInfo"] {
        background-color: #1a2a4a; 
        border-left: 4px solid #0066ff;
        color: #ffffff !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    div[data-testid="stInfo"] * p, div[data-testid="stInfo"] * span, div[data-testid="stInfo"] * strong {
        color: #ffffff !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #262730 !important; 
        border-color: #444 !important;
        color: white !important;
    }
    div[data-baseweb="popover"] ul {
        background-color: #262730 !important;
        color: white !important;
    }

    h1 { margin-top: -30px; font-weight: 700; }

    /* CSS Khusus untuk Legenda */
    .legend-item { display: flex; align-items: center; margin-bottom: 8px; font-size: 14px; }
    .color-box { width: 16px; height: 16px; border-radius: 3px; margin-right: 10px; border: 1px solid rgba(255,255,255,0.2); }
</style>
""", unsafe_allow_html=True)

# ======================
# SESSION STATE
# ======================
if "match_result" not in st.session_state:
    st.session_state.match_result = None
if "current_supply" not in st.session_state:
    st.session_state.current_supply = None

# ======================
# DATA (Dummy)
# ======================
supplies = [
    {"id": 1, "item": "Water", "lokasi": "Gudang Logistik Pusat", "lat": -6.2000, "lon": 106.8000},
    {"id": 2, "item": "Food", "lokasi": "Posko Bantuan Sudirman", "lat": -6.1500, "lon": 106.8500},
    {"id": 3, "item": "Medicine", "lokasi": "RSUD Tarakan", "lat": -6.2200, "lon": 106.7500},
]

demands = [
    {"id": 101, "item": "Water", "lokasi": "Posko Pengungsian Tebet", "lat": -6.2500, "lon": 106.8200, "urgency": 5},
    {"id": 102, "item": "Food", "lokasi": "Dapur Umum Pasar Minggu", "lat": -6.3000, "lon": 106.8500, "urgency": 3},
    {"id": 103, "item": "Medicine", "lokasi": "Tenda Medis Blok M", "lat": -6.2800, "lon": 106.8000, "urgency": 4},
    {"id": 104, "item": "Water", "lokasi": "Pemukiman Kemayoran", "lat": -6.1800, "lon": 106.8200, "urgency": 1},
    {"id": 105, "item": "Water", "lokasi": "Huntara Jatinegara", "lat": -6.2200, "lon": 106.8700, "urgency": 2},
]

# ======================
# HEX COLORS (Presisi 100%)
# ======================
SUPPLY_COLOR = "#28a745"
URGENCY_COLORS = {
    1: "#d4b520", # Kuning Mustard (Tidak terlalu terang)
    2: "#ff9900", # Oranye
    3: "#ff5500", # Oranye Tua / Merah Terang
    4: "#cc0000", # Merah
    5: "#8b0000"  # Merah Gelap (Kritis)
}

# ======================
# FUNCTIONS
# ======================
def distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2) ** 0.5

def get_route_osrm(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        data = response.json()
        if data["code"] == "Ok":
            route = data["routes"][0]
            dist_km = route["distance"] / 1000
            time_min = route["duration"] / 60
            coordinates = route["geometry"]["coordinates"]
            route_coords = [[coord[1], coord[0]] for coord in coordinates]
            return round(dist_km, 1), int(time_min), route_coords
    except Exception as e:
        pass
    return None, None, None

def match_score(s, d):
    score = 0
    if s["item"] == d["item"]: score += 50
    dist = distance(s["lat"], s["lon"], d["lat"], d["lon"])
    score += max(0, 30 - dist * 100)
    score += d["urgency"] * 10
    return round(score, 2)

def find_best_match(supply, list_of_demands):
    best = None
    best_score = -1
    for d in list_of_demands:
        if supply["item"] == d["item"]:
            score = match_score(supply, d)
            if score > best_score:
                best_score = score
                best = d
    return best, best_score

# FUNGSI CUSTOM MARKER HTML: Agar warna marker persis sama dengan kode Hex
def create_custom_marker(bg_color, symbol):
    html_string = f"""
    <div style="
        background-color: {bg_color};
        width: 30px; height: 30px;
        border-radius: 50%;
        border: 2px solid white;
        display: flex; align-items: center; justify-content: center;
        color: white; font-weight: bold; font-family: sans-serif; font-size: 14px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.5);
    ">
        {symbol}
    </div>
    """
    # Mengembalikan objek DivIcon Folium
    return folium.DivIcon(
        html=html_string, 
        icon_size=(30, 30), 
        icon_anchor=(15, 15), 
        popup_anchor=(0, -15)
    )

# ======================
# UI HEADER
# ======================
st.markdown("<h1 style='text-align: center;'>🚨 Disaster Logistic Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a1a1aa;'>Match Supply dengan Demand secara otomatis berdasarkan jarak & urgensi</p>", unsafe_allow_html=True)
st.write("---")

# ======================
# LAYOUTING
# ======================
col_left, col_right = st.columns([1, 3])

with col_left:
    st.markdown("### 🔍 Search Supply")
    
    item_options = ["All"] + list(set([s["item"] for s in supplies]))
    search_query = st.selectbox("Pilih Kategori Supply:", item_options)
    
    if "last_query" not in st.session_state:
        st.session_state.last_query = search_query
    elif st.session_state.last_query != search_query:
        st.session_state.match_result = None
        st.session_state.current_supply = None
        st.session_state.last_query = search_query

    if search_query == "All":
        filtered_supplies, filtered_demands = supplies, demands
        kategori_teks = "Semua Kategori"
    else:
        filtered_supplies = [s for s in supplies if s["item"] == search_query]
        filtered_demands = [d for d in demands if d["item"] == search_query]
        kategori_teks = search_query
    
    st.markdown("### 📊 Info Data")
    st.info(f"**Supply ({kategori_teks}):** {len(filtered_supplies)}\n\n**Demand ({kategori_teks}):** {len(filtered_demands)}")
    
    # === LEGENDA PETA BARU (Kode Hex Asli, Teks Bersih tanpa embel-embel warna) ===
    st.markdown("### 📍 Map Legend")
    st.markdown(f"""
    <div style='background-color: #262730; padding: 15px; border-radius: 8px; font-size: 14px; border: 1px solid #444;'>
        <div class='legend-item'><div class='color-box' style='background-color: {SUPPLY_COLOR};'></div> Hijau: Supply / Gudang</div>
        <hr style='border: 0; border-top: 1px solid #444; margin: 10px 0;'>
        <b style='display: block; margin-bottom: 8px;'>Tingkat Urgensi Demand:</b>
        <div class='legend-item'><div class='color-box' style='background-color: {URGENCY_COLORS[1]};'></div> Level 1: Rendah</div>
        <div class='legend-item'><div class='color-box' style='background-color: {URGENCY_COLORS[2]};'></div> Level 2: Rendah-Sedang</div>
        <div class='legend-item'><div class='color-box' style='background-color: {URGENCY_COLORS[3]};'></div> Level 3: Sedang</div>
        <div class='legend-item'><div class='color-box' style='background-color: {URGENCY_COLORS[4]};'></div> Level 4: Tinggi</div>
        <div class='legend-item'><div class='color-box' style='background-color: {URGENCY_COLORS[5]};'></div> Level 5: Kritis</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    
    find_match_btn = st.button("🚀 Find Best Match", type="primary", use_container_width=True)

    if find_match_btn and len(filtered_supplies) > 0:
        with st.spinner('Menghitung rute tercepat...'):
            supply_to_match = filtered_supplies[0]
            best_demand, best_score = find_best_match(supply_to_match, filtered_demands)
            
            if best_demand:
                dist_km, time_min, route_coords = get_route_osrm(
                    supply_to_match["lat"], supply_to_match["lon"], 
                    best_demand["lat"], best_demand["lon"]
                )
                st.session_state.current_supply = supply_to_match
                st.session_state.match_result = {
                    "demand": best_demand, 
                    "score": best_score,
                    "dist_km": dist_km,
                    "time_min": time_min,
                    "route_coords": route_coords
                }
            else:
                st.session_state.match_result = "NOT_FOUND"

with col_right:
    # Peta Terang
    m = folium.Map(location=[-6.23, 106.82], zoom_start=12, tiles="CartoDB positron")

    # Marker Supply (Custom Icon Kotak Logistik: 📦)
    for s in filtered_supplies:
        folium.Marker(
            [s["lat"], s["lon"]],
            tooltip=f"<b>Supply:</b> {s['item']}<br><b>Lokasi:</b> {s['lokasi']}",
            icon=create_custom_marker(SUPPLY_COLOR, "📦")
        ).add_to(m)

    # Marker Demand (Custom Icon Tanda Seru: ! dengan warna persis)
    for d in filtered_demands:
        hex_color = URGENCY_COLORS[d["urgency"]]
        folium.Marker(
            [d["lat"], d["lon"]],
            tooltip=f"<b>Demand:</b> {d['item']}<br><b>Urgensi:</b> Level {d['urgency']}<br><b>Lokasi:</b> {d['lokasi']}",
            icon=create_custom_marker(hex_color, "!")
        ).add_to(m)

    # Marker Truk & Rute (Pop-up Terang)
    if st.session_state.match_result and isinstance(st.session_state.match_result, dict):
        res = st.session_state.match_result
        sup = st.session_state.current_supply
        route_coords = res["route_coords"]
        
        if route_coords:
            folium.PolyLine(locations=route_coords, color="#3399ff", weight=5, opacity=0.9).add_to(m)
            mid_idx = len(route_coords) // 2
            mid_point = route_coords[mid_idx]
            
            popup_html = f"""
            <div style="font-family: 'Inter', sans-serif; font-size: 13px; min-width: 250px; background-color: white; color: #1f2937; padding: 10px; border-radius: 5px;">
                <h4 style="margin-top:0; margin-bottom:10px; color:#0066ff;">🚚 Route Details</h4>
                <b>📍 Start:</b> {sup['lokasi']} (ID: {sup['id']})<br>
                <b>🏁 End:</b> {res['demand']['lokasi']} (ID: {res['demand']['id']})<br>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ddd;">
                <b>🛣️ Distance:</b> {res['dist_km']} km<br>
                <b>⏱️ Est. Time:</b> {res['time_min']} mins<br>
                <hr style="margin: 8px 0; border: 0; border-top: 1px solid #ddd;">
                <b>⭐ Match Score:</b> <span style="color:green; font-weight:bold;">{res['score']}</span>
            </div>
            """
            # Custom Marker Truk di tengah rute
            folium.Marker(
                location=mid_point,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip="Klik untuk melihat Detail Pengiriman",
                icon=create_custom_marker("#0066ff", "🚚")
            ).add_to(m)
            
    # Tinggi peta diubah menjadi 650px agar pasti lebih tinggi/menutupi seluruh area kiri
    st_folium(m, width="100%", height=650)

    if st.session_state.match_result == "NOT_FOUND":
        st.warning(f"⚠️ Tidak ditemukan Demand untuk Supply saat ini.")
# === UI ===
# === MAP ===
# === DATA ===
# 15 Data Supply
supplies = [
    {"id": 1, "item": "water", "lat": -6.2000, "lon": 106.8000, "qty": 100},
    {"id": 2, "item": "food", "lat": -6.2146, "lon": 106.8451, "qty": 50},
    {"id": 3, "item": "medicine", "lat": -6.1751, "lon": 106.8272, "qty": 200},
    {"id": 4, "item": "tent", "lat": -6.1263, "lon": 106.7377, "qty": 10},
    {"id": 5, "item": "clothing", "lat": -6.2587, "lon": 106.8207, "qty": 80},
    {"id": 6, "item": "water", "lat": -6.1800, "lon": 106.9000, "qty": 150},
    {"id": 7, "item": "food", "lat": -6.2400, "lon": 106.7000, "qty": 75},
    {"id": 8, "item": "medicine", "lat": -6.3000, "lon": 106.8200, "qty": 120},
    {"id": 9, "item": "tent", "lat": -6.2200, "lon": 106.6500, "qty": 5},
    {"id": 10, "item": "clothing", "lat": -6.1500, "lon": 106.8800, "qty": 60},
    {"id": 11, "item": "water", "lat": -6.3500, "lon": 106.7800, "qty": 90},
    {"id": 12, "item": "food", "lat": -6.1000, "lon": 106.7500, "qty": 40},
    {"id": 13, "item": "medicine", "lat": -6.2800, "lon": 106.9500, "qty": 180},
    {"id": 14, "item": "tent", "lat": -6.4000, "lon": 106.8500, "qty": 15},
    {"id": 15, "item": "clothing", "lat": -6.2000, "lon": 106.6000, "qty": 110},
]

# 15 Data Demand
demands = [
    {"id": 101, "item": "water", "lat": -6.2500, "lon": 106.8200, "urgency": 5, "qty_needed": 200},
    {"id": 102, "item": "food", "lat": -6.3000, "lon": 106.8500, "urgency": 3, "qty_needed": 150},
    {"id": 103, "item": "medicine", "lat": -6.1500, "lon": 106.8000, "urgency": 4, "qty_needed": 50},
    {"id": 104, "item": "water", "lat": -6.2200, "lon": 106.7500, "urgency": 2, "qty_needed": 300},
    {"id": 105, "item": "tent", "lat": -6.1000, "lon": 106.7000, "urgency": 5, "qty_needed": 20},
    {"id": 106, "item": "water", "lat": -6.1950, "lon": 106.8550, "urgency": 4, "qty_needed": 120},
    {"id": 107, "item": "food", "lat": -6.2100, "lon": 106.7800, "urgency": 5, "qty_needed": 100},
    {"id": 108, "item": "medicine", "lat": -6.3200, "lon": 106.8000, "urgency": 3, "qty_needed": 40},
    {"id": 109, "item": "tent", "lat": -6.2800, "lon": 106.7200, "urgency": 4, "qty_needed": 15},
    {"id": 110, "item": "clothing", "lat": -6.1400, "lon": 106.8200, "urgency": 1, "qty_needed": 250},
    {"id": 111, "item": "water", "lat": -6.2600, "lon": 106.9200, "urgency": 5, "qty_needed": 180},
    {"id": 112, "item": "food", "lat": -6.3300, "lon": 106.8800, "urgency": 2, "qty_needed": 90},
    {"id": 113, "item": "medicine", "lat": -6.1600, "lon": 106.7300, "urgency": 5, "qty_needed": 70},
    {"id": 114, "item": "tent", "lat": -6.2300, "lon": 106.8100, "urgency": 3, "qty_needed": 10},
    {"id": 115, "item": "clothing", "lat": -6.3800, "lon": 106.8300, "urgency": 4, "qty_needed": 130},
]

# fungsi edit data

def edit_supply(target_id, new_item=None, new_qty=None, new_lat=None, new_lon=None):
    """Mencari supply berdasarkan ID dan mengubah atributnya"""
    for s in supplies:
        if s["id"] == target_id:
            if new_item: s["item"] = new_item
            if new_qty is not None: s["qty"] = new_qty
            if new_lat is not None: s["lat"] = new_lat
            if new_lon is not None: s["lon"] = new_lon
            return True
    return False

def edit_demand(target_id, new_item=None, new_qty_needed=None, new_urgency=None, new_lat=None, new_lon=None):
    """Mencari demand berdasarkan ID dan mengubah atributnya"""
    for d in demands:
        if d["id"] == target_id:
            if new_item: d["item"] = new_item
            if new_qty_needed is not None: d["qty_needed"] = new_qty_needed
            if new_urgency is not None: d["urgency"] = new_urgency
            if new_lat is not None: d["lat"] = new_lat
            if new_lon is not None: d["lon"] = new_lon
            return True
    return False

# === SCORING ENGINE ===
# === SELECTION ENGINE ===
