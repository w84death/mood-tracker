import sqlite3
import os

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

    # Table for daily health entries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_entries (
            date TEXT PRIMARY KEY,
            mood INTEGER,
            energy INTEGER,
            sleep_quality INTEGER,
            notes TEXT
        )
    ''')

    # Table for lifestyle factors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lifestyle (
            date TEXT PRIMARY KEY,
            caffeine_count INTEGER,
            last_meal_time TEXT,
            sleep_time TEXT,
            wake_time TEXT
        )
    ''')

    # Table for weather data
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

    # Table for moon phases (simplified calculation can be added later)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moon_phases (
            date TEXT PRIMARY KEY,
            phase_name TEXT,
            illumination_percent REAL
        )
    ''')

    conn.commit()
    conn.close()
