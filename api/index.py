from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>TRMNL Weather Server</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
                .endpoint { background: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0; }
            </style>
        </head>
        <body>
            <h1>🌤️ TRMNL Weather Server</h1>
            <p>Your weather server is running successfully!</p>
            
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <strong>GET /api/weather</strong><br>
                Returns current weather and 3-day forecast in JSON format
            </div>
            
            <p><a href="/api/weather">View Weather Data →</a></p>
            
            <h2>Setup Instructions:</h2>
            <ol>
                <li>Make sure you've set your WEATHER_API_KEY in Vercel environment variables</li>
                <li>Optionally set LOCATION (defaults to Berkeley,CA)</li>
                <li>Use the /api/weather endpoint as your TRMNL polling URL</li>
            </ol>
        </body>
        </html>
        """
        
        self.wfile.write(html.encode())
