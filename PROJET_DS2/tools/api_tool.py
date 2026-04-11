import requests

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=36.8&longitude=10.1&current_weather=true"

    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "API failed"}

    data = response.json()

    return {
        "temperature": data["current_weather"]["temperature"],
        "windspeed": data["current_weather"]["windspeed"]
    }
