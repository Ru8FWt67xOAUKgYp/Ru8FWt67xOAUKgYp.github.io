 
import json
from py_gasbuddy import GasBuddy

def update_gas_data():
    gb = GasBuddy()
    # H3W 1X4 is in Montreal. 
    # Zip code search works for Canadian postal codes.
    stations = gb.get_stations(zip_code="H3W 1X4")
    
    # Extract name, price, and address for regular gas (Fuel Type 1)
    results = []
    for s in stations:
        # Check if regular gas price exists
        reg_price = s.get('fuel_types', {}).get('1', {}).get('price')
        if reg_price:
            results.append({
                "name": s.get('name'),
                "address": s.get('address'),
                "price": float(reg_price),
                "updated": s.get('fuel_types', {}).get('1', {}).get('posted_time')
            })
    
    # Sort by price (lowest first) and take top 20
    top_20 = sorted(results, key=lambda x: x['price'])[:20]
    
    with open('gas_prices.json', 'w') as f:
        json.dump(top_20, f, indent=4)

if __name__ == "__main__":
    update_gas_data()