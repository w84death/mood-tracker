# 🌊 MoodFlow - Personal Wellness Tracker

A modern, intuitive health and mood tracking application with a beautiful landing page and timeline-based interface. Track your wellness journey with flexible data entry, beautiful visualizations, and secure PIN-based authentication.

## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed
- Modern web browser

### Building
```sudo docker build -t mood-tracker .```

### Running
```sudo docker run -p 8080:8080 mood-tracker```

### Open in Browser
Navigate to [http://localhost:8080](http://localhost:8080)

## 📋 Usage Guide

### Adding Entries
1. **Click any time slot** on the timeline
2. **Select entry type** from the dropdown (mood, energy, meal, etc.)
3. **Enter value or description** based on the entry type
4. **Add optional notes** for additional context
5. **Save the entry** - it appears instantly on the timeline

### Entry Types
- **Mood** 😊: Rate 1-5 (1=poor, 5=excellent)
- **Energy** ⚡: Rate 1-5 (1=exhausted, 5=energetic)
- **Sleep Quality** 😴: Rate 1-5 (1=poor sleep, 5=great sleep)
- **Caffeine** ☕: Number of servings (coffee, tea, etc.)
- **Meals** 🍽️: Describe what you ate
- **Exercise** 🏃: Type and duration of activity
- **Water** 💧: Glasses or bottles consumed
- **Wake Up** 🌅: Mark when you woke up
- **Bedtime** 🌙: Mark when you went to sleep
- **Notes** 📝: General observations or thoughts

## 🏗 Architecture

### Backend
- **Flask**: Python web framework
- **SQLite**: Lightweight database for data storage
- **RESTful API**: Clean separation of concerns

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Vanilla JavaScript**: No heavy frameworks
- **Responsive design**: Mobile-first approach
- **Progressive enhancement**: Works without JavaScript

## 🌤️ Weather Integration

The mood tracker automatically fetches weather data to help correlate environmental factors with your mood and energy levels.

### Setup Weather API
1. **Get OpenWeather API Key**:
   - Visit [OpenWeatherMap](https://openweathermap.org/api)
   - Sign up for a free account
   - Generate an API key

2. **Configure Location**:
   - Set your latitude and longitude in `.env`
   - Default coordinates are for Poznań, Poland
   - Use tools like [latlong.net](https://www.latlong.net/) to find your coordinates

3. **Environment Variables**:
```env
OPENWEATHER_API_KEY=your_actual_api_key_here
LATITUDE=your_latitude
LONGITUDE=your_longitude
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Inter font family** by Rasmus Andersson
- **Flask framework** by the Pallets team
- **SQLite** for reliable data storage
- **Docker** for containerization

---

**Start tracking your wellness journey today with the Timeline-Based Mood Tracker!** 🌟
