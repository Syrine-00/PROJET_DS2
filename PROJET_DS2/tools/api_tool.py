import requests

def fetch_weather_data():
    url = "https://api.open-meteo.com/v1/forecast?latitude=36.8&longitude=10.1&current_weather=true"

    response = requests.get(url)

    if response.status_code != 200:
        return {"error": "API failed"}

    data = response.json()

    return {
        "temperature": data["current_weather"]["temperature"],
        "windspeed": data["current_weather"]["windspeed"],
        "tourism_impact": "high" if data["current_weather"]["temperature"] > 25 else "medium"
    }

def fetch_api_data():
    return {
        "top_regions": {
            "Tunis": 120000,
            "Sousse": 95000,
            "Djerba": 87000
        },
        "total_revenue": 302000,
        "average_occupancy_rate": 78
    }
