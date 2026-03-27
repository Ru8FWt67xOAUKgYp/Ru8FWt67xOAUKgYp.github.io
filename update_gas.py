import json
import sys
# You MUST add 'curl_cffi' to your .yml dependencies (see below)
from curl_cffi import requests 

def fetch_gas_prices():
    url = "https://www.gasbuddy.com/graphql"
    
    # We use 'impersonate' to mimic a real Chrome browser's TLS fingerprint
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://www.gasbuddy.com",
        "referer": "https://www.gasbuddy.com/",
    }
    
    payload = {
        "operationName": "LocationBySearchTerm",
        "variables": {
            "search": "H3W 1X4",
            "fuel": 1,
            "maxAge": 0,
            "brandId": None,
            "cursor": None,
            "lat": 45.4925, # Added Montreal coords to help the search
            "lng": -73.6331
        },
        "query": """query LocationBySearchTerm($brandId: Int, $cursor: String, $fuel: Int, $lat: Float, $lng: Float, $maxAge: Int, $search: String) {
          locationBySearchTerm(lat: $lat, lng: $lng, search: $search) {
            stations(brandId: $brandId, cursor: $cursor, fuel: $fuel, maxAge: $maxAge) {
              results {
                name
                address { line1 }
                prices {
                  fuelProduct
                  credit {
                    price
                    postedTime
                  }
                }
              }
            }
          }
        }"""
    }

    try:
        # 'impersonate="chrome"' is the magic fix for 400/403 errors
        response = requests.post(url, json=payload, headers=headers, impersonate="chrome", timeout=30)
        
        if response.status_code != 200:
            print(f"Handshake failed ({response.status_code}). Server response: {response.text[:200]}")
            sys.exit(1)

        data = response.json()
        stations = data.get('data', {}).get('locationBySearchTerm', {}).get('stations', {}).get('results', [])
        
        results = []
        for s in stations:
            reg_prices = [p for p in s.get('prices', []) if p.get('fuelProduct') == 'regular']
            if reg_prices:
                price_data = reg_prices[0].get('credit', {})
                if price_data.get('price', 0) > 0:
                    results.append({
                        "name": s.get('name', 'Station'),
                        "address": s.get('address', {}).get('line1', 'Montreal, QC'),
                        "price": price_data['price']
                    })

        if not results:
            print("No prices found. The search returned 0 results.")
            sys.exit(1)

        with open('gas_prices.json', 'w') as f:
            json.dump(sorted(results, key=lambda x: x['price'])[:20], f, indent=4)
        
        print(f"Success! {len(results)} stations found.")

    except Exception as e:
        print(f"Script Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_gas_prices()