import requests
import os

API_KEY = os.getenv('OPENWEATHER_API_KEY')
LAT = os.getenv('LATITUDE', '52.4064')  # Poznań, Poland
LON = os.getenv('LONGITUDE', '16.9252')

def get_weather(date):
    """Fetch weather data for a given date from OpenWeatherMap API."""
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Extract relevant weather data
        weather_data = {
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'precipitation': data.get('rain', {}).get('1h', 0)  # Rainfall in last hour, default to 0 if not present
        }
        return weather_data
    except requests.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None
