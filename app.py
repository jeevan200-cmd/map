from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import numpy as np
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data', exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

VEHICLE_CATEGORIES = ['bike', 'motorcycle', 'car', 'auto_rickshaw', 'bus', 'truck', 'ambulance', 'police', 'fire_truck']

CAMERA_LOCATIONS = [
    {'id': 'cam_001', 'name': 'Times Square', 'lat': 40.7580, 'lon': -73.9855, 'location': 'New York, NY', 'road': 'Broadway'},
    {'id': 'cam_002', 'name': 'Golden Gate Bridge', 'lat': 37.8199, 'lon': -122.4783, 'location': 'San Francisco, CA', 'road': 'US-101'},
    {'id': 'cam_003', 'name': 'Hollywood Blvd', 'lat': 34.1016, 'lon': -118.3267, 'location': 'Los Angeles, CA', 'road': 'Hollywood Blvd'},
    {'id': 'cam_004', 'name': 'Magnificent Mile', 'lat': 41.8954, 'lon': -87.6246, 'location': 'Chicago, IL', 'road': 'Michigan Ave'},
    {'id': 'cam_005', 'name': 'Space Center', 'lat': 29.5519, 'lon': -95.0930, 'location': 'Houston, TX', 'road': 'NASA Pkwy'},
    {'id': 'cam_006', 'name': 'Las Vegas Strip', 'lat': 36.1147, 'lon': -115.1728, 'location': 'Las Vegas, NV', 'road': 'Las Vegas Blvd'},
    {'id': 'cam_007', 'name': 'Miami Beach', 'lat': 25.7907, 'lon': -80.1300, 'location': 'Miami, FL', 'road': 'Collins Ave'},
    {'id': 'cam_008', 'name': 'Pike Place', 'lat': 47.6097, 'lon': -122.3422, 'location': 'Seattle, WA', 'road': 'Pike St'},
]

ROAD_SEGMENTS = [
    {'id': 'road_001', 'name': 'Broadway North', 'coords': [[40.7580, -73.9855], [40.7650, -73.9800], [40.7720, -73.9750]]},
    {'id': 'road_002', 'name': 'Broadway South', 'coords': [[40.7580, -73.9855], [40.7510, -73.9910], [40.7440, -73.9960]]},
    {'id': 'road_003', 'name': 'Golden Gate North', 'coords': [[37.8199, -122.4783], [37.8350, -122.4750], [37.8500, -122.4700]]},
    {'id': 'road_004', 'name': 'Hollywood East', 'coords': [[34.1016, -118.3267], [34.1016, -118.3100], [34.1016, -118.2900]]},
    {'id': 'road_005', 'name': 'Michigan Ave North', 'coords': [[41.8954, -87.6246], [41.9050, -87.6246], [41.9150, -87.6246]]},
    {'id': 'road_006', 'name': 'Las Vegas Blvd', 'coords': [[36.1147, -115.1728], [36.1250, -115.1700], [36.1350, -115.1680]]},
    {'id': 'road_007', 'name': 'Collins Ave', 'coords': [[25.7907, -80.1300], [25.8000, -80.1280], [25.8100, -80.1260]]},
    {'id': 'road_008', 'name': 'Pike St', 'coords': [[47.6097, -122.3422], [47.6150, -122.3400], [47.6200, -122.3380]]},
]

POIS = [
    {'id': 'poi_001', 'name': 'Statue of Liberty', 'lat': 40.6892, 'lon': -74.0445, 'category': 'monument', 'rating': 4.8, 'description': 'Iconic symbol of freedom'},
    {'id': 'poi_002', 'name': 'Central Park', 'lat': 40.7829, 'lon': -73.9654, 'category': 'park', 'rating': 4.9, 'description': 'Urban oasis in Manhattan'},
    {'id': 'poi_003', 'name': 'Golden Gate Park', 'lat': 37.7694, 'lon': -122.4862, 'category': 'park', 'rating': 4.7, 'description': 'Large urban park'},
    {'id': 'poi_004', 'name': 'Hollywood Sign', 'lat': 34.1341, 'lon': -118.3215, 'category': 'landmark', 'rating': 4.6, 'description': 'Famous landmark'},
    {'id': 'poi_005', 'name': 'Navy Pier', 'lat': 41.8917, 'lon': -87.6063, 'category': 'entertainment', 'rating': 4.5, 'description': 'Lakefront entertainment'},
    {'id': 'poi_006', 'name': 'Space Center Houston', 'lat': 29.5519, 'lon': -95.0930, 'category': 'museum', 'rating': 4.7, 'description': 'NASA visitor center'},
    {'id': 'poi_007', 'name': 'Bellagio Fountains', 'lat': 36.1126, 'lon': -115.1767, 'category': 'attraction', 'rating': 4.8, 'description': 'Famous water show'},
    {'id': 'poi_008', 'name': 'South Beach', 'lat': 25.7825, 'lon': -80.1340, 'category': 'beach', 'rating': 4.6, 'description': 'Iconic beach destination'},
]

EMERGENCY_SERVICES = [
    {'id': 'hosp_001', 'name': 'NYC General Hospital', 'lat': 40.7370, 'lon': -73.9750, 'type': 'hospital', 'phone': '911'},
    {'id': 'hosp_002', 'name': 'SF Medical Center', 'lat': 37.7630, 'lon': -122.4580, 'type': 'hospital', 'phone': '911'},
    {'id': 'police_001', 'name': 'NYPD Precinct 1', 'lat': 40.7128, 'lon': -74.0060, 'type': 'police', 'phone': '911'},
    {'id': 'fire_001', 'name': 'FDNY Station 1', 'lat': 40.7200, 'lon': -73.9980, 'type': 'fire_station', 'phone': '911'},
    {'id': 'hosp_003', 'name': 'LA Medical Center', 'lat': 34.0700, 'lon': -118.3000, 'type': 'hospital', 'phone': '911'},
    {'id': 'police_002', 'name': 'LAPD Central', 'lat': 34.0530, 'lon': -118.2450, 'type': 'police', 'phone': '911'},
]

DISASTER_ZONES = [
    {'id': 'flood_001', 'name': 'Hudson River Flood Zone', 'lat': 40.7580, 'lon': -74.0000, 'type': 'flood', 'risk': 'medium', 'radius': 2000},
    {'id': 'quake_001', 'name': 'San Andreas Fault Zone', 'lat': 37.7749, 'lon': -122.4194, 'type': 'earthquake', 'risk': 'high', 'radius': 5000},
    {'id': 'hurricane_001', 'name': 'Miami Hurricane Zone', 'lat': 25.7617, 'lon': -80.1918, 'type': 'hurricane', 'risk': 'high', 'radius': 10000},
]

TRAFFIC_SIGNALS = [
    {'id': 'sig_001', 'lat': 40.7580, 'lon': -73.9855, 'intersection': 'Broadway & 42nd'},
    {'id': 'sig_002', 'lat': 37.8199, 'lon': -122.4783, 'intersection': 'GG Bridge South'},
    {'id': 'sig_003', 'lat': 34.1016, 'lon': -118.3267, 'intersection': 'Hollywood & Highland'},
    {'id': 'sig_004', 'lat': 41.8954, 'lon': -87.6246, 'intersection': 'Michigan & Chicago'},
    {'id': 'sig_005', 'lat': 36.1147, 'lon': -115.1728, 'intersection': 'Las Vegas Blvd & Flamingo'},
]

PARKING_LOTS = [
    {'id': 'park_001', 'name': 'Times Square Parking', 'lat': 40.7550, 'lon': -73.9850, 'capacity': 500, 'rate': '$8/hr'},
    {'id': 'park_002', 'name': 'Hollywood Garage', 'lat': 34.0980, 'lon': -118.3250, 'capacity': 300, 'rate': '$5/hr'},
    {'id': 'park_003', 'name': 'Vegas Strip Parking', 'lat': 36.1100, 'lon': -115.1700, 'capacity': 1000, 'rate': '$3/hr'},
    {'id': 'park_004', 'name': 'Miami Beach Lot', 'lat': 25.7850, 'lon': -80.1280, 'capacity': 200, 'rate': '$4/hr'},
]

community_reports = []

def get_congestion(density):
    if density < 30: return {'level': 'free_flow', 'color': '#00ff00', 'label': 'Free Flow', 'speed': 55}
    elif density < 60: return {'level': 'moderate', 'color': '#ffff00', 'label': 'Moderate', 'speed': 35}
    elif density < 85: return {'level': 'heavy', 'color': '#ff8c00', 'label': 'Heavy', 'speed': 20}
    elif density < 95: return {'level': 'severe', 'color': '#ff0000', 'label': 'Severe', 'speed': 10}
    else: return {'level': 'standstill', 'color': '#8b0000', 'label': 'Standstill', 'speed': 2}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/cameras')
def get_cameras():
    return jsonify(CAMERA_LOCATIONS)

@app.route('/api/traffic-data')
def get_traffic_data():
    data = []
    for cam in CAMERA_LOCATIONS:
        counts = {'bike': np.random.randint(10, 60), 'motorcycle': np.random.randint(15, 90),
                  'car': np.random.randint(150, 600), 'auto_rickshaw': np.random.randint(5, 40),
                  'bus': np.random.randint(8, 35), 'truck': np.random.randint(12, 70),
                  'ambulance': np.random.randint(0, 5), 'police': np.random.randint(0, 4), 'fire_truck': np.random.randint(0, 2)}
        total = sum(counts.values())
        density = min(100, (total / 900) * 100)
        cong = get_congestion(density)
        data.append({**cam, 'vehicle_counts': counts, 'total_vehicles': total, 'density': round(density, 1),
                     'congestion': cong, 'avg_speed': cong['speed'], 'pedestrians': np.random.randint(20, 300),
                     'timestamp': datetime.now().isoformat()})
    return jsonify(data)

@app.route('/api/road-segments')
def get_road_segments():
    segments = []
    for road in ROAD_SEGMENTS:
        density = np.random.randint(10, 100)
        cong = get_congestion(density)
        segments.append({**road, 'density': density, 'congestion': cong, 'vehicles': np.random.randint(50, 400)})
    return jsonify(segments)

@app.route('/api/heatmap-data')
def get_heatmap_data():
    points = []
    for cam in CAMERA_LOCATIONS:
        # Generate dense cluster around camera location
        base_intensity = np.random.uniform(0.6, 1.0)
        for _ in range(40):
            # Core points - high intensity near center
            points.append({'lat': cam['lat'] + np.random.normal(0, 0.005),
                          'lon': cam['lon'] + np.random.normal(0, 0.005),
                          'intensity': base_intensity * np.random.uniform(0.8, 1.0)})
        for _ in range(30):
            # Medium range points
            points.append({'lat': cam['lat'] + np.random.normal(0, 0.015),
                          'lon': cam['lon'] + np.random.normal(0, 0.015),
                          'intensity': base_intensity * np.random.uniform(0.4, 0.7)})
        for _ in range(20):
            # Outer range points
            points.append({'lat': cam['lat'] + np.random.normal(0, 0.03),
                          'lon': cam['lon'] + np.random.normal(0, 0.03),
                          'intensity': np.random.uniform(0.2, 0.4)})
    # Add some random hot spots between cities for road traffic
    hot_spots = [
        (39.0, -84.0), (38.0, -90.0), (35.0, -106.0), (33.5, -112.0), (32.7, -117.0)
    ]
    for lat, lon in hot_spots:
        for _ in range(15):
            points.append({'lat': lat + np.random.uniform(-0.02, 0.02),
                          'lon': lon + np.random.uniform(-0.02, 0.02),
                          'intensity': np.random.uniform(0.3, 0.6)})
    return jsonify(points)

@app.route('/api/traffic-signals')
def get_signals():
    signals = []
    for sig in TRAFFIC_SIGNALS:
        status = random.choice(['green', 'yellow', 'red'])
        signals.append({**sig, 'status': status, 'queue': np.random.randint(0, 25),
                       'wait_time': np.random.randint(5, 120), 'adaptive': True, 'cycle': np.random.randint(30, 90)})
    return jsonify(signals)

@app.route('/api/pois')
def get_pois():
    pois = []
    for poi in POIS:
        pois.append({**poi, 'crowd': random.choice(['low', 'medium', 'high']),
                    'wait_time': np.random.randint(0, 45), 'open': random.choice([True, True, True, False])})
    return jsonify(pois)

@app.route('/api/emergency-services')
def get_emergency():
    return jsonify(EMERGENCY_SERVICES)

@app.route('/api/disaster-zones')
def get_disasters():
    zones = []
    for z in DISASTER_ZONES:
        zones.append({**z, 'active': random.choice([False, False, False, True]),
                     'alert_level': random.choice(['watch', 'warning', 'emergency'])})
    return jsonify(zones)

@app.route('/api/parking')
def get_parking():
    lots = []
    for p in PARKING_LOTS:
        avail = np.random.randint(0, p['capacity'])
        lots.append({**p, 'available': avail, 'occupancy': round((1 - avail/p['capacity']) * 100, 1)})
    return jsonify(lots)

@app.route('/api/reports', methods=['GET', 'POST'])
def handle_reports():
    global community_reports
    if request.method == 'POST':
        data = request.json
        report = {'id': f'rep_{len(community_reports)+1}', 'type': data.get('type', 'general'),
                  'description': data.get('description', ''), 'lat': data.get('lat'), 'lon': data.get('lon'),
                  'timestamp': datetime.now().isoformat(), 'verified': False, 'upvotes': 0}
        community_reports.append(report)
        return jsonify({'success': True, 'report': report})
    return jsonify(community_reports[-30:])

@app.route('/api/reports/<rid>/upvote', methods=['POST'])
def upvote(rid):
    for r in community_reports:
        if r['id'] == rid: r['upvotes'] += 1; return jsonify({'success': True})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/predictions')
def predictions():
    preds = []
    for cam in CAMERA_LOCATIONS[:5]:
        hourly = [{'hour': h, 'count': (250 if 7<=h<=9 or 17<=h<=19 else 120) + np.random.randint(-40, 60),
                   'confidence': round(np.random.uniform(0.75, 0.95), 2)} for h in range(24)]
        preds.append({'camera_id': cam['id'], 'name': cam['name'], 'predictions': hourly})
    return jsonify(preds)

@app.route('/api/analytics')
def analytics():
    return jsonify({'total_cameras': len(CAMERA_LOCATIONS), 'active_cameras': len(CAMERA_LOCATIONS),
                    'vehicles_today': np.random.randint(80000, 150000), 'avg_congestion': round(np.random.uniform(35, 70), 1),
                    'incidents': np.random.randint(3, 18), 'resolved': np.random.randint(2, 12),
                    'aqi': np.random.randint(25, 160), 'carbon_tons': round(np.random.uniform(80, 350), 1),
                    'pedestrians': np.random.randint(15000, 60000), 'emergency_calls': np.random.randint(8, 30)})

@app.route('/api/route', methods=['POST'])
def route():
    return jsonify({'routes': [
        {'name': 'Fastest', 'time': np.random.randint(12, 40), 'dist': round(np.random.uniform(4, 18), 1), 'traffic': 'low'},
        {'name': 'Shortest', 'time': np.random.randint(18, 50), 'dist': round(np.random.uniform(3, 12), 1), 'traffic': 'medium'},
        {'name': 'Eco-Friendly', 'time': np.random.randint(20, 55), 'dist': round(np.random.uniform(5, 20), 1), 'traffic': 'low', 'carbon_saved': '18%'}
    ]})

@app.route('/api/historical')
def historical():
    hours = list(range(24))
    return jsonify({'hours': hours, 'bikes': [np.random.randint(25, 90) for _ in hours],
                    'cars': [np.random.randint(180, 500) for _ in hours], 'buses': [np.random.randint(12, 50) for _ in hours],
                    'trucks': [np.random.randint(25, 90) for _ in hours]})

@app.route('/api/camera/<cid>')
def camera_detail(cid):
    cam = next((c for c in CAMERA_LOCATIONS if c['id'] == cid), None)
    if not cam: return jsonify({'error': 'Not found'}), 404
    counts = {c: np.random.randint(15, 120) for c in VEHICLE_CATEGORIES}
    hourly = [{'hour': f'{h:02d}:00', 'total': np.random.randint(120, 550)} for h in range(6)]
    density = np.random.randint(20, 90)
    return jsonify({'camera': cam, 'vehicle_counts': counts, 'total': sum(counts.values()),
                    'hourly': hourly, 'congestion': get_congestion(density), 'timestamp': datetime.now().isoformat()})

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files: return jsonify({'error': 'No file'}), 400
    f = request.files['file']
    if f.filename == '': return jsonify({'error': 'No file'}), 400
    fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{f.filename}"
    f.save(os.path.join(app.config['UPLOAD_FOLDER'], fname))
    return jsonify({'success': True, 'file': fname, 'detections': np.random.randint(15, 60),
                    'counts': {c: np.random.randint(1, 25) for c in VEHICLE_CATEGORIES[:6]}})

if __name__ == '__main__':
    print("🚗 Smart City Traffic Platform Starting...")
    print("📍 Public: http://localhost:5000")
    print("📊 Admin: http://localhost:5000/admin")
    app.run(debug=True, host='0.0.0.0', port=5000)
