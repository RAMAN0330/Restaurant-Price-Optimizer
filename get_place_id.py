import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_place_id(api_key, place_name, location):
    base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': place_name,
        'inputtype': 'textquery',
        'locationbias': f'point:{location}',
        'fields': 'place_id,name,formatted_address',
        'key': api_key
    }
    
    response = requests.get(base_url, params=params)
    return response.json()

if __name__ == "__main__":
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    place_name = "Village The Soul of India"
    location = "40.7631,-73.5267"  # Hicksville coordinates
    
    result = get_place_id(api_key, place_name, location)
    print("Place Details:", result)
