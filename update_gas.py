import requests
import json
import sys
import os
from datetime import datetime

def fetch_free_gas():
    # Montreal H3W 1X4 Search
    # This endpoint is generally more open than their GraphQL one
    url = "https://www.gasbuddy.com/assets-v2/api/stations"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "Accept": "application/json"
    }
    
    params = {
        "search": "H3W 1X4",
        "fuel": 1 # 1 = Regular
    }

    try:
        # Load history for the Price Drop badge
        prev_min = 0
        if os.path.exists('gas_prices.json'):
            with open('gas_prices.json', 'r') as f:
                history = json.load(f)
                prev_min = history.get("current_min", 0)

        response = requests.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        stations = data.get('stations', [])
        processed = []
        
        for s in stations:
            # Extract price - GasBuddy often nests this in 'prices'
            price_entry = next((p for p in s.get('prices', []) if p.get('fuel_type') == 'regular'), None)
            price = float(price_entry.get('price')) if price_entry else 0
            
            if price > 0:
                processed.append({
                    "name": s.get('name', 'Station'),
                    "address": s.get('address', 'Montreal'),
                    "price": price
                })

        # Sort by cheapest
        sorted_list = sorted(processed, key=lambda x: x['price'])
        current_min = sorted_list[0]['price'] if sorted_list else 0

        output = {
            "last_updated": datetime.now().strftime("%b %d, %H:%M"),
            "prev_min": prev_min,
            "current_min": current_min,
            "stations": sorted_list[:12]
        }

        with open('gas_prices.json', 'w') as f:
            json.dump(output, f, indent=4)
        
        print(f"Updated: {len(processed)} stations found. Low: {current_min}¢")

    except Exception as e:
        print(f"Fetch failed: {e}")
        # Create a dummy file so the HTML doesn't crash if it's the first run
        if not os.path.exists('gas_prices.json'):
            with open('gas_prices.json', 'w') as f:
                json.dump({"stations": [], "last_updated": "Error", "current_min": 0, "prev_min": 0}, f)
        sys.exit(1)

if __name__ == "__main__":
    fetch_free_gas()