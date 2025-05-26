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
            precipitation REAL
        )
    ''')

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
        ('energy', 'Energy Level', '⚡', 'numeric', 1, 5, '3', 'Rate your energy level (1-5)'),
        ('sleep_quality', 'Sleep Quality', '😴', 'numeric', 1, 5, '3', 'Rate your sleep quality (1-5)'),
        ('caffeine', 'Caffeine', '☕', 'numeric', 0, 10, '1', 'Number of caffeine servings'),
        ('meal', 'Meal', '🍽️', 'text', None, None, '', 'What did you eat?'),
        ('wake_up', 'Wake Up', '🌅', 'boolean', None, None, 'true', 'Mark when you woke up'),
        ('sleep_start', 'Bedtime', '🌙', 'boolean', None, None, 'true', 'Mark when you went to bed'),
        ('exercise', 'Exercise', '🏃', 'text', None, None, '', 'Type of exercise or activity'),
        ('water', 'Water Intake', '💧', 'numeric', 0, 20, '1', 'Glasses of water'),
        ('stress', 'Stress Level', '😰', 'numeric', 1, 5, '1', 'Rate your stress level (1-5)'),
        ('notes', 'General Notes', '📝', 'text', None, None, '', 'Any observations or notes'),
        ('alcohol', 'Alcohol', '🍷', 'numeric', 0, 10, '1', 'Number of alcoholic drinks'),
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

def update_entry_types_for_integers():
    """Update existing entry types to ensure integer inputs and proper defaults."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update existing entry types to have better defaults and descriptions
    updates = [
        ('caffeine', 'Caffeine', '☕', 'numeric', 0, 10, '1', 'Number of caffeine servings'),
        ('water', 'Water Intake', '💧', 'numeric', 0, 20, '1', 'Glasses of water'),
        ('energy', 'Energy Level', '⚡', 'numeric', 1, 5, '3', 'Rate your energy level (1-5)'),
        ('sleep_quality', 'Sleep Quality', '😴', 'numeric', 1, 5, '3', 'Rate your sleep quality (1-5)'),
        ('stress', 'Stress Level', '😰', 'numeric', 1, 5, '1', 'Rate your stress level (1-5)'),
        ('mood', 'Mood', '😊', 'mood_select', 1, 5, '3', 'How are you feeling overall?')
    ]
    
    for entry_type, display_name, emoji, value_type, min_val, max_val, default_val, description in updates:
        cursor.execute('''
            UPDATE entry_types 
            SET display_name = ?, emoji = ?, value_type = ?, min_value = ?, max_value = ?, default_value = ?, description = ?
            WHERE type_name = ?
        ''', (display_name, emoji, value_type, min_val, max_val, default_val, description, entry_type))
    
    conn.commit()
    conn.close()