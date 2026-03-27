import requests
import json
import sys

def fetch_gas_prices():
    url = "https://www.gasbuddy.com/graphql"
    
    # GasBuddy now requires a real-looking User-Agent header
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }
    
    query = """
    query LocationBySearchTerm($search: String, $fuel: Int) {
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
    }
    """
    
    variables = {
        "search": "H3W 1X4",
        "fuel": 1  # 1 = Regular
    }

    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Guard against empty data structure
        if not data.get('data') or not data['data'].get('locationBySearchTerm'):
            print("Error: GasBuddy returned no data for this postal code.")
            sys.exit(1)

        stations = data['data']['locationBySearchTerm']['stations']['results']
        
        results = []
        for s in stations:
            # Filter for regular gas and valid prices
            reg_prices = [p for p in s.get('prices', []) if p.get('fuelProduct') == 'regular']
            if reg_prices:
                price_val = reg_prices[0].get('credit', {}).get('price')
                if price_val and price_val > 0:
                    results.append({
                        "name": s.get('name', 'Unknown'),
                        "address": s.get('address', {}).get('line1', 'No Address'),
                        "price": price_val,
                        "updated": reg_prices[0]['credit'].get('postedTime')
                    })
        
        if not results:
            print("No valid prices found in the results.")
            sys.exit(1)

        # Sort and Save
        top_20 = sorted(results, key=lambda x: x['price'])[:20]
        with open('gas_prices.json', 'w') as f:
            json.dump(top_20, f, indent=4)
        
        print(f"Success! Found {len(top_20)} stations.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_gas_prices()