import requests
import json

def fetch_gas_prices():
    url = "https://www.gasbuddy.com/graphql"
    
    # This query mimics what the GasBuddy website does to find local stations
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
        "fuel": 1 # 1 is Regular Gas
    }

    try:
        response = requests.post(url, json={'query': query, 'variables': variables}, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        stations = data['data']['locationBySearchTerm']['stations']['results']
        
        results = []
        for s in stations:
            # Extract the specific price for regular gas
            reg_prices = [p for p in s['prices'] if p['fuelProduct'] == 'regular']
            if reg_prices and reg_prices[0]['credit']['price'] > 0:
                results.append({
                    "name": s['name'],
                    "address": s['address']['line1'],
                    "price": reg_prices[0]['credit']['price'],
                    "updated": reg_prices[0]['credit']['postedTime']
                })
        
        # Sort by price and take top 20
        top_20 = sorted(results, key=lambda x: x['price'])[:20]
        
        with open('gas_prices.json', 'w') as f:
            json.dump(top_20, f, indent=4)
        print(f"Successfully updated {len(top_20)} stations.")

    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    fetch_gas_prices()