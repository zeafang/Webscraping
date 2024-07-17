import pandas as pd
import requests
import time

def get_geocode_opencage(address, api_key, retries=3):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={requests.utils.quote(address)}&key={api_key}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            geocode_data = response.json()
            if geocode_data['results']:
                location = geocode_data['results'][0]['geometry']
                return location['lat'], location['lng']
            else:
                print(f"Error geocoding {address}: No results")
                return None, None
        elif response.status_code == 401:
            print(f"HTTP error 401: Unauthorized. Please check your API key.")
            return None, None
        elif response.status_code == 403:
            print(f"HTTP error 403: Forbidden. You might have exceeded your usage limits.")
            return None, None
        elif response.status_code == 429:
            print(f"HTTP error 429: Too Many Requests. You are being rate limited.")
            if retries > 0:
                print("Retrying after a short wait...")
                time.sleep(5)
                return get_geocode_opencage(address, api_key, retries - 1)
            else:
                return None, None
        else:
            print(f"HTTP error {response.status_code} for address {address}")
            return None, None
    except requests.exceptions.RequestException as e:
        if retries > 0:
            time.sleep(1)
            return get_geocode_opencage(address, api_key, retries - 1)
        else:
            print(f"Failed to geocode {address} after retries due to {e}")
            return None, None

def geocode_addresses(input_csv, output_csv, api_key):
    df = pd.read_csv(input_csv)
    df['Latitude'] = None
    df['Longitude'] = None
    for index, row in df.iterrows():
        address = row['Address']  # Assuming the column with addresses is named 'Address'
        latitude, longitude = get_geocode_opencage(address, api_key)
        df.at[index, 'Latitude'] = latitude
        df.at[index, 'Longitude'] = longitude
        print(f"Updated row {index}: {df.loc[index].to_dict()}")
    df.to_csv(output_csv, index=False)
    print(f"Geocoded addresses saved to {output_csv}")

# Example usage
api_key = "5a3db60c204b47e09b6cc73988c26986"  # Replace with your OpenCage API key
input_csv = "asian_market_ontario.csv"  # Path to the input CSV file containing addresses
output_csv = "asian_market_ontario_geocode.csv"  # Path to the output CSV file
geocode_addresses(input_csv, output_csv, api_key)
