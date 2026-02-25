from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import os
from datetime import datetime


def get_day_label(date_str, index):
    """Convert a YYYY-MM-DD date string to a short day label."""
    if index == 0:
        return "Today"
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%a")


def get_date_label(date_str):
    """Convert a YYYY-MM-DD date string to MM/DD format."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return "{}/{}".format(dt.month, dt.day)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'PUT_YOUR_KEY_HERE')
        LOCATION = os.environ.get('LOCATION', '37.8715,-122.2730')

        try:
            # Get current weather + 3-day forecast with hourly data
            forecast_url = (
                f"https://api.weatherapi.com/v1/forecast.json"
                f"?key={WEATHER_API_KEY}&q={LOCATION}&days=3&aqi=no&alerts=no"
            )
            with urllib.request.urlopen(forecast_url) as response:
                forecast_data = json.loads(response.read())

            current_data = forecast_data["current"]
            location_data = forecast_data["location"]
            forecast_days = forecast_data["forecast"]["forecastday"]

            weather_data = {
                "location": location_data["name"],
                "region": location_data["region"],
                "current": {
                    "temp_f": int(current_data["temp_f"]),
                    "temp_c": int(current_data["temp_c"]),
                    "condition": current_data["condition"]["text"],
                    "humidity": current_data["humidity"],
                    "wind_mph": int(current_data["wind_mph"]),
                    "feels_like_f": int(current_data["feelslike_f"]),
                    "uv": current_data.get("uv", 0)
                },
                "forecast": [],
                "hourly": []
            }

            # Add all 4 days (index 0 = Today, 1-3 = next 3 days)
            # Templates skip index 0 to show only upcoming days
            for i, day in enumerate(forecast_days):
                weather_data["forecast"].append({
                    "day": get_day_label(day["date"], i),
                    "date": get_date_label(day["date"]),
                    "high_f": int(day["day"]["maxtemp_f"]),
                    "low_f": int(day["day"]["mintemp_f"]),
                    "condition": day["day"]["condition"]["text"],
                    "rain": day["day"].get("daily_chance_of_rain", 0)
                })

            # Add next 6 hours of hourly forecast
            today_forecast = forecast_days[0]
            tomorrow_forecast = forecast_days[1] if len(forecast_days) > 1 else None
            current_hour = datetime.now().hour

            for hour_data in today_forecast["hour"]:
                hour_time = datetime.strptime(hour_data["time"], "%Y-%m-%d %H:%M")
                if hour_time.hour >= current_hour:
                    weather_data["hourly"].append({
                        "time": hour_time.strftime("%I %p").lstrip("0"),
                        "temp_f": int(hour_data["temp_f"]),
                        "condition": hour_data["condition"]["text"],
                        "rain": hour_data.get("chance_of_rain", 0)
                    })

            if len(weather_data["hourly"]) < 6 and tomorrow_forecast:
                hours_needed = 6 - len(weather_data["hourly"])
                for i, hour_data in enumerate(tomorrow_forecast["hour"]):
                    if i >= hours_needed:
                        break
                    hour_time = datetime.strptime(hour_data["time"], "%Y-%m-%d %H:%M")
                    weather_data["hourly"].append({
                        "time": hour_time.strftime("%I %p").lstrip("0"),
                        "temp_f": int(hour_data["temp_f"]),
                        "condition": hour_data["condition"]["text"],
                        "rain": hour_data.get("chance_of_rain", 0)
                    })

            weather_data["hourly"] = weather_data["hourly"][:6]

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(weather_data).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
