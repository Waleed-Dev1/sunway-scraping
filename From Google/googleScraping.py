import requests
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')


def get_mall_info(mall_name, location=""):
    """Finds the mall using Google Places API."""
    search_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": mall_name + " mall",
        "location": location,
        "key": API_KEY
    }
    response = requests.get(search_url, params=params)
    data = response.json()

    logger.info(data)
    if "results" in data and data["results"]:
        mall = data["results"][0]  # Take the first result
        return {
            "name": mall["name"],
            "place_id": mall["place_id"],
            "address": mall["formatted_address"],
            "lat": mall["geometry"]["location"]["lat"],
            "lng": mall["geometry"]["location"]["lng"]
        }
    else:
        print(f"No results found for {mall_name}")
        return None
