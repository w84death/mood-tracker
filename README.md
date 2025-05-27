# 🌟 Timeline-Based Mood Tracker

A modern, intuitive health and mood tracking application with a timeline-based interface that lets you log entries for any hour of any day. Track your wellness journey with flexible data entry and beautiful visualizations.

## ✨ Features

### 🕒 Timeline Interface
- **Hourly time slots**: Add entries for any hour of any day
- **Flexible data entry**: No need to fill out entire forms at once
- **Visual timeline**: See your day at a glance with color-coded entries
- **Retroactive logging**: Add entries for past days or future planning

### 📊 Health Metrics
- **Mood tracking**: Rate your mood from 1-5
- **Energy levels**: Track your energy throughout the day
- **Sleep quality**: Log how well you slept

- **Exercise**: Record physical activities
- **Nutrition**: Log meals and water intake
- **Caffeine intake**: Track coffee and other stimulants
- **Weather correlation**: Automatic weather data for mood analysis
- **Custom notes**: Add detailed observations

### 📱 Modern Interface
- **Responsive design**: Works on desktop, tablet, and mobile
- **Dark mode support**: Automatic theme switching
- **Intuitive UI**: Easy-to-use timeline grid
- **Real-time updates**: Instant feedback when adding entries
- **Color-coded entries**: Visual distinction between entry types

### 📈 Analytics & Insights
- **Daily summaries**: View key metrics at a glance
- **Weather correlation**: See how weather affects your mood and energy
- **Entry history**: Browse past entries by date
- **Pattern recognition**: Identify trends in your data
- **Export capabilities**: Data portability for analysis

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Modern web browser

### 1. Start the Application
```bash
./run-docker.sh start
```

### 2. Initialize Database
```bash
./run-docker.sh init-db
```

### 3. Add Sample Data (Optional)
```bash
./run-docker.sh sample-data
```

### 4. Open in Browser
Navigate to [http://localhost:8080](http://localhost:8080)

## 🛠 Docker Commands

Building:
```sudo docker build -t mood-tracker .```

Running:
```sudo docker run -p 8080:8080 mood-tracker```
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

### Timeline Navigation
- **Scroll horizontally** to see different days
- **Click "Go to Today"** to jump to current date
- **Use "Load More Days"** to extend the timeline
- **Hover over entries** to see details
- **Click entries** to edit or delete

### Daily Summaries
- Visit the **Entries page** for daily summaries
- See **key metrics** highlighted with color coding
- Browse **chronological history** of your entries
- Export or analyze your **long-term patterns**

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

### Database Schema
- **timeline_entries**: Hourly entries with flexible value types
- **entry_types**: Configurable entry types and metadata
- **weather**: Daily weather data integration
- **moon_phases**: Lunar cycle tracking

### Docker Setup
- **Multi-stage builds**: Optimized container sizes
- **Volume persistence**: Data survives container restarts
- **Environment configuration**: Easy customization
- **Health checks**: Automatic service monitoring

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

### Weather Features
- **Current weather**: Real-time data for today
- **5-day forecast**: Weather predictions for future dates
- **Historical weather**: Limited to free tier (requires subscription for dates older than 5 days)
- **Timeline integration**: Weather info displayed in day headers with data type indicators
- **Daily summaries**: Weather conditions shown alongside mood metrics
- **Future date restrictions**: Only notes entries allowed for future dates
- **Visual indicators**: Different styling for current, forecast, and historical data

### Weather Data Includes
- **Temperature**: Daily min/max temperatures in Celsius
- **Humidity**: Relative humidity percentage
- **Precipitation**: Rainfall amounts in millimeters
- **Weather conditions**: Clear, cloudy, rainy, etc. with emojis
- **Data type**: Indicators for current, forecast, or historical data
- **Pressure & wind**: Additional environmental metrics

### API Limitations
- **Free tier**: Current weather + 5-day forecast
- **Historical data**: Requires paid subscription for dates older than 5 days
- **Future dates**: Limited to 5-day forecast range
- **Entry restrictions**: Future dates only allow general notes

### Privacy & Data
- Weather data is cached locally in your database
- No personal location data is sent to external services
- Only coordinates (lat/lon) are used for weather lookup
- Weather data helps identify patterns but doesn't track your movements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Inter font family** by Rasmus Andersson
- **Flask framework** by the Pallets team
- **SQLite** for reliable data storage
- **Docker** for containerization

---

**Start tracking your wellness journey today with the Timeline-Based Mood Tracker!** 🌟
