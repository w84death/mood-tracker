from flask import Flask, render_template, request, redirect, url_for, jsonify
import database
import weather
from datetime import datetime, timedelta, date

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
    
    # Generate date range for template
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append({
            'date': current_date.isoformat(),
            'display': current_date.strftime('%A, %B %d'),
            'is_today': current_date == today
        })
        current_date += timedelta(days=1)
    
    return render_template('timeline.html', 
                         timeline_data=timeline_data,
                         date_range=date_range,
                         entry_types=entry_types)

@app.route('/api/add_entry', methods=['POST'])
def add_entry():
    """API endpoint to add a timeline entry."""
    data = request.get_json()
    
    try:
        date_str = data['date']
        hour = int(data['hour'])
        entry_type = data['entry_type']
        
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
    """Legacy view for entries (for backward compatibility)."""
    # Get recent timeline entries and convert to daily summary
    today = date.today()
    start_date = today - timedelta(days=30)
    
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
                'mood': None,
                'energy': None,
                'sleep_quality': None,
                'notes': []
            }
        
        daily_summaries[date_key]['entries'].append(entry)
        
        # Extract key metrics for summary
        if entry['entry_type'] == 'mood' and entry['numeric_value']:
            daily_summaries[date_key]['mood'] = entry['numeric_value']
        elif entry['entry_type'] == 'energy' and entry['numeric_value']:
            daily_summaries[date_key]['energy'] = entry['numeric_value']
        elif entry['entry_type'] == 'sleep_quality' and entry['numeric_value']:
            daily_summaries[date_key]['sleep_quality'] = entry['numeric_value']
        elif entry['notes']:
            daily_summaries[date_key]['notes'].append(entry['notes'])
    
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
            'entry_types': [dict(et) for et in entry_types]
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

if __name__ == '__main__':
    database.init_db()  # Initialize the database on startup
    app.run(host='0.0.0.0', port=8080, debug=True)