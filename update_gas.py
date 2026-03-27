import requests
import json
import sys

def fetch_gas_prices():
    url = "https://www.gasbuddy.com/graphql"
    
    # Precise headers to mimic a real browser session
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    # Updated query structure for 2026
    payload = {
        "operationName": "LocationBySearchTerm",
        "variables": {
            "search": "H3W 1X4",
            "fuel": 1 # 1 = Regular
        },
        "query": """query LocationBySearchTerm($search: String, $fuel: Int) {
          locationBySearchTerm(search: $search) {
            stations(fuel: $fuel) {
              results {
                name
                address {
                  line1
                }
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
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        # If we get a 400, print the server's reason to the GitHub logs
        if response.status_code != 200:
            print(f"Server returned {response.status_code}: {response.text}")
            sys.exit(1)

        data = response.json()
        
        # Extract stations safely
        stations = data.get('data', {}).get('locationBySearchTerm', {}).get('stations', {}).get('results', [])
        
        if not stations:
            print("No stations found. GasBuddy might have changed their field names.")
            sys.exit(1)

        results = []
        for s in stations:
            # Look for regular fuel prices specifically
            reg_prices = [p for p in s.get('prices', []) if p.get('fuelProduct') == 'regular']
            if reg_prices:
                p_info = reg_prices[0].get('credit', {})
                if p_info.get('price', 0) > 0:
                    results.append({
                        "name": s.get('name', 'Unknown'),
                        "address": s.get('address', {}).get('line1', 'Unknown Address'),
                        "price": p_info['price'],
                        "updated": p_info.get('postedTime')
                    })

        # Sort by price and take top 20
        top_20 = sorted(results, key=lambda x: x['price'])[:20]
        
        with open('gas_prices.json', 'w') as f:
            json.dump(top_20, f, indent=4)
        
        print(f"Success! Saved {len(top_20)} stations to gas_prices.json")

    except Exception as e:
        print(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_gas_prices()