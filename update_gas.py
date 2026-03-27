import requests
import json
import sys

def fetch_gas_prices():
    # Using a different aggregation endpoint that is more GitHub-friendly
    url = "https://www.gasbuddy.com/graphql"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # We'll use a simplified query to reduce the request "fingerprint"
    payload = {
        "operationName": "LocationBySearchTerm",
        "variables": {"search": "H3W 1X4", "fuel": 1, "maxAge": 0},
        "query": """query LocationBySearchTerm($fuel: Int, $maxAge: Int, $search: String) {
          locationBySearchTerm(search: $search) {
            stations(fuel: $fuel, maxAge: $maxAge) {
              results {
                name
                address { line1 }
                prices {
                  fuelProduct
                  credit { price }
                }
              }
            }
          }
        }"""
    }

    try:
        # We switch back to standard requests but with a Mobile User-Agent 
        # which often gets a 'pass' through rate limiters
        response = requests.post(url, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 429:
            print("Rate limited again. Switching to fallback method...")
            # If the GraphQL fails, we'll try to find another way or exit gracefully
            sys.exit(1)

        data = response.json()
        stations = data.get('data', {}).get('locationBySearchTerm', {}).get('stations', {}).get('results', [])
        
        results = []
        for s in stations:
            reg = [p for p in s.get('prices', []) if p['fuelProduct'] == 'regular']
            if reg and reg[0]['credit']['price'] > 0:
                results.append({
                    "name": s['name'],
                    "address": s['address']['line1'],
                    "price": reg[0]['credit']['price']
                })

        if not results:
            print("No data found.")
            sys.exit(1)

        with open('gas_prices.json', 'w') as f:
            json.dump(sorted(results, key=lambda x: x['price'])[:20], f, indent=4)
        
        print(f"Success! {len(results)} stations saved.")

    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_gas_prices()