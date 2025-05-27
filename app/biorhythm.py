import math
import os
from datetime import datetime, date, timedelta
from typing import Dict, List, Any

def get_birth_date() -> date:
    """Get birth date from environment variable."""
    birth_date_str = os.getenv('BIRTH_DATE')
    if not birth_date_str:
        raise ValueError("BIRTH_DATE not set in environment variables")
    
    try:
        return datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    except ValueError:
        raise ValueError("BIRTH_DATE must be in YYYY-MM-DD format")

def calculate_days_since_birth(birth_date: date, target_date: date) -> int:
    """Calculate the number of days between birth date and target date."""
    return (target_date - birth_date).days

def calculate_biorhythm_value(days_since_birth: int, cycle_length: int) -> float:
    """Calculate biorhythm value for a given cycle."""
    return math.sin(2 * math.pi * days_since_birth / cycle_length)

def get_biorhythm_status(value: float) -> str:
    """Get biorhythm status based on value."""
    if abs(value) < 0.1:
        return "critical"
    elif value > 0:
        return "positive"
    else:
        return "negative"

def get_biorhythm_percentage(value: float) -> int:
    """Convert biorhythm value to percentage (0-100)."""
    return round((value + 1) * 50)

def calculate_biorhythms(target_date: date) -> Dict[str, Dict[str, Any]]:
    """Calculate all biorhythm cycles for a given date."""
    try:
        birth_date = get_birth_date()
        days_since_birth = calculate_days_since_birth(birth_date, target_date)
        
        cycles = {
            'physical': 23,
            'emotional': 28,
            'intellectual': 33
        }
        
        biorhythms = {}
        
        for cycle_name, cycle_length in cycles.items():
            value = calculate_biorhythm_value(days_since_birth, cycle_length)
            status = get_biorhythm_status(value)
            percentage = get_biorhythm_percentage(value)
            
            biorhythms[cycle_name] = {
                'value': round(value, 3),
                'status': status,
                'percentage': percentage,
                'cycle_length': cycle_length,
                'days_since_birth': days_since_birth
            }
        
        return biorhythms
        
    except Exception:
        # Return empty dict if birth date not configured
        return {}

def get_biorhythm_data_range(start_date: date, end_date: date) -> List[Dict]:
    """Get biorhythm data for a date range."""
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        biorhythms = calculate_biorhythms(current_date)
        if biorhythms:  # Only add if birth date is configured
            data.append({
                'date': current_date.isoformat(),
                'biorhythms': biorhythms
            })
        current_date = current_date + timedelta(days=1)
    
    return data

def get_biorhythm_emoji(cycle_name: str, status: str) -> str:
    """Get emoji representation for biorhythm status."""
    emojis = {
        'physical': {
            'positive': '💪',
            'negative': '😴',
            'critical': '⚠️'
        },
        'emotional': {
            'positive': '😊',
            'negative': '😔',
            'critical': '🤔'
        },
        'intellectual': {
            'positive': '🧠',
            'negative': '😵',
            'critical': '💭'
        }
    }
    
    return emojis.get(cycle_name, {}).get(status, '❓')

def get_biorhythm_description(cycle_name: str, status: str) -> str:
    """Get human-readable description for biorhythm status."""
    descriptions = {
        'physical': {
            'positive': 'High physical energy and stamina',
            'negative': 'Low physical energy, rest recommended',
            'critical': 'Physical transition period, be cautious'
        },
        'emotional': {
            'positive': 'Positive emotional state and creativity',
            'negative': 'Lower emotional resilience, practice self-care',
            'critical': 'Emotional sensitivity heightened'
        },
        'intellectual': {
            'positive': 'Sharp mental focus and analytical thinking',
            'negative': 'Reduced mental clarity, avoid complex decisions',
            'critical': 'Mental transition, good for reflection'
        }
    }
    
    return descriptions.get(cycle_name, {}).get(status, 'Unknown status')