import os
import requests
import logging
import time

logger = logging.getLogger(__name__)

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city: str, retries: int = 3) -> dict:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not set")

    for attempt in range(retries):
        try:
            start = time.time()
            response = requests.get(
                OPENWEATHER_URL,
                params={"q": city, "appid": api_key, "units": "metric"},
                timeout=5
            )
            elapsed = round((time.time() - start) * 1000, 2)
            logger.info({"event": "openweather_request", "city": city, "status": response.status_code, "ms": elapsed})

            if response.status_code == 404:
                return {"error": f"City '{city}' not found"}
            if response.status_code == 401:
                return {"error": "Invalid API key"}

            response.raise_for_status()
            data = response.json()

            return {
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].capitalize(),
                "icon": data["weather"][0]["icon"],
            }

        except requests.exceptions.Timeout:
            logger.warning({"event": "openweather_timeout", "attempt": attempt + 1})
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            logger.error({"event": "openweather_error", "error": str(e)})
            return {"error": "Weather service unavailable. Please try again later."}

    return {"error": "Weather service timed out after multiple retries."}