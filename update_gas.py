import os
import requests
import json
import sys
from datetime import datetime

def fetch_zyla_gas():
    api_key = os.getenv("ZYLA_API_KEY")
    if not api_key:
        print("Error: ZYLA_API_KEY secret is missing.")
        sys.exit(1)

    # Zyla Real-Time Canadian Fuel Prices API
    url = "https://zylalabs.com/api/6855/real-time+canadian+fuel+prices+api/11000/get+prices"
    headers = {'Authorization': f'Bearer {api_key}'}
    params = {'postal_code': 'H3W 1X4'}

    try:
        # 1. Load existing data to get the previous minimum price
        try:
            with open('gas_prices.json', 'r') as f:
                old_data = json.load(f)
                prev_min = old_data.get("current_min", 0)
        except:
            prev_min = 0

        # 2. Fetch new data
        response = requests.get(url, headers=headers, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        raw_stations = data.get('result', [])
        if not raw_stations:
            print("No data in API response.")
            sys.exit(1)

        # 3. Process and Sort
        processed = []
        for s in raw_stations:
            price = float(s.get('fuel_price', 0))
            if price > 0:
                processed.append({
                    "name": s.get('service_station', 'Gas Station'),
                    "price": price
                })
        
        sorted_list = sorted(processed, key=lambda x: x['price'])
        current_min = sorted_list[0]['price'] if sorted_list else 0

        # 4. Save with metadata for the HTML
        final_output = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "prev_min": prev_min,
            "current_min": current_min,
            "stations": sorted_list[:15] # Keep top 15 for mobile speed
        }

        with open('gas_prices.json', 'w') as f:
            json.dump(final_output, f, indent=4)
            
        print(f"Sync complete. Low: {current_min}¢ (Prev: {prev_min}¢)")

    except Exception as e:
        print(f"Failed to update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_zyla_gas()