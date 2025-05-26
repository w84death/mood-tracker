import requests
import os
from datetime import datetime, timedelta
import time

API_KEY = os.getenv('OPENWEATHER_API_KEY')
LAT = os.getenv('LATITUDE', '52.4064')  # Poznań, Poland
LON = os.getenv('LONGITUDE', '16.9252')

def get_current_weather():
    """Fetch current weather data from OpenWeatherMap API."""
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None
        
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract relevant weather data
        weather_data = {
            'temp_min': data['main']['temp_min'],
            'temp_max': data['main']['temp_max'],
            'temp_current': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'precipitation': data.get('rain', {}).get('1h', 0) + data.get('snow', {}).get('1h', 0),
            'weather_main': data['weather'][0]['main'],
            'weather_description': data['weather'][0]['description'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'clouds': data.get('clouds', {}).get('all', 0)
        }
        return weather_data
    except requests.RequestException as e:
        print(f"Error fetching current weather data: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing weather data: {e}")
        return None

def get_historical_weather(date_str):
    """Fetch historical weather data for a specific date (YYYY-MM-DD format)."""
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None
        
    try:
        # Convert date string to timestamp
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        timestamp = int(date_obj.timestamp())
        
        # Check if date is more than 5 days ago (requires One Call API 3.0)
        days_ago = (datetime.now() - date_obj).days
        
        if days_ago > 5:
            # Use One Call API 3.0 for historical data (requires subscription)
            url = f'http://api.openweathermap.org/data/3.0/onecall/timemachine?lat={LAT}&lon={LON}&dt={timestamp}&appid={API_KEY}&units=metric'
        else:
            # For recent dates, use current weather as approximation
            return get_current_weather()
            
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract weather data from historical API response
        if 'data' in data and len(data['data']) > 0:
            day_data = data['data'][0]
            weather_data = {
                'temp_min': day_data.get('temp', {}).get('min', day_data.get('temp', 0)),
                'temp_max': day_data.get('temp', {}).get('max', day_data.get('temp', 0)),
                'temp_current': day_data.get('temp', 0) if isinstance(day_data.get('temp'), (int, float)) else day_data.get('temp', {}).get('day', 0),
                'humidity': day_data.get('humidity', 0),
                'pressure': day_data.get('pressure', 0),
                'precipitation': day_data.get('rain', {}).get('1h', 0) + day_data.get('snow', {}).get('1h', 0) if 'rain' in day_data or 'snow' in day_data else 0,
                'weather_main': day_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': day_data.get('weather', [{}])[0].get('description', 'Unknown'),
                'wind_speed': day_data.get('wind_speed', 0),
                'clouds': day_data.get('clouds', 0)
            }
            return weather_data
        else:
            print(f"No historical weather data available for {date_str}")
            return None
            
    except requests.RequestException as e:
        print(f"Error fetching historical weather data for {date_str}: {e}")
        # If historical API fails, try to get current weather as fallback
        if days_ago <= 1:
            return get_current_weather()
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing historical weather data for {date_str}: {e}")
        return None

def get_weather_for_date(date_str):
    """Get weather data for any date, using appropriate API based on date."""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    today = datetime.now().date()
    target_date = date_obj.date()
    
    # If it's today or future, get current weather
    if target_date >= today:
        return get_current_weather()
    else:
        return get_historical_weather(date_str)

def format_weather_summary(weather_data):
    """Format weather data into a human-readable summary."""
    if not weather_data:
        return "Weather data unavailable"
    
    temp_range = f"{weather_data.get('temp_min', 0):.1f}°C - {weather_data.get('temp_max', 0):.1f}°C"
    description = weather_data.get('weather_description', 'Unknown').title()
    humidity = weather_data.get('humidity', 0)
    precipitation = weather_data.get('precipitation', 0)
    
    summary = f"{description}, {temp_range}"
    if humidity > 0:
        summary += f", {humidity}% humidity"
    if precipitation > 0:
        summary += f", {precipitation:.1f}mm rain"
    
    return summary

def get_weather_emoji(weather_main):
    """Get appropriate emoji for weather condition."""
    weather_emojis = {
        'Clear': '☀️',
        'Clouds': '☁️',
        'Rain': '🌧️',
        'Drizzle': '🌦️',
        'Thunderstorm': '⛈️',
        'Snow': '❄️',
        'Mist': '🌫️',
        'Fog': '🌫️',
        'Haze': '🌫️',
        'Smoke': '🌫️',
        'Dust': '🌫️',
        'Sand': '🌫️',
        'Ash': '🌫️',
        'Squall': '💨',
        'Tornado': '🌪️'
    }
    return weather_emojis.get(weather_main, '🌤️')