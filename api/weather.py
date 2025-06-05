from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import os
from datetime import datetime

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Your WeatherAPI key - you'll set this in Vercel
        WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'PUT_YOUR_KEY_HERE')
        LOCATION = os.environ.get('LOCATION', 'Berkeley,CA')
        
        try:
            # Get current weather + 3-day forecast with hourly data
            forecast_url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={LOCATION}&days=3&aqi=no&alerts=no"
            with urllib.request.urlopen(forecast_url) as response:
                forecast_data = json.loads(response.read())
            
            current_data = forecast_data["current"]
            location_data = forecast_data["location"]
            forecast_days = forecast_data["forecast"]["forecastday"]
            
            # Format the data for TRMNL
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
                "hourly_today": [],
                "rain_chances": []
            }
            
            # Add daily forecast with rain chances
            for day in forecast_days:
                day_data = {
                    "date": day["date"],
                    "high_f": int(day["day"]["maxtemp_f"]),
                    "low_f": int(day["day"]["mintemp_f"]),
                    "condition": day["day"]["condition"]["text"],
                    "chance_of_rain": day["day"].get("daily_chance_of_rain", 0),
                    "max_wind_mph": int(day["day"].get("maxwind_mph", 0)),
                    "avg_humidity": int(day["day"].get("avghumidity", 0))
                }
                weather_data["forecast"].append(day_data)
                
                # Separate rain chances for easy access
                weather_data["rain_chances"].append({
                    "date": day["date"],
                    "chance": day["day"].get("daily_chance_of_rain", 0)
                })
            
            # Add today's hourly forecast (next 12 hours)
            today_forecast = forecast_days[0]
            current_hour = datetime.now().hour
            
            for hour_data in today_forecast["hour"]:
                hour_time = datetime.strptime(hour_data["time"], "%Y-%m-%d %H:%M")
                
                # Only include current hour and next 11 hours
                if hour_time.hour >= current_hour:
                    hourly_item = {
                        "time": hour_time.strftime("%I %p").lstrip("0"),  # "2 PM"
                        "temp_f": int(hour_data["temp_f"]),
                        "condition": hour_data["condition"]["text"],
                        "chance_of_rain": hour_data.get("chance_of_rain", 0),
                        "wind_mph": int(hour_data.get("wind_mph", 0))
                    }
                    weather_data["hourly_today"].append(hourly_item)
                    
                    # Limit to 12 hours
                    if len(weather_data["hourly_today"]) >= 12:
                        break
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(weather_data).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
