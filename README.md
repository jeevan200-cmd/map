# AI-Powered Traffic Monitoring System

## Overview
An automated, AI-driven traffic monitoring system that detects, classifies, and counts vehicles using static traffic camera footage. The system visualizes traffic density on an interactive GIS map with heat maps.

## Features
- 🚗 **Vehicle Detection & Classification**: Detects and classifies bikes, cars, buses, and trucks using YOLOv8
- 📊 **Traffic Counting**: Counts vehicles crossing predefined lines or zones
- 🗺️ **GIS Visualization**: Interactive map with heat maps showing traffic density
- 📈 **Real-time Updates**: Live traffic data visualization
- 📍 **Location-based Analysis**: Traffic intensity by location and time

## Technology Stack
- **Backend**: Python, Flask, OpenCV, Ultralytics YOLOv8
- **Frontend**: HTML, CSS, JavaScript, Leaflet.js
- **Visualization**: Heat maps, markers, clustering

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access the Application
Open your browser and navigate to: `http://localhost:5000`

## Usage
1. Upload traffic camera footage or use the demo data
2. The system automatically detects and classifies vehicles
3. View traffic density on the interactive map
4. Analyze traffic patterns by time and location

## Project Structure
```
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── models/                 # AI models directory
├── static/                 # Frontend assets
│   ├── css/
│   ├── js/
│   └── images/
├── templates/              # HTML templates
├── uploads/                # Uploaded videos/images
└── data/                   # Traffic data storage
```

## License
MIT License
