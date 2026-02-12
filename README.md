# trmnl-weather

Weather app for TRMNL e-ink display. Fetches weather data from WeatherAPI.com and serves it as a polling endpoint for TRMNL private plugins.

## Setup

### 1. Deploy to Vercel

Set the following environment variables in your Vercel project:

- `WEATHER_API_KEY` (required) - Your [WeatherAPI.com](https://www.weatherapi.com/) API key
- `LOCATION` (optional) - Location query string (defaults to `37.8715,-122.2730` / Berkeley, CA). Accepts city names, coordinates, or postal codes.

### 2. Configure TRMNL Plugin

1. In your [TRMNL dashboard](https://usetrmnl.com), create a new **Private Plugin** using the **Polling** strategy.
2. Set the polling URL to your Vercel deployment: `https://your-app.vercel.app/api/weather`
3. Open the **Markup Editor** and paste the contents of the appropriate template from the `templates/` directory:
   - `templates/full.liquid` - Full screen (800x480)
   - `templates/half_horizontal.liquid` - Half horizontal layout
   - `templates/half_vertical.liquid` - Half vertical layout
   - `templates/quadrant.liquid` - Quadrant layout

The templates use the [TRMNL Design Framework](https://usetrmnl.com/framework) CSS classes for proper rendering on the e-ink display.

## API Response

The `/api/weather` endpoint returns JSON with the following structure:

```json
{
  "location": "Berkeley",
  "region": "California",
  "current": {
    "temp_f": 72,
    "temp_c": 22,
    "condition": "Partly cloudy",
    "humidity": 45,
    "wind_mph": 5,
    "feels_like_f": 70,
    "uv": 6
  },
  "forecast": [
    {"day": "Today", "high_f": 75, "low_f": 52, "condition": "Sunny", "rain": 10},
    {"day": "Fri", "high_f": 73, "low_f": 51, "condition": "Partly cloudy", "rain": 20},
    {"day": "Sat", "high_f": 70, "low_f": 48, "condition": "Clear", "rain": 0}
  ],
  "hourly": [
    {"time": "5 PM", "temp_f": 72, "condition": "Sunny", "rain": 10},
    {"time": "6 PM", "temp_f": 70, "condition": "Sunny", "rain": 5}
  ]
}
```

The response is kept compact (~850 bytes) to stay within TRMNL's 2KB polling response limit.
