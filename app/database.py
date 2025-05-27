import sqlite3
import os
from datetime import datetime, timedelta

# Define the database path
DB_PATH = os.path.join(os.path.dirname(__file__), '../data/health.db')

def get_db_connection():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for timeline entries (hourly slots)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timeline_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            numeric_value REAL,
            text_value TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(datetime, entry_type)
        )
    ''')

    # Table for entry types configuration
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entry_types (
            type_name TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            emoji TEXT,
            value_type TEXT NOT NULL, -- 'numeric', 'text', 'boolean'
            min_value REAL,
            max_value REAL,
            default_value TEXT,
            description TEXT
        )
    ''')

    # Table for weather data (daily)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather (
            date TEXT PRIMARY KEY,
            temp_min REAL,
            temp_max REAL,
            humidity REAL,
            pressure REAL,
            precipitation REAL,
            air_pressure REAL,
            weather_main TEXT,
            weather_description TEXT
        )
    ''')
    
    # Add new columns to existing weather table if they don't exist
    try:
        cursor.execute('ALTER TABLE weather ADD COLUMN air_pressure REAL')
    except:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE weather ADD COLUMN weather_main TEXT')
    except:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE weather ADD COLUMN weather_description TEXT')
    except:
        pass  # Column already exists

    # Table for moon phases (daily)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moon_phases (
            date TEXT PRIMARY KEY,
            phase_name TEXT,
            illumination_percent REAL
        )
    ''')

    # Insert default entry types
    default_entry_types = [
        ('mood', 'Mood', '😊', 'mood_select', 1, 5, '3', 'How are you feeling overall?'),
        ('energy', 'Energy Level', '⚡', 'energy_select', 1, 5, '3', 'Rate your energy level'),
        ('sleep_quality', 'Sleep Quality', '😴', 'sleep_select', 1, 5, '3', 'Rate your sleep quality'),
        ('caffeine', 'Caffeine', '☕', 'caffeine_select', 0, 10, '1', 'Number of caffeine servings'),
        ('meal', 'Meal', '🍽️', 'text', None, None, '', 'What did you eat?'),
        ('wake_up', 'Wake Up', '🌅', 'boolean', None, None, 'true', 'Mark when you woke up'),
        ('sleep_start', 'Bedtime', '🌙', 'boolean', None, None, 'true', 'Mark when you went to bed'),
        ('exercise', 'Exercise', '🏃', 'text', None, None, '', 'Type of exercise or activity'),
        ('water', 'Water Intake', '💧', 'water_select', 0, 20, '8', 'Glasses of water'),

        ('notes', 'General Notes', '📝', 'text', None, None, '', 'Any observations or notes'),
        ('alcohol', 'Alcohol', '🍷', 'alcohol_select', 0, 10, '0', 'Number of alcoholic drinks'),
        ('medication', 'Medication', '💊', 'text', None, None, '', 'Medications taken'),
        ('vitamins', 'Vitamins/Supplements', '🌿', 'text', None, None, '', 'Vitamins or supplements taken'),
        ('weight', 'Weight', '⚖️', 'numeric', 50, 300, '70', 'Weight in kg')
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO entry_types 
        (type_name, display_name, emoji, value_type, min_value, max_value, default_value, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', default_entry_types)

    conn.commit()
    conn.close()

def get_timeline_data(start_date, end_date):
    """Get timeline entries for a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT te.datetime, te.entry_type, te.numeric_value, te.text_value, te.notes,
               et.display_name, et.emoji, et.value_type
        FROM timeline_entries te
        JOIN entry_types et ON te.entry_type = et.type_name
        WHERE date(te.datetime) BETWEEN ? AND ?
        ORDER BY te.datetime ASC
    ''', (start_date, end_date))
    
    entries = cursor.fetchall()
    conn.close()
    return entries

def add_timeline_entry(datetime_str, entry_type, numeric_value=None, text_value=None, notes=None):
    """Add or update a timeline entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO timeline_entries 
        (datetime, entry_type, numeric_value, text_value, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime_str, entry_type, numeric_value, text_value, notes))
    
    conn.commit()
    conn.close()

def get_entry_types():
    """Get all available entry types."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM entry_types ORDER BY display_name')
    entry_types = cursor.fetchall()
    conn.close()
    return entry_types

def delete_timeline_entry(datetime_str, entry_type):
    """Delete a specific timeline entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM timeline_entries 
        WHERE datetime = ? AND entry_type = ?
    ''', (datetime_str, entry_type))
    
    conn.commit()
    conn.close()

def get_day_entries(date_str):
    """Get all entries for a specific day."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT te.datetime, te.entry_type, te.numeric_value, te.text_value, te.notes,
               et.display_name, et.emoji, et.value_type
        FROM timeline_entries te
        JOIN entry_types et ON te.entry_type = et.type_name
        WHERE date(te.datetime) = ?
        ORDER BY te.datetime ASC
    ''', (date_str,))
    
    entries = cursor.fetchall()
    conn.close()
    return entries

def get_mood_options():
    """Get mood options for dropdown."""
    return [
        {'value': 1, 'label': 'Terrible 😞', 'emoji': '😞'},
        {'value': 2, 'label': 'Bad 😔', 'emoji': '😔'},
        {'value': 3, 'label': 'Okay 😐', 'emoji': '😐'},
        {'value': 4, 'label': 'Good 😊', 'emoji': '😊'},
        {'value': 5, 'label': 'Excellent 😄', 'emoji': '😄'}
    ]

def store_weather_data(date_str, weather_data):
    """Store weather data for a specific date."""
    if not weather_data:
        return
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Handle None values properly
    temp_min = weather_data.get('temp_min') or 0
    temp_max = weather_data.get('temp_max') or 0
    humidity = weather_data.get('humidity') or 0
    pressure = weather_data.get('pressure') or 0
    precipitation = weather_data.get('precipitation') or 0
    air_pressure = weather_data.get('air_pressure') or weather_data.get('pressure') or 0
    weather_main = weather_data.get('weather_main') or ''
    weather_description = weather_data.get('weather_description') or ''
    
    cursor.execute('''
        INSERT OR REPLACE INTO weather 
        (date, temp_min, temp_max, humidity, pressure, precipitation, air_pressure, weather_main, weather_description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        date_str,
        temp_min,
        temp_max,
        humidity,
        pressure,
        precipitation,
        air_pressure,
        weather_main,
        weather_description
    ))
    
    conn.commit()
    conn.close()

def get_weather_data(date_str):
    """Get weather data for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM weather WHERE date = ?', (date_str,))
    weather = cursor.fetchone()
    conn.close()
    
    if weather:
        return dict(weather)
    return None

def get_weather_data_range(start_date, end_date):
    """Get weather data for a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM weather 
        WHERE date BETWEEN ? AND ? 
        ORDER BY date
    ''', (start_date, end_date))
    
    weather_data = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in weather_data]

def get_daily_summary_with_weather(date_str):
    """Get daily summary including weather data and mood entries."""
    # Get all entries for the day
    entries = get_day_entries(date_str)
    
    # Get weather data
    weather = get_weather_data(date_str)
    
    # Process entries into summary
    summary = {
        'date': date_str,
        'weather': weather,
        'mood_entries': [],
        'energy_entries': [],
        'sleep_quality': None,

        'notes': [],
        'activities': []
    }
    
    for entry in entries:
        if entry['entry_type'] == 'mood' and entry['numeric_value']:
            summary['mood_entries'].append({
                'time': entry['datetime'].split(' ')[1][:5],
                'value': entry['numeric_value'],
                'notes': entry['notes']
            })
        elif entry['entry_type'] == 'energy' and entry['numeric_value']:
            summary['energy_entries'].append({
                'time': entry['datetime'].split(' ')[1][:5],
                'value': entry['numeric_value'],
                'notes': entry['notes']
            })
        elif entry['entry_type'] == 'sleep_quality' and entry['numeric_value']:
            summary['sleep_quality'] = entry['numeric_value']

        elif entry['notes']:
            summary['notes'].append({
                'time': entry['datetime'].split(' ')[1][:5],
                'type': entry['display_name'],
                'text': entry['notes']
            })
        elif entry['text_value']:
            summary['activities'].append({
                'time': entry['datetime'].split(' ')[1][:5],
                'type': entry['display_name'],
                'text': entry['text_value']
            })
    
    return summary

def get_energy_options():
    """Get energy level options for dropdown."""
    return [
        {'value': 1, 'label': 'Exhausted 😴', 'emoji': '😴'},
        {'value': 2, 'label': 'Tired 😪', 'emoji': '😪'},
        {'value': 3, 'label': 'Normal ⚡', 'emoji': '⚡'},
        {'value': 4, 'label': 'Energetic 🔋', 'emoji': '🔋'},
        {'value': 5, 'label': 'Supercharged ⚡⚡', 'emoji': '⚡⚡'}
    ]

def get_sleep_options():
    """Get sleep quality options for dropdown."""
    return [
        {'value': 1, 'label': 'Terrible 😴', 'emoji': '😴'},
        {'value': 2, 'label': 'Poor 😪', 'emoji': '😪'},
        {'value': 3, 'label': 'Okay 😐', 'emoji': '😐'},
        {'value': 4, 'label': 'Good 😊', 'emoji': '😊'},
        {'value': 5, 'label': 'Excellent 😄', 'emoji': '😄'}
    ]



def get_caffeine_options():
    """Get caffeine intake options for dropdown."""
    return [
        {'value': 0, 'label': 'None ☕', 'emoji': '☕'},
        {'value': 1, 'label': '1 serving ☕', 'emoji': '☕'},
        {'value': 2, 'label': '2 servings ☕☕', 'emoji': '☕☕'},
        {'value': 3, 'label': '3 servings ☕☕☕', 'emoji': '☕☕☕'},
        {'value': 4, 'label': '4 servings ☕☕☕☕', 'emoji': '☕☕☕☕'},
        {'value': 5, 'label': '5+ servings ☕☕☕☕☕', 'emoji': '☕☕☕☕☕'}
    ]

def get_water_options():
    """Get water intake options for dropdown."""
    return [
        {'value': 0, 'label': 'None 💧', 'emoji': '💧'},
        {'value': 1, 'label': '1 glass 💧', 'emoji': '💧'},
        {'value': 2, 'label': '2 glasses 💧💧', 'emoji': '💧💧'},
        {'value': 4, 'label': '4 glasses 💧💧💧💧', 'emoji': '💧💧💧💧'},
        {'value': 6, 'label': '6 glasses 💧💧💧💧💧💧', 'emoji': '💧💧💧💧💧💧'},
        {'value': 8, 'label': '8 glasses (recommended) 💧💧💧💧💧💧💧💧', 'emoji': '💧💧💧💧💧💧💧💧'},
        {'value': 10, 'label': '10+ glasses 💧💧💧💧💧💧💧💧💧💧', 'emoji': '💧💧💧💧💧💧💧💧💧💧'}
    ]

def get_alcohol_options():
    """Get alcohol intake options for dropdown."""
    return [
        {'value': 0, 'label': 'None 🚫', 'emoji': '🚫'},
        {'value': 1, 'label': '1 drink 🍷', 'emoji': '🍷'},
        {'value': 2, 'label': '2 drinks 🍷🍷', 'emoji': '🍷🍷'},
        {'value': 3, 'label': '3 drinks 🍷🍷🍷', 'emoji': '🍷🍷🍷'},
        {'value': 4, 'label': '4 drinks 🍷🍷🍷🍷', 'emoji': '🍷🍷🍷🍷'},
        {'value': 5, 'label': '5+ drinks 🍷🍷🍷🍷🍷', 'emoji': '🍷🍷🍷🍷🍷'}
    ]

def update_entry_types_for_integers():
    """Update existing entry types to use dropdown selects and proper defaults."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update existing entry types to use dropdown selects
    updates = [
        ('caffeine', 'Caffeine', '☕', 'caffeine_select', 0, 10, '1', 'Number of caffeine servings'),
        ('water', 'Water Intake', '💧', 'water_select', 0, 20, '8', 'Glasses of water'),
        ('energy', 'Energy Level', '⚡', 'energy_select', 1, 5, '3', 'Rate your energy level'),
        ('sleep_quality', 'Sleep Quality', '😴', 'sleep_select', 1, 5, '3', 'Rate your sleep quality'),

        ('mood', 'Mood', '😊', 'mood_select', 1, 5, '3', 'How are you feeling overall?'),
        ('alcohol', 'Alcohol', '🍷', 'alcohol_select', 0, 10, '0', 'Number of alcoholic drinks')
    ]
    
    for entry_type, display_name, emoji, value_type, min_val, max_val, default_val, description in updates:
        cursor.execute('''
            UPDATE entry_types 
            SET display_name = ?, emoji = ?, value_type = ?, min_value = ?, max_value = ?, default_value = ?, description = ?
            WHERE type_name = ?
        ''', (display_name, emoji, value_type, min_val, max_val, default_val, description, entry_type))
    
    conn.commit()
    conn.close()

def store_moon_phase_data(date_str, phase_name, illumination_percent):
    """Store moon phase data for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO moon_phases 
        (date, phase_name, illumination_percent)
        VALUES (?, ?, ?)
    ''', (date_str, phase_name, illumination_percent))
    
    conn.commit()
    conn.close()

def get_moon_phase_data(date_str):
    """Get moon phase data for a specific date."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM moon_phases WHERE date = ?', (date_str,))
    moon_phase = cursor.fetchone()
    conn.close()
    
    if moon_phase:
        return dict(moon_phase)
    return None

def get_moon_phase_data_range(start_date, end_date):
    """Get moon phase data for a date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM moon_phases WHERE date BETWEEN ? AND ? ORDER BY date', 
                   (start_date, end_date))
    moon_phases = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in moon_phases]