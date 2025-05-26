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
- **Stress levels**: Monitor stress patterns
- **Exercise**: Record physical activities
- **Nutrition**: Log meals and water intake
- **Caffeine intake**: Track coffee and other stimulants
- **Custom notes**: Add detailed observations

### 📱 Modern Interface
- **Responsive design**: Works on desktop, tablet, and mobile
- **Dark mode support**: Automatic theme switching
- **Intuitive UI**: Easy-to-use timeline grid
- **Real-time updates**: Instant feedback when adding entries
- **Color-coded entries**: Visual distinction between entry types

### 📈 Analytics & Insights
- **Daily summaries**: View key metrics at a glance
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

The `run-docker.sh` script provides easy management:

```bash
./run-docker.sh start        # Start the application
./run-docker.sh stop         # Stop the application
./run-docker.sh restart      # Restart the application
./run-docker.sh rebuild      # Rebuild and restart
./run-docker.sh logs         # View real-time logs
./run-docker.sh status       # Check service status
./run-docker.sh init-db      # Initialize database
./run-docker.sh sample-data  # Add sample entries
./run-docker.sh cleanup      # Clean up Docker resources
./run-docker.sh help         # Show all commands
```

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
- **Stress** 😰: Rate 1-5 (1=relaxed, 5=very stressed)
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

## 🔧 Development

### Local Development
```bash
# Clone the repository
git clone <repository-url>
cd mood-tracker

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from app.database import init_db; init_db()"

# Run development server
python3 app/app.py
```

### Environment Variables
Create `.env` file with:
```env
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_PATH=./data/health.db
PORT=8080
```

### File Structure
```
mood-tracker/
├── app/
│   ├── app.py              # Main Flask application
│   ├── database.py         # Database operations
│   ├── weather.py          # Weather integration
│   ├── static/
│   │   └── style.css       # Unified styles
│   └── templates/
│       ├── timeline.html   # Main timeline interface
│       ├── entries.html    # Daily summaries
│       └── index.html      # Legacy form (fallback)
├── data/
│   └── health.db          # SQLite database
├── docker-compose.yml     # Docker configuration
├── Dockerfile            # Container build instructions
├── requirements.txt      # Python dependencies
├── run-docker.sh        # Docker management script
└── README.md           # This file
```

## 🌍 Browser Compatibility

- **Chrome/Chromium**: 88+
- **Firefox**: 85+
- **Safari**: 14+
- **Edge**: 88+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 88+

## 📊 Data Export

Your data is stored in SQLite format for easy analysis:

```sql
-- View all timeline entries
SELECT * FROM timeline_entries ORDER BY datetime;

-- Get mood patterns
SELECT date(datetime) as day, AVG(numeric_value) as avg_mood 
FROM timeline_entries 
WHERE entry_type = 'mood' 
GROUP BY date(datetime);
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Inter font family** by Rasmus Andersson
- **Flask framework** by the Pallets team
- **SQLite** for reliable data storage
- **Docker** for containerization

## 📞 Support

For questions, issues, or feature requests:
- **Open an issue** on GitHub
- **Check the documentation** in this README
- **Review the code** - it's well-commented!

---

**Start tracking your wellness journey today with the Timeline-Based Mood Tracker!** 🌟