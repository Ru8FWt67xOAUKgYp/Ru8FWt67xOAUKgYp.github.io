import requests
import json
import sys

def fetch_gas_prices():
    url = "https://www.gasbuddy.com/graphql"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Precise query with ALL variables defined in the schema to avoid 400 errors
    payload = {
        "operationName": "LocationBySearchTerm",
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
        }""",
        "variables": {
            "search": "H3W 1X4",
            "fuel": 1,        # 1 = Regular
            "maxAge": 0,      # 0 = Any age
            "brandId": None,
            "cursor": None,
            "lat": None,
            "lng": None
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Server Error {response.status_code}: {response.text}")
            sys.exit(1)

        data = response.json()
        stations = data.get('data', {}).get('locationBySearchTerm', {}).get('stations', {}).get('results', [])
        
        if not stations:
            print("No stations found in response.")
            sys.exit(1)

        results = []
        for s in stations:
            # Match regular fuel type
            reg_prices = [p for p in s.get('prices', []) if p.get('fuelProduct') == 'regular']
            if reg_prices:
                p_info = reg_prices[0].get('credit', {})
                if p_info.get('price', 0) > 0:
                    results.append({
                        "name": s.get('name', 'Station'),
                        "address": s.get('address', {}).get('line1', 'Unknown Address'),
                        "price": p_info['price']
                    })

        # Sort by price and save top 20
        top_20 = sorted(results, key=lambda x: x['price'])[:20]
        
        with open('gas_prices.json', 'w') as f:
            json.dump(top_20, f, indent=4)
        
        print(f"Success! Found {len(top_20)} stations.")

    except Exception as e:
        print(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_gas_prices()