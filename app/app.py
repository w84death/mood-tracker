from flask import Flask, render_template, request, redirect, url_for
import database
import weather

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main page with the data entry form."""
    return render_template('index.html')

@app.route('/entries')
def view_entries():
    """Render a page showing all health entries with weather data."""
    conn = database.get_db_connection()  # Assuming you have a database module
    cursor = conn.cursor()
    cursor.execute('''
        SELECT de.date, de.mood, de.energy, de.sleep_quality, de.notes,
               w.temp_min, w.temp_max, w.humidity, w.pressure, w.precipitation
        FROM daily_entries de
        LEFT JOIN weather w ON de.date = w.date
        ORDER BY de.date DESC
    ''')
    entries = cursor.fetchall()
    conn.close()
    return render_template('entries.html', entries=entries)

@app.route('/submit', methods=['POST'])
def submit():
    """Handle form submission and store data in the database."""
    date = request.form['date']
    mood = int(request.form['mood'])
    energy = int(request.form['energy'])
    sleep_quality = int(request.form['sleep_quality'])
    notes = request.form['notes']
    caffeine_count = int(request.form['caffeine_count'])
    last_meal_time = request.form['last_meal_time']
    sleep_time = request.form['sleep_time']
    wake_time = request.form['wake_time']

    # Store daily entries
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO daily_entries (date, mood, energy, sleep_quality, notes) VALUES (?, ?, ?, ?, ?)',
                   (date, mood, energy, sleep_quality, notes))

    # Store lifestyle data
    cursor.execute('INSERT OR REPLACE INTO lifestyle (date, caffeine_count, last_meal_time, sleep_time, wake_time) VALUES (?, ?, ?, ?, ?)',
                   (date, caffeine_count, last_meal_time, sleep_time, wake_time))

    # Fetch and store weather data for the given date
    weather_data = weather.get_weather(date)
    if weather_data:
        cursor.execute('INSERT OR REPLACE INTO weather (date, temp_min, temp_max, humidity, pressure, precipitation) VALUES (?, ?, ?, ?, ?, ?)',
                       (date, weather_data['temp_min'], weather_data['temp_max'], weather_data['humidity'], weather_data['pressure'], weather_data['precipitation']))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    database.init_db()  # Initialize the database on startup
    app.run(host='0.0.0.0', port=8080, debug=True)
