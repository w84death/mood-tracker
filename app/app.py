from flask import Flask, render_template, request, redirect, url_for, jsonify
import database
import weather
from datetime import datetime, timedelta, date
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def timeline():
    """Render the main timeline view."""
    # Get date range (show current week by default)
    today = date.today()
    start_date = today - timedelta(days=3)  # Show 3 days before
    end_date = today + timedelta(days=3)    # Show 3 days after
    
    # Get timeline entries for this range
    entries = database.get_timeline_data(start_date.isoformat(), end_date.isoformat())
    entry_types = database.get_entry_types()
    mood_options = database.get_mood_options()
    energy_options = database.get_energy_options()
    sleep_options = database.get_sleep_options()
    stress_options = database.get_stress_options()
    caffeine_options = database.get_caffeine_options()
    water_options = database.get_water_options()
    alcohol_options = database.get_alcohol_options()
    
    # Get weather data for the date range
    weather_data = database.get_weather_data_range(start_date.isoformat(), end_date.isoformat())
    weather_by_date = {w['date']: w for w in weather_data}
    
    # Fetch missing weather and moon phase data synchronously for now to avoid race conditions
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        if date_str not in weather_by_date:
            weather_info = weather.get_weather_for_date(date_str)
            if weather_info:
                database.store_weather_data(date_str, weather_info)
                weather_by_date[date_str] = weather_info
        
        # Calculate and store moon phase data
        moon_phase = database.get_moon_phase_data(date_str)
        if not moon_phase:
            moon_data = weather.calculate_moon_phase(date_str)
            if moon_data:
                database.store_moon_phase_data(date_str, moon_data['phase_name'], moon_data['illumination_percent'])
                moon_phase = {
                    'phase_name': moon_data['phase_name'],
                    'illumination_percent': moon_data['illumination_percent']
                }
        
        # Add to weather data for easy access
        if moon_phase:
            weather_by_date[date_str + '_moon'] = {
                'phase_name': moon_phase.get('phase_name') if isinstance(moon_phase, dict) else moon_phase['phase_name'],
                'illumination_percent': moon_phase.get('illumination_percent') if isinstance(moon_phase, dict) else moon_phase['illumination_percent'],
                'phase_emoji': weather.get_moon_phase_emoji(moon_phase.get('phase_name') if isinstance(moon_phase, dict) else moon_phase['phase_name'])
            }
        
        current_date += timedelta(days=1)
    
    # Organize entries by date and hour
    timeline_data = {}
    for entry in entries:
        entry_datetime = datetime.fromisoformat(entry['datetime'])
        date_key = entry_datetime.date().isoformat()
        hour_key = entry_datetime.hour
        
        if date_key not in timeline_data:
            timeline_data[date_key] = {}
        if hour_key not in timeline_data[date_key]:
            timeline_data[date_key][hour_key] = []
            
        timeline_data[date_key][hour_key].append({
            'type': entry['entry_type'],
            'display_name': entry['display_name'],
            'emoji': entry['emoji'],
            'value_type': entry['value_type'],
            'numeric_value': entry['numeric_value'],
            'text_value': entry['text_value'],
            'notes': entry['notes']
        })
    
    # Generate date range for template with weather and moon phase
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        weather_info = weather_by_date.get(date_str, {})
        moon_phase_info = database.get_moon_phase_data(date_str)
        if moon_phase_info:
            moon_phase_info['phase_emoji'] = weather.get_moon_phase_emoji(moon_phase_info['phase_name'])
        is_future = current_date > today
        date_range.append({
            'date': date_str,
            'display': current_date.strftime('%A, %B %d'),
            'is_today': current_date == today,
            'is_future': is_future,
            'weather': weather_info,
            'weather_summary': weather.format_weather_summary(weather_info) if weather_info else None,
            'moon_phase': moon_phase_info
        })
        current_date += timedelta(days=1)
    
    return render_template('timeline.html', 
                         timeline_data=timeline_data,
                         date_range=date_range,
                         entry_types=entry_types,
                         mood_options=mood_options,
                         energy_options=energy_options,
                         sleep_options=sleep_options,
                         stress_options=stress_options,
                         caffeine_options=caffeine_options,
                         water_options=water_options,
                         alcohol_options=alcohol_options)

@app.route('/api/add_entry', methods=['POST'])
def add_entry():
    """API endpoint to add a timeline entry."""
    data = request.get_json()
    
    try:
        date_str = data['date']
        hour = int(data['hour'])
        entry_type = data['entry_type']
        
        # Check if this is a future date and restrict entry types
        if weather.is_future_date(date_str):
            if entry_type != 'notes':
                return jsonify({
                    'success': False, 
                    'error': 'For future dates, only general notes entries are allowed'
                }), 400
        
        # Create datetime string
        datetime_str = f"{date_str} {hour:02d}:00:00"
        
        # Get values based on entry type
        numeric_value = data.get('numeric_value')
        text_value = data.get('text_value')
        notes = data.get('notes')
        
        # Add to database
        database.add_timeline_entry(datetime_str, entry_type, numeric_value, text_value, notes)
        
        return jsonify({'success': True, 'message': 'Entry added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/delete_entry', methods=['POST'])
def delete_entry():
    """API endpoint to delete a timeline entry."""
    data = request.get_json()
    
    try:
        date_str = data['date']
        hour = int(data['hour'])
        entry_type = data['entry_type']
        
        # Create datetime string
        datetime_str = f"{date_str} {hour:02d}:00:00"
        
        # Delete from database
        database.delete_timeline_entry(datetime_str, entry_type)
        
        return jsonify({'success': True, 'message': 'Entry deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/get_entries')
def get_entries():
    """API endpoint to get entries for a date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    try:
        entries = database.get_timeline_data(start_date, end_date)
        
        # Convert to JSON-friendly format
        entries_list = []
        for entry in entries:
            entries_list.append({
                'datetime': entry['datetime'],
                'entry_type': entry['entry_type'],
                'display_name': entry['display_name'],
                'emoji': entry['emoji'],
                'value_type': entry['value_type'],
                'numeric_value': entry['numeric_value'],
                'text_value': entry['text_value'],
                'notes': entry['notes']
            })
        
        return jsonify({'entries': entries_list})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/entries')
def view_entries():
    """Enhanced view for daily summaries with weather correlation."""
    # Get recent timeline entries and convert to daily summary
    today = date.today()
    start_date = today - timedelta(days=30)
    
    # Get weather data for the range
    weather_data = database.get_weather_data_range(start_date.isoformat(), today.isoformat())
    weather_by_date = {w['date']: w for w in weather_data}
    
    # Fetch missing weather and moon phase data synchronously
    current_date = start_date
    while current_date <= today:
        date_str = current_date.isoformat()
        if date_str not in weather_by_date:
            weather_info = weather.get_weather_for_date(date_str)
            if weather_info:
                database.store_weather_data(date_str, weather_info)
                weather_by_date[date_str] = weather_info
        
        # Calculate and store moon phase data
        moon_phase = database.get_moon_phase_data(date_str)
        if not moon_phase:
            moon_data = weather.calculate_moon_phase(date_str)
            if moon_data:
                database.store_moon_phase_data(date_str, moon_data['phase_name'], moon_data['illumination_percent'])
        
        current_date += timedelta(days=1)
    
    entries = database.get_timeline_data(start_date.isoformat(), today.isoformat())
    
    # Group entries by date for summary view
    daily_summaries = {}
    for entry in entries:
        entry_datetime = datetime.fromisoformat(entry['datetime'])
        date_key = entry_datetime.date().isoformat()
        
        if date_key not in daily_summaries:
            daily_summaries[date_key] = {
                'date': date_key,
                'entries': [],
                'mood_values': [],
                'energy_values': [],
                'stress_values': [],
                'sleep_quality': None,
                'notes': [],
                'weather': weather_by_date.get(date_key, {}),
                'moon_phase': weather_by_date.get(date_key + '_moon', {})
            }
        
        daily_summaries[date_key]['entries'].append(entry)
        
        # Extract key metrics for summary
        if entry['entry_type'] == 'mood' and entry['numeric_value']:
            daily_summaries[date_key]['mood_values'].append(entry['numeric_value'])
        elif entry['entry_type'] == 'energy' and entry['numeric_value']:
            daily_summaries[date_key]['energy_values'].append(entry['numeric_value'])
        elif entry['entry_type'] == 'stress' and entry['numeric_value']:
            daily_summaries[date_key]['stress_values'].append(entry['numeric_value'])
        elif entry['entry_type'] == 'sleep_quality' and entry['numeric_value']:
            daily_summaries[date_key]['sleep_quality'] = entry['numeric_value']
        elif entry['notes']:
            daily_summaries[date_key]['notes'].append(entry['notes'])
    
    # Calculate averages and add weather summaries
    for date_key, summary in daily_summaries.items():
        # Calculate average mood, energy, stress
        summary['avg_mood'] = sum(summary['mood_values']) / len(summary['mood_values']) if summary['mood_values'] else None
        summary['avg_energy'] = sum(summary['energy_values']) / len(summary['energy_values']) if summary['energy_values'] else None
        summary['avg_stress'] = sum(summary['stress_values']) / len(summary['stress_values']) if summary['stress_values'] else None
        
        # Add weather summary
        summary['weather_summary'] = weather.format_weather_summary(summary['weather']) if summary['weather'] else None
        
        # Add moon phase summary
        if summary['moon_phase']:
            summary['moon_phase_summary'] = f"{summary['moon_phase']['phase_emoji']} {summary['moon_phase']['phase_name']} ({summary['moon_phase']['illumination_percent']:.0f}% visible)"
    
    # Convert to list and sort by date (newest first)
    summaries_list = list(daily_summaries.values())
    summaries_list.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('entries.html', entries=summaries_list)

@app.route('/load_timeline')
def load_timeline():
    """API endpoint to load timeline data for a specific date range."""
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    try:
        entries = database.get_timeline_data(start_date, end_date)
        entry_types = database.get_entry_types()
        mood_options = database.get_mood_options()
        energy_options = database.get_energy_options()
        sleep_options = database.get_sleep_options()
        stress_options = database.get_stress_options()
        caffeine_options = database.get_caffeine_options()
        water_options = database.get_water_options()
        alcohol_options = database.get_alcohol_options()
        
        # Get weather data for the range
        weather_data = database.get_weather_data_range(start_date, end_date)
        weather_by_date = {w['date']: w for w in weather_data}
            
        # Organize entries by date and hour
        timeline_data = {}
        for entry in entries:
            entry_datetime = datetime.fromisoformat(entry['datetime'])
            date_key = entry_datetime.date().isoformat()
            hour_key = entry_datetime.hour
                
            if date_key not in timeline_data:
                timeline_data[date_key] = {}
            if hour_key not in timeline_data[date_key]:
                timeline_data[date_key][hour_key] = []
                    
            timeline_data[date_key][hour_key].append({
                'type': entry['entry_type'],
                'display_name': entry['display_name'],
                'emoji': entry['emoji'],
                'value_type': entry['value_type'],
                'numeric_value': entry['numeric_value'],
                'text_value': entry['text_value'],
                'notes': entry['notes']
            })
            
        return jsonify({
            'timeline_data': timeline_data,
            'entry_types': [dict(et) for et in entry_types],
            'mood_options': mood_options,
            'energy_options': energy_options,
            'sleep_options': sleep_options,
            'stress_options': stress_options,
            'caffeine_options': caffeine_options,
            'water_options': water_options,
            'alcohol_options': alcohol_options,
            'weather_data': weather_by_date
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Legacy route for backward compatibility
@app.route('/submit', methods=['POST'])
def submit():
    """Handle legacy form submission (convert to timeline entries)."""
    date_str = request.form['date']
    
    # Convert form data to timeline entries
    entries_to_add = []
    
    if request.form.get('mood'):
        entries_to_add.append(('12:00:00', 'mood', float(request.form['mood']), None))
    
    if request.form.get('energy'):
        entries_to_add.append(('12:00:00', 'energy', float(request.form['energy']), None))
    
    if request.form.get('sleep_quality'):
        entries_to_add.append(('08:00:00', 'sleep_quality', float(request.form['sleep_quality']), None))
    
    if request.form.get('caffeine_count'):
        entries_to_add.append(('09:00:00', 'caffeine', float(request.form['caffeine_count']), None))
    
    if request.form.get('last_meal_time'):
        meal_time = request.form['last_meal_time']
        entries_to_add.append((meal_time + ':00', 'meal', None, 'Last meal'))
    
    if request.form.get('notes'):
        entries_to_add.append(('23:00:00', 'notes', None, request.form['notes']))
    
    # Add all entries
    for time_str, entry_type, numeric_value, text_value in entries_to_add:
        datetime_str = f"{date_str} {time_str}"
        database.add_timeline_entry(datetime_str, entry_type, numeric_value, text_value, None)
    
    return redirect(url_for('timeline'))

@app.route('/api/weather/<date_str>')
def get_weather_api(date_str):
    """API endpoint to get weather data for a specific date."""
    try:
        # Check if we have cached weather data
        cached_weather = database.get_weather_data(date_str)
        if cached_weather:
            return jsonify({
                'success': True,
                'weather': cached_weather,
                'summary': weather.format_weather_summary(cached_weather)
            })
        
        # Fetch fresh weather data
        weather_data = weather.get_weather_for_date(date_str)
        if weather_data:
            database.store_weather_data(date_str, weather_data)
            return jsonify({
                'success': True,
                'weather': weather_data,
                'summary': weather.format_weather_summary(weather_data)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Weather data not available for this date'
            }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/analytics')
def analytics():
    """Render the analytics page with correlation data."""
    try:
        # Get data for the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # Get all entries for analytics
        entries_raw = database.get_timeline_data(start_date.isoformat(), end_date.isoformat())
        entries = [dict(e) for e in entries_raw]
        
        # Get weather data
        weather_data_raw = database.get_weather_data_range(start_date.isoformat(), end_date.isoformat())
        weather_data = [dict(w) for w in weather_data_raw]
        weather_by_date = {w['date']: w for w in weather_data}
        
        # Get moon phase data
        moon_data_raw = database.get_moon_phase_data_range(start_date.isoformat(), end_date.isoformat())
        moon_data = [dict(m) for m in moon_data_raw]
        moon_by_date = {m['date']: m for m in moon_data}
        
        # Process daily summaries for analytics
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            # Get entries for this date - extract date from datetime
            day_entries = [e for e in entries if e.get('datetime', '').startswith(date_str)]
            
            # Calculate averages for mood, energy, stress
            mood_values = [e['numeric_value'] for e in day_entries if e.get('entry_type') == 'mood' and e.get('numeric_value') is not None]
            energy_values = [e['numeric_value'] for e in day_entries if e.get('entry_type') == 'energy' and e.get('numeric_value') is not None]
            stress_values = [e['numeric_value'] for e in day_entries if e.get('entry_type') == 'stress' and e.get('numeric_value') is not None]
            sleep_values = [e['numeric_value'] for e in day_entries if e.get('entry_type') == 'sleep_quality' and e.get('numeric_value') is not None]
            
            # Get weather for this date
            weather = weather_by_date.get(date_str, {})
            moon = moon_by_date.get(date_str, {})
            
            # Calculate average temperature
            temp_min = weather.get('temp_min')
            temp_max = weather.get('temp_max')
            temperature = ((temp_min + temp_max) / 2) if temp_min is not None and temp_max is not None else None
            
            daily_summary = {
                'date': date_str,
                'avg_mood': sum(mood_values) / len(mood_values) if mood_values else None,
                'avg_energy': sum(energy_values) / len(energy_values) if energy_values else None,
                'avg_stress': sum(stress_values) / len(stress_values) if stress_values else None,
                'sleep_quality': sleep_values[0] if sleep_values else None,
                'temperature': temperature,
                'humidity': weather.get('humidity'),
                'air_pressure': weather.get('air_pressure'),
                'moon_illumination': moon.get('illumination_percent'),
                'weather_main': weather.get('weather_main'),
                'precipitation': weather.get('precipitation', 0)
            }
            
            daily_data.append(daily_summary)
            current_date += timedelta(days=1)
        
        return render_template('analytics.html', daily_data=daily_data)
        
    except Exception as e:
        return render_template('analytics.html', daily_data=[], error=str(e))

if __name__ == '__main__':
    database.init_db()  # Initialize the database on startup
    database.update_entry_types_for_integers()  # Update existing entry types
    app.run(host='0.0.0.0', port=8081, debug=True)