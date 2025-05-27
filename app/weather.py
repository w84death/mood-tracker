import requests
import os
import math
from datetime import datetime, timedelta
import time
import calendar

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
        # Calculate daylight hours from sunrise/sunset
        sunrise = data.get('sys', {}).get('sunrise', 0)
        sunset = data.get('sys', {}).get('sunset', 0)
        daylight_hours = 0
        if sunrise and sunset:
            daylight_hours = (sunset - sunrise) / 3600  # Convert seconds to hours

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
            'clouds': data.get('clouds', {}).get('all', 0),
            'air_pressure': data['main']['pressure'],
            'daylight_hours': round(daylight_hours, 2),
            'data_type': 'current'
        }
        return weather_data
    except requests.RequestException as e:
        print(f"Error fetching current weather data: {e}")
        return None
    except KeyError as e:
        print(f"Error parsing weather data: {e}")
        return None

def get_forecast_weather(date_str):
    """Fetch forecast weather data for future dates."""
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None

    try:
        url = f'http://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Parse the target date
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Find forecast data for the target date
        daily_forecasts = {}
        for forecast in data['list']:
            forecast_datetime = datetime.fromtimestamp(forecast['dt'])
            forecast_date = forecast_datetime.date()

            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = []
            daily_forecasts[forecast_date].append(forecast)

        if target_date in daily_forecasts:
            day_forecasts = daily_forecasts[target_date]

            # Calculate daily aggregates from hourly forecasts
            temps = [f['main']['temp'] for f in day_forecasts]
            humidities = [f['main']['humidity'] for f in day_forecasts]
            precipitations = [f.get('rain', {}).get('3h', 0) + f.get('snow', {}).get('3h', 0) for f in day_forecasts]

            # Get the most common weather condition
            weather_conditions = [f['weather'][0]['main'] for f in day_forecasts]
            most_common_condition = max(set(weather_conditions), key=weather_conditions.count)

            # Get description from first forecast with the most common condition
            description = next(f['weather'][0]['description'] for f in day_forecasts if f['weather'][0]['main'] == most_common_condition)

            # Calculate estimated daylight hours for forecast date
            daylight_hours = calculate_daylight_hours(date_str, float(LAT))

            weather_data = {
                'temp_min': min(temps),
                'temp_max': max(temps),
                'temp_current': sum(temps) / len(temps),
                'humidity': sum(humidities) / len(humidities),
                'pressure': day_forecasts[0]['main']['pressure'],
                'precipitation': max(precipitations),
                'weather_main': most_common_condition,
                'weather_description': description,
                'wind_speed': sum(f.get('wind', {}).get('speed', 0) for f in day_forecasts) / len(day_forecasts),
                'clouds': sum(f.get('clouds', {}).get('all', 0) for f in day_forecasts) / len(day_forecasts),
                'air_pressure': sum(f['main']['pressure'] for f in day_forecasts) / len(day_forecasts),
                'daylight_hours': daylight_hours,
                'data_type': 'forecast'
            }
            return weather_data
        else:
            print(f"No forecast data available for {date_str}")
            return None

    except requests.RequestException as e:
        print(f"Error fetching forecast weather data for {date_str}: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing forecast weather data for {date_str}: {e}")
        return None

def get_historical_weather(date_str):
    """Fetch historical weather data for a specific date (YYYY-MM-DD format).
    Note: Historical weather data requires OpenWeather subscription for dates older than 5 days.
    """
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None

    try:
        # Convert date string to timestamp at noon UTC
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        # Set time to noon to get better daily average
        date_obj = date_obj.replace(hour=12, minute=0, second=0)
        timestamp = int(date_obj.timestamp())

        # Check how many days ago this was
        days_ago = (datetime.now() - date_obj).days

        # For dates more than 5 days ago, try the paid historical API
        if days_ago > 5:
            url = f'http://api.openweathermap.org/data/3.0/onecall/timemachine?lat={LAT}&lon={LON}&dt={timestamp}&appid={API_KEY}&units=metric'
        else:
            # For recent dates (within 5 days), use the free tier One Call API
            url = f'http://api.openweathermap.org/data/2.5/onecall/timemachine?lat={LAT}&lon={LON}&dt={timestamp}&appid={API_KEY}&units=metric'

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract weather data from historical API response
        if 'data' in data and len(data['data']) > 0:
            day_data = data['data'][0]

            # Handle different response structures
            if 'temp' in day_data:
                if isinstance(day_data['temp'], dict):
                    temp_min = day_data['temp'].get('min', day_data['temp'].get('day', 0))
                    temp_max = day_data['temp'].get('max', day_data['temp'].get('day', 0))
                    temp_current = day_data['temp'].get('day', 0)
                else:
                    temp_min = temp_max = temp_current = day_data['temp']
            else:
                temp_min = temp_max = temp_current = 0

            # Calculate daylight hours for historical date
            daylight_hours = calculate_daylight_hours(date_str, float(LAT))

            weather_data = {
                'temp_min': temp_min,
                'temp_max': temp_max,
                'temp_current': temp_current,
                'humidity': day_data.get('humidity', 0),
                'pressure': day_data.get('pressure', 0),
                'precipitation': day_data.get('rain', {}).get('1h', 0) + day_data.get('snow', {}).get('1h', 0) if 'rain' in day_data or 'snow' in day_data else 0,
                'weather_main': day_data.get('weather', [{}])[0].get('main', 'Unknown'),
                'weather_description': day_data.get('weather', [{}])[0].get('description', 'Unknown'),
                'wind_speed': day_data.get('wind_speed', 0),
                'clouds': day_data.get('clouds', 0),
                'air_pressure': day_data.get('pressure', 0),
                'daylight_hours': daylight_hours,
                'data_type': 'historical'
            }
            return weather_data
        else:
            print(f"No historical weather data available for {date_str}")
            return None

    except requests.RequestException as e:
        if "401" in str(e):
            print(f"Historical weather data requires OpenWeather subscription for {date_str}")
        else:
            print(f"Error fetching historical weather data for {date_str}: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing historical weather data for {date_str}: {e}")
        return None

def get_weather_for_date(date_str):
    """Get weather data for any date, using appropriate API based on date."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().date()
        target_date = date_obj.date()
        days_diff = (target_date - today).days

        weather_data = None
        if days_diff > 0:
            # Future date - get forecast (only available for next 5 days)
            if days_diff <= 5:
                weather_data = get_forecast_weather(date_str)
            else:
                print(f"Forecast not available for {date_str} (too far in future)")
                return None
        elif days_diff == 0:
            # Today - get current weather
            weather_data = get_current_weather()
        else:
            # Past date - get historical weather
            weather_data = get_historical_weather(date_str)

        # Add air pollution data if weather data was successfully retrieved
        if weather_data:
            air_pollution = get_air_pollution_for_date(date_str)
            if air_pollution:
                weather_data.update(air_pollution)

        return weather_data

    except ValueError as e:
        print(f"Invalid date format: {date_str}")
        return None

def format_weather_summary(weather_data):
    """Format weather data into a human-readable summary."""
    if not weather_data:
        return "Weather data unavailable"
    
    temp_min = weather_data.get('temp_min', 0) or 0
    temp_max = weather_data.get('temp_max', 0) or 0
    temp_range = f"{temp_min:.1f}°C - {temp_max:.1f}°C"
    
    description = weather_data.get('weather_description') or 'Unknown'
    if description and description != 'Unknown':
        description = description.title()
    
    humidity = weather_data.get('humidity', 0) or 0
    precipitation = weather_data.get('precipitation', 0) or 0
    air_pressure = weather_data.get('air_pressure', 0) or 0
    data_type = weather_data.get('data_type', 'unknown')
    aqi = weather_data.get('aqi')
    aqi_description = weather_data.get('aqi_description')
    daylight_hours = weather_data.get('daylight_hours', 0) or 0
    
    summary = f"{description}, {temp_range}"
    if humidity and humidity > 0:
        summary += f", {humidity:.0f}% humidity"
    if air_pressure and air_pressure > 0:
        summary += f", {air_pressure:.0f}hPa"
    if precipitation and precipitation > 0:
        summary += f", {precipitation:.1f}mm rain"
    if aqi and aqi_description:
        aqi_emoji = get_aqi_emoji(aqi)
        summary += f", {aqi_emoji} {aqi_description} air"
    if daylight_hours and daylight_hours > 0:
        summary += f", ☀️ {daylight_hours:.1f}h daylight"
    
    # Add data type indicator
    if data_type == 'forecast':
        summary += " (forecast)"
    elif data_type == 'historical':
        summary += " (actual)"
    
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

def is_future_date(date_str):
    """Check if a date is in the future."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date_obj > today
    except ValueError:
        return False

def calculate_moon_phase(date_str):
    """Calculate moon phase for a given date."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')

        # Known new moon date as reference (January 6, 2000)
        known_new_moon = datetime(2000, 1, 6, 18, 14)

        # Calculate days since known new moon
        days_since = (date_obj - known_new_moon).total_seconds() / (24 * 3600)

        # Moon cycle is approximately 29.53 days
        moon_cycle = 29.530588853

        # Calculate current position in cycle (0-1)
        cycle_position = (days_since % moon_cycle) / moon_cycle

        # Calculate illumination percentage
        if cycle_position <= 0.5:
            # Waxing (0 to 100%)
            illumination = cycle_position * 2 * 100
        else:
            # Waning (100% to 0%)
            illumination = (1 - cycle_position) * 2 * 100

        # Determine phase name based on cycle position
        if cycle_position < 0.0625:
            phase_name = "New Moon"
            phase_emoji = "🌑"
        elif cycle_position < 0.1875:
            phase_name = "Waxing Crescent"
            phase_emoji = "🌒"
        elif cycle_position < 0.3125:
            phase_name = "First Quarter"
            phase_emoji = "🌓"
        elif cycle_position < 0.4375:
            phase_name = "Waxing Gibbous"
            phase_emoji = "🌔"
        elif cycle_position < 0.5625:
            phase_name = "Full Moon"
            phase_emoji = "🌕"
        elif cycle_position < 0.6875:
            phase_name = "Waning Gibbous"
            phase_emoji = "🌖"
        elif cycle_position < 0.8125:
            phase_name = "Last Quarter"
            phase_emoji = "🌗"
        else:
            phase_name = "Waning Crescent"
            phase_emoji = "🌘"

        return {
            'phase_name': phase_name,
            'phase_emoji': phase_emoji,
            'illumination_percent': round(illumination, 1),
            'cycle_position': cycle_position
        }

    except ValueError:
        return None

def get_moon_phase_emoji(phase_name):
    """Get emoji for moon phase."""
    phase_emojis = {
        'New Moon': '🌑',
        'Waxing Crescent': '🌒',
        'First Quarter': '🌓',
        'Waxing Gibbous': '🌔',
        'Full Moon': '🌕',
        'Waning Gibbous': '🌖',
        'Last Quarter': '🌗',
        'Waning Crescent': '🌘'
    }
    return phase_emojis.get(phase_name, '🌙')

def is_historical_date(date_str):
    """Check if a date is in the past."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return date_obj < today
    except ValueError:
        return False

def get_air_pollution_for_date(date_str):
    """Get air pollution data for a specific date."""
    if not API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return None

    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        today = datetime.now().date()
        target_date = date_obj.date()
        days_diff = (target_date - today).days

        if days_diff == 0:
            # Current air pollution
            url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={LAT}&lon={LON}&appid={API_KEY}'
        elif days_diff > 0 and days_diff <= 5:
            # Forecast air pollution (available for next 5 days)
            url = f'http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={LAT}&lon={LON}&appid={API_KEY}'
        else:
            # Historical air pollution (requires paid plan for dates > 5 days ago)
            # Use current date timestamp at noon for historical data
            timestamp = int(date_obj.replace(hour=12).timestamp())
            url = f'http://api.openweathermap.org/data/2.5/air_pollution/history?lat={LAT}&lon={LON}&start={timestamp}&end={timestamp}&appid={API_KEY}'

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if 'list' in data and len(data['list']) > 0:
            pollution_data = data['list'][0]  # Get first entry
            
            # For forecast data, find the entry closest to the target date
            if days_diff > 0 and days_diff <= 5:
                target_timestamp = date_obj.replace(hour=12).timestamp()
                closest_entry = min(data['list'], 
                                   key=lambda x: abs(x['dt'] - target_timestamp))
                pollution_data = closest_entry

            aqi = pollution_data.get('main', {}).get('aqi', 0)
            components = pollution_data.get('components', {})
            
            return {
                'aqi': aqi,
                'aqi_description': get_aqi_description(aqi),
                'pm2_5': components.get('pm2_5', 0),
                'pm10': components.get('pm10', 0),
                'no2': components.get('no2', 0),
                'o3': components.get('o3', 0),
                'co': components.get('co', 0)
            }
        else:
            print(f"No air pollution data available for {date_str}")
            return None

    except requests.RequestException as e:
        if "401" in str(e):
            print(f"Air pollution data may require OpenWeather subscription for {date_str}")
        else:
            print(f"Error fetching air pollution data for {date_str}: {e}")
        return None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Error parsing air pollution data for {date_str}: {e}")
        return None

def get_aqi_description(aqi):
    """Convert AQI number to description."""
    aqi_descriptions = {
        1: "Good",
        2: "Fair", 
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }
    return aqi_descriptions.get(aqi, "Unknown")

def get_aqi_emoji(aqi):
    """Get emoji for air quality index."""
    aqi_emojis = {
        1: "🟢",  # Good
        2: "🟡",  # Fair
        3: "🟠",  # Moderate
        4: "🔴",  # Poor
        5: "🟣"   # Very Poor
    }
    return aqi_emojis.get(aqi, "⚪")

def calculate_daylight_hours(date_str, latitude):
    """Calculate daylight hours for a given date and latitude."""
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Day of year
        day_of_year = date_obj.timetuple().tm_yday
        
        # Solar declination angle
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        
        # Hour angle
        lat_rad = math.radians(latitude)
        decl_rad = math.radians(declination)
        
        # Calculate sunrise hour angle
        cos_hour_angle = -math.tan(lat_rad) * math.tan(decl_rad)
        
        # Check for polar day or polar night
        if cos_hour_angle > 1:
            return 0  # Polar night
        elif cos_hour_angle < -1:
            return 24  # Polar day
        
        hour_angle = math.degrees(math.acos(cos_hour_angle))
        daylight_hours = 2 * hour_angle / 15  # Convert to hours
        
        return round(daylight_hours, 2)
        
    except (ValueError, ZeroDivisionError) as e:
        print(f"Error calculating daylight hours for {date_str}: {e}")
        return 0
