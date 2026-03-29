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
# CUSTOM CSS
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

    [data-testid="stAppViewContainer"] { background-color: #0e1117; }

    h1, h2, h3, h4, h5, h6, p, span, label, .st-bb { color: #ffffff !important; }

    div[data-testid="stInfo"] {
        background-color: #1a2a4a;
        border-left: 4px solid #0066ff;
        color: #ffffff !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    div[data-testid="stInfo"] * p,
    div[data-testid="stInfo"] * span,
    div[data-testid="stInfo"] * strong { color: #ffffff !important; }

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
# DATA (15 Supply + 15 Demand)
# ======================
if "supplies" not in st.session_state:
    st.session_state.supplies = [
        {"id": 1,  "item": "water",    "lokasi": "Gudang Logistik Pusat",    "lat": -6.2000, "lon": 106.8000, "qty": 100},
        {"id": 2,  "item": "food",     "lokasi": "Posko Bantuan Sudirman",   "lat": -6.2146, "lon": 106.8451, "qty": 50},
        {"id": 3,  "item": "medicine", "lokasi": "RSUD Tarakan",             "lat": -6.1751, "lon": 106.8272, "qty": 200},
        {"id": 4,  "item": "tent",     "lokasi": "Gudang Tenda Cengkareng",  "lat": -6.1263, "lon": 106.7377, "qty": 10},
        {"id": 5,  "item": "clothing", "lokasi": "Posko Pakaian Tebet",      "lat": -6.2587, "lon": 106.8207, "qty": 80},
        {"id": 6,  "item": "water",    "lokasi": "Depo Air Pulogadung",      "lat": -6.1800, "lon": 106.9000, "qty": 150},
        {"id": 7,  "item": "food",     "lokasi": "Dapur Umum Kebayoran",     "lat": -6.2400, "lon": 106.7000, "qty": 75},
        {"id": 8,  "item": "medicine", "lokasi": "Apotek Darurat Pasar Minggu", "lat": -6.3000, "lon": 106.8200, "qty": 120},
        {"id": 9,  "item": "tent",     "lokasi": "Gudang Tenda Kalideres",   "lat": -6.2200, "lon": 106.6500, "qty": 5},
        {"id": 10, "item": "clothing", "lokasi": "Gudang Pakaian Kelapa Gading", "lat": -6.1500, "lon": 106.8800, "qty": 60},
        {"id": 11, "item": "water",    "lokasi": "Depo Air Depok",           "lat": -6.3500, "lon": 106.7800, "qty": 90},
        {"id": 12, "item": "food",     "lokasi": "Dapur Umum Penjaringan",   "lat": -6.1000, "lon": 106.7500, "qty": 40},
        {"id": 13, "item": "medicine", "lokasi": "Klinik Darurat Bekasi",    "lat": -6.2800, "lon": 106.9500, "qty": 180},
        {"id": 14, "item": "tent",     "lokasi": "Gudang Tenda Ciputat",     "lat": -6.4000, "lon": 106.8500, "qty": 15},
        {"id": 15, "item": "clothing", "lokasi": "Posko Pakaian Tangerang",  "lat": -6.2000, "lon": 106.6000, "qty": 110},
    ]

if "demands" not in st.session_state:
    st.session_state.demands = [
        {"id": 101, "item": "water",    "lokasi": "Posko Pengungsian Tebet",      "lat": -6.2500, "lon": 106.8200, "urgency": 5, "qty_needed": 200},
        {"id": 102, "item": "food",     "lokasi": "Dapur Umum Pasar Minggu",      "lat": -6.3000, "lon": 106.8500, "urgency": 3, "qty_needed": 150},
        {"id": 103, "item": "medicine", "lokasi": "Tenda Medis Blok M",           "lat": -6.1500, "lon": 106.8000, "urgency": 4, "qty_needed": 50},
        {"id": 104, "item": "water",    "lokasi": "Pemukiman Kemayoran",          "lat": -6.2200, "lon": 106.7500, "urgency": 2, "qty_needed": 300},
        {"id": 105, "item": "tent",     "lokasi": "Pengungsian Penjaringan",      "lat": -6.1000, "lon": 106.7000, "urgency": 5, "qty_needed": 20},
        {"id": 106, "item": "water",    "lokasi": "Huntara Jatinegara",           "lat": -6.1950, "lon": 106.8550, "urgency": 4, "qty_needed": 120},
        {"id": 107, "item": "food",     "lokasi": "Pengungsian Kebayoran Lama",   "lat": -6.2100, "lon": 106.7800, "urgency": 5, "qty_needed": 100},
        {"id": 108, "item": "medicine", "lokasi": "Puskesmas Darurat Depok",      "lat": -6.3200, "lon": 106.8000, "urgency": 3, "qty_needed": 40},
        {"id": 109, "item": "tent",     "lokasi": "Kamp Pengungsi Ciledug",       "lat": -6.2800, "lon": 106.7200, "urgency": 4, "qty_needed": 15},
        {"id": 110, "item": "clothing", "lokasi": "Posko Kelapa Gading",          "lat": -6.1400, "lon": 106.8200, "urgency": 1, "qty_needed": 250},
        {"id": 111, "item": "water",    "lokasi": "Barak Pengungsi Bekasi Timur", "lat": -6.2600, "lon": 106.9200, "urgency": 5, "qty_needed": 180},
        {"id": 112, "item": "food",     "lokasi": "Dapur Umum Ciputat",           "lat": -6.3300, "lon": 106.8800, "urgency": 2, "qty_needed": 90},
        {"id": 113, "item": "medicine", "lokasi": "Tenda Medis Kalideres",        "lat": -6.1600, "lon": 106.7300, "urgency": 5, "qty_needed": 70},
        {"id": 114, "item": "tent",     "lokasi": "Kamp Sementara Tanah Abang",   "lat": -6.2300, "lon": 106.8100, "urgency": 3, "qty_needed": 10},
        {"id": 115, "item": "clothing", "lokasi": "Pengungsian Ciputat Timur",    "lat": -6.3800, "lon": 106.8300, "urgency": 4, "qty_needed": 130},
    ]

# Shorthand references
supplies = st.session_state.supplies
demands  = st.session_state.demands

# ======================
# COLORS
# ======================
SUPPLY_COLOR = "#28a745"
URGENCY_COLORS = {
    1: "#d4b520",
    2: "#ff9900",
    3: "#ff5500",
    4: "#cc0000",
    5: "#8b0000"
}
ALL_ITEMS = ["water", "food", "medicine", "tent", "clothing"]

# ======================
# FUNCTIONS
# ======================
def distance(lat1, lon1, lat2, lon2):
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2) ** 0.5

def get_route_osrm(lat1, lon1, lat2, lon2):
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    )
    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        if data["code"] == "Ok":
            route = data["routes"][0]
            dist_km   = round(route["distance"] / 1000, 1)
            time_min  = int(route["duration"] / 60)
            coords    = [[c[1], c[0]] for c in route["geometry"]["coordinates"]]
            return dist_km, time_min, coords
    except Exception:
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
    best, best_score = None, -1
    for d in list_of_demands:
        if supply["item"] == d["item"]:
            s = match_score(supply, d)
            if s > best_score:
                best_score, best = s, d
    return best, best_score

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
    ">{symbol}</div>
    """
    return folium.DivIcon(html=html_string, icon_size=(30,30), icon_anchor=(15,15), popup_anchor=(0,-15))

# ======================
# HEADER
# ======================
st.markdown("<h1 style='text-align: center;'>🚨 Disaster Logistic Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #a1a1aa;'>Match Supply dengan Demand secara otomatis berdasarkan jarak & urgensi</p>", unsafe_allow_html=True)
st.write("---")

# ======================
# TABS
# ======================
tab_map, tab_supply, tab_demand = st.tabs(["🗺️ Peta & Matching", "📦 Edit Supply", "🆘 Edit Demand"])

# ==============================
# TAB 1: PETA & MATCHING
# ==============================
with tab_map:
    col_left, col_right = st.columns([1, 3])

    with col_left:
        st.markdown("### 🔍 Filter")

        item_options = ["All"] + ALL_ITEMS
        search_query = st.selectbox("Pilih Kategori:", item_options)

        if "last_query" not in st.session_state:
            st.session_state.last_query = search_query
        elif st.session_state.last_query != search_query:
            st.session_state.match_result = None
            st.session_state.current_supply = None
            st.session_state.last_query = search_query

        if search_query == "All":
            filtered_supplies = supplies
            filtered_demands  = demands
            kategori_teks     = "Semua Kategori"
        else:
            filtered_supplies = [s for s in supplies if s["item"] == search_query]
            filtered_demands  = [d for d in demands  if d["item"] == search_query]
            kategori_teks     = search_query

        st.markdown("### 📊 Info Data")
        st.info(
            f"**Supply ({kategori_teks}):** {len(filtered_supplies)}\n\n"
            f"**Demand ({kategori_teks}):** {len(filtered_demands)}"
        )

        st.markdown("### 📍 Legenda")
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

        # Pilih supply mana yang mau di-match
        supply_labels = {s["id"]: f"#{s['id']} – {s['item']} ({s['lokasi'][:20]}…)" for s in filtered_supplies}
        if filtered_supplies:
            selected_supply_id = st.selectbox(
                "Supply yang akan di-match:",
                options=[s["id"] for s in filtered_supplies],
                format_func=lambda x: supply_labels[x]
            )
        else:
            selected_supply_id = None

        find_match_btn = st.button("🚀 Find Best Match", type="primary", use_container_width=True)

        if find_match_btn and selected_supply_id is not None:
            with st.spinner("Menghitung rute tercepat..."):
                supply_to_match = next(s for s in supplies if s["id"] == selected_supply_id)
                best_demand, best_score = find_best_match(supply_to_match, filtered_demands)
                if best_demand:
                    dist_km, time_min, route_coords = get_route_osrm(
                        supply_to_match["lat"], supply_to_match["lon"],
                        best_demand["lat"],     best_demand["lon"]
                    )
                    st.session_state.current_supply = supply_to_match
                    st.session_state.match_result   = {
                        "demand":      best_demand,
                        "score":       best_score,
                        "dist_km":     dist_km,
                        "time_min":    time_min,
                        "route_coords": route_coords
                    }
                else:
                    st.session_state.match_result = "NOT_FOUND"

    with col_right:
        m = folium.Map(location=[-6.23, 106.82], zoom_start=11, tiles="CartoDB positron")

        for s in filtered_supplies:
            folium.Marker(
                [s["lat"], s["lon"]],
                tooltip=f"<b>Supply:</b> {s['item']}<br><b>Lokasi:</b> {s['lokasi']}<br><b>Qty:</b> {s['qty']}",
                icon=create_custom_marker(SUPPLY_COLOR, "📦")
            ).add_to(m)

        for d in filtered_demands:
            hex_color = URGENCY_COLORS[d["urgency"]]
            folium.Marker(
                [d["lat"], d["lon"]],
                tooltip=f"<b>Demand:</b> {d['item']}<br><b>Urgensi:</b> Level {d['urgency']}<br><b>Lokasi:</b> {d['lokasi']}<br><b>Qty Needed:</b> {d['qty_needed']}",
                icon=create_custom_marker(hex_color, "!")
            ).add_to(m)

        if st.session_state.match_result and isinstance(st.session_state.match_result, dict):
            res   = st.session_state.match_result
            sup   = st.session_state.current_supply
            route = res["route_coords"]

            if route:
                folium.PolyLine(locations=route, color="#3399ff", weight=5, opacity=0.9).add_to(m)
                mid   = route[len(route) // 2]
                popup = f"""
                <div style="font-family:sans-serif;font-size:13px;min-width:250px;color:#1f2937;padding:10px;border-radius:5px;">
                    <h4 style="margin-top:0;color:#0066ff;">🚚 Route Details</h4>
                    <b>📍 Start:</b> {sup['lokasi']} (ID: {sup['id']})<br>
                    <b>🏁 End:</b> {res['demand']['lokasi']} (ID: {res['demand']['id']})<br>
                    <hr style="margin:8px 0;border:0;border-top:1px solid #ddd;">
                    <b>🛣️ Distance:</b> {res['dist_km']} km<br>
                    <b>⏱️ Est. Time:</b> {res['time_min']} mins<br>
                    <hr style="margin:8px 0;border:0;border-top:1px solid #ddd;">
                    <b>⭐ Match Score:</b> <span style="color:green;font-weight:bold;">{res['score']}</span>
                </div>
                """
                folium.Marker(
                    location=mid,
                    popup=folium.Popup(popup, max_width=350),
                    tooltip="Klik untuk melihat Detail Pengiriman",
                    icon=create_custom_marker("#0066ff", "🚚")
                ).add_to(m)

        st_folium(m, width="100%", height=650)

        if st.session_state.match_result == "NOT_FOUND":
            st.warning("⚠️ Tidak ditemukan Demand yang cocok untuk Supply yang dipilih.")

# ==============================
# TAB 2: EDIT SUPPLY
# ==============================
with tab_supply:
    st.markdown("### 📦 Data Supply")
    st.caption("Klik baris untuk mengedit, lalu tekan Save.")

    supply_ids = [s["id"] for s in supplies]
    sel_supply_id = st.selectbox(
        "Pilih Supply (ID) untuk diedit:",
        options=supply_ids,
        format_func=lambda x: f"#{x} – {next(s for s in supplies if s['id']==x)['item']} | {next(s for s in supplies if s['id']==x)['lokasi']}"
    )

    sel_supply = next(s for s in supplies if s["id"] == sel_supply_id)

    with st.form("form_edit_supply"):
        col1, col2 = st.columns(2)
        with col1:
            new_item   = st.selectbox("Item",  ALL_ITEMS, index=ALL_ITEMS.index(sel_supply["item"]))
            new_lokasi = st.text_input("Lokasi", value=sel_supply["lokasi"])
            new_qty    = st.number_input("Qty", min_value=0, value=sel_supply["qty"])
        with col2:
            new_lat = st.number_input("Latitude",  value=sel_supply["lat"], format="%.4f")
            new_lon = st.number_input("Longitude", value=sel_supply["lon"], format="%.4f")

        saved = st.form_submit_button("💾 Save Changes", type="primary")
        if saved:
            sel_supply["item"]   = new_item
            sel_supply["lokasi"] = new_lokasi
            sel_supply["qty"]    = new_qty
            sel_supply["lat"]    = new_lat
            sel_supply["lon"]    = new_lon
            st.success(f"✅ Supply #{sel_supply_id} berhasil diupdate!")
            st.rerun()

    st.write("---")
    st.markdown("#### 📋 Semua Data Supply")
    st.dataframe(
        [{k: v for k, v in s.items()} for s in supplies],
        use_container_width=True, hide_index=True
    )

    st.write("---")
    st.markdown("#### ➕ Tambah Supply Baru")
    with st.form("form_add_supply"):
        col1, col2 = st.columns(2)
        with col1:
            add_item   = st.selectbox("Item",   ALL_ITEMS, key="add_s_item")
            add_lokasi = st.text_input("Lokasi", key="add_s_lokasi")
            add_qty    = st.number_input("Qty", min_value=0, value=0, key="add_s_qty")
        with col2:
            add_lat = st.number_input("Latitude",  value=-6.2000, format="%.4f", key="add_s_lat")
            add_lon = st.number_input("Longitude", value=106.8000, format="%.4f", key="add_s_lon")
        added = st.form_submit_button("➕ Tambah", type="primary")
        if added:
            new_id = max(s["id"] for s in supplies) + 1
            st.session_state.supplies.append({
                "id": new_id, "item": add_item, "lokasi": add_lokasi,
                "lat": add_lat, "lon": add_lon, "qty": add_qty
            })
            st.success(f"✅ Supply baru ditambahkan dengan ID #{new_id}!")
            st.rerun()

    st.write("---")
    st.markdown("#### 🗑️ Hapus Supply")
    del_supply_id = st.selectbox(
        "Pilih Supply untuk dihapus:",
        options=supply_ids,
        format_func=lambda x: f"#{x} – {next(s for s in supplies if s['id']==x)['item']} | {next(s for s in supplies if s['id']==x)['lokasi']}",
        key="del_supply"
    )
    if st.button("🗑️ Hapus Supply ini", type="secondary"):
        st.session_state.supplies = [s for s in st.session_state.supplies if s["id"] != del_supply_id]
        st.success(f"✅ Supply #{del_supply_id} dihapus.")
        st.rerun()

# ==============================
# TAB 3: EDIT DEMAND
# ==============================
with tab_demand:
    st.markdown("### 🆘 Data Demand")

    demand_ids = [d["id"] for d in demands]
    sel_demand_id = st.selectbox(
        "Pilih Demand (ID) untuk diedit:",
        options=demand_ids,
        format_func=lambda x: f"#{x} – {next(d for d in demands if d['id']==x)['item']} | {next(d for d in demands if d['id']==x)['lokasi']}"
    )

    sel_demand = next(d for d in demands if d["id"] == sel_demand_id)

    with st.form("form_edit_demand"):
        col1, col2 = st.columns(2)
        with col1:
            new_d_item     = st.selectbox("Item", ALL_ITEMS, index=ALL_ITEMS.index(sel_demand["item"]))
            new_d_lokasi   = st.text_input("Lokasi", value=sel_demand["lokasi"])
            new_d_qty      = st.number_input("Qty Needed", min_value=0, value=sel_demand["qty_needed"])
            new_d_urgency  = st.slider("Urgency Level", 1, 5, value=sel_demand["urgency"])
        with col2:
            new_d_lat = st.number_input("Latitude",  value=sel_demand["lat"], format="%.4f")
            new_d_lon = st.number_input("Longitude", value=sel_demand["lon"], format="%.4f")

        saved_d = st.form_submit_button("💾 Save Changes", type="primary")
        if saved_d:
            sel_demand["item"]      = new_d_item
            sel_demand["lokasi"]    = new_d_lokasi
            sel_demand["qty_needed"]= new_d_qty
            sel_demand["urgency"]   = new_d_urgency
            sel_demand["lat"]       = new_d_lat
            sel_demand["lon"]       = new_d_lon
            st.success(f"✅ Demand #{sel_demand_id} berhasil diupdate!")
            st.rerun()

    st.write("---")
    st.markdown("#### 📋 Semua Data Demand")
    st.dataframe(
        [{k: v for k, v in d.items()} for d in demands],
        use_container_width=True, hide_index=True
    )

    st.write("---")
    st.markdown("#### ➕ Tambah Demand Baru")
    with st.form("form_add_demand"):
        col1, col2 = st.columns(2)
        with col1:
            add_d_item    = st.selectbox("Item",   ALL_ITEMS, key="add_d_item")
            add_d_lokasi  = st.text_input("Lokasi", key="add_d_lokasi")
            add_d_qty     = st.number_input("Qty Needed", min_value=0, value=0, key="add_d_qty")
            add_d_urgency = st.slider("Urgency Level", 1, 5, value=3, key="add_d_urgency")
        with col2:
            add_d_lat = st.number_input("Latitude",  value=-6.2500, format="%.4f", key="add_d_lat")
            add_d_lon = st.number_input("Longitude", value=106.8200, format="%.4f", key="add_d_lon")
        added_d = st.form_submit_button("➕ Tambah", type="primary")
        if added_d:
            new_id = max(d["id"] for d in demands) + 1
            st.session_state.demands.append({
                "id": new_id, "item": add_d_item, "lokasi": add_d_lokasi,
                "lat": add_d_lat, "lon": add_d_lon,
                "urgency": add_d_urgency, "qty_needed": add_d_qty
            })
            st.success(f"✅ Demand baru ditambahkan dengan ID #{new_id}!")
            st.rerun()

    st.write("---")
    st.markdown("#### 🗑️ Hapus Demand")
    del_demand_id = st.selectbox(
        "Pilih Demand untuk dihapus:",
        options=demand_ids,
        format_func=lambda x: f"#{x} – {next(d for d in demands if d['id']==x)['item']} | {next(d for d in demands if d['id']==x)['lokasi']}",
        key="del_demand"
    )
    if st.button("🗑️ Hapus Demand ini", type="secondary"):
        st.session_state.demands = [d for d in st.session_state.demands if d["id"] != del_demand_id]
        st.success(f"✅ Demand #{del_demand_id} dihapus.")
        st.rerun()
