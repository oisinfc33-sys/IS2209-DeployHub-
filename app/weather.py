import os
import requests
import logging

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> dict:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "API key not configured"}

    try:
        response = requests.get(
            OPENWEATHER_URL,
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=5
        )

        if response.status_code == 404:
            return {"error": f"City '{city}' not found"}

        if response.status_code == 401:
            return {"error": "Invalid API key"}

        if response.status_code != 200:
            return {"error": "Weather API error", "api_response": response.json()}

        data = response.json()

        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "conditions": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"],
        }

        except requests.exceptions.Timeout:
        logger.warning("OpenWeatherMap request timed out for city: %s", city)
        return {"error": "Weather service timed out, please try again"}

  except requests.exceptions.RequestException as e:
        logger.error("Failed to contact weather service: %s", str(e))
        return {"error": "Failed to contact weather service", "details": str(e)}

