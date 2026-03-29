# dummy data

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