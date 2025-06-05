from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Your WeatherAPI key - you'll set this in Vercel
        WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY', 'PUT_YOUR_KEY_HERE')
        LOCATION = os.environ.get('LOCATION', 'Berkeley,CA')
        
        try:
            # Get current weather
            current_url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={LOCATION}"
            with urllib.request.urlopen(current_url) as response:
                current_data = json.loads(response.read())
            
            # Get 3-day forecast
            forecast_url = f"https://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={LOCATION}&days=3"
            with urllib.request.urlopen(forecast_url) as response:
                forecast_data = json.loads(response.read())
            
            # Format the data for TRMNL
            weather_data = {
                "location": current_data["location"]["name"],
                "region": current_data["location"]["region"],
                "current": {
                    "temp_f": int(current_data["current"]["temp_f"]),
                    "temp_c": int(current_data["current"]["temp_c"]),
                    "condition": current_data["current"]["condition"]["text"],
                    "humidity": current_data["current"]["humidity"],
                    "wind_mph": int(current_data["current"]["wind_mph"]),
                    "feels_like_f": int(current_data["current"]["feelslike_f"])
                },
                "forecast": []
            }
            
            # Add forecast days
            for day in forecast_data["forecast"]["forecastday"]:
                weather_data["forecast"].append({
                    "date": day["date"],
                    "high_f": int(day["day"]["maxtemp_f"]),
                    "low_f": int(day["day"]["mintemp_f"]),
                    "condition": day["day"]["condition"]["text"]
                })
            
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
