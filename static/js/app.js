// Smart City Traffic Platform - Main Application
let map, heatmapLayer, markersLayer, roadsLayer, signalsLayer, poisLayer, emergencyLayer, disasterLayer, parkingLayer, reportsLayer;
let trafficData = [], roadSegments = [], reportLocation = null;

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    loadAllData();
    setupEventListeners();
    startTimers();
});

function initMap() {
    map = L.map('map').setView([39.8283, -98.5795], 4);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap', maxZoom: 19
    }).addTo(map);
    
    markersLayer = L.layerGroup().addTo(map);
    roadsLayer = L.layerGroup().addTo(map);
    signalsLayer = L.layerGroup();
    poisLayer = L.layerGroup();
    emergencyLayer = L.layerGroup();
    disasterLayer = L.layerGroup();
    parkingLayer = L.layerGroup();
    reportsLayer = L.layerGroup();
    
    map.on('click', (e) => {
        reportLocation = e.latlng;
        L.popup().setLatLng(e.latlng).setContent('📍 Report location set here').openOn(map);
    });
}

async function loadAllData() {
    await Promise.all([loadTrafficData(), loadRoadSegments(), loadHeatmap()]);
    loadPredictions(); loadAnalytics();
}

async function loadTrafficData() {
    try {
        const res = await fetch('/api/traffic-data');
        trafficData = await res.json();
        updateStats(); updateMarkers(); updateCameraList();
    } catch (e) { console.error('Traffic data error:', e); }
}

async function loadRoadSegments() {
    try {
        const res = await fetch('/api/road-segments');
        roadSegments = await res.json();
        updateRoads();
    } catch (e) { console.error('Road segments error:', e); }
}

async function loadHeatmap() {
    try {
        const res = await fetch('/api/heatmap-data');
        const data = await res.json();
        if (heatmapLayer) map.removeLayer(heatmapLayer);
        const points = data.map(p => [p.lat, p.lon, p.intensity]);
        heatmapLayer = L.heatLayer(points, { 
            radius: 35, 
            blur: 25, 
            maxZoom: 17,
            max: 1.0,
            minOpacity: 0.4,
            gradient: { 
                0.0: '#00ff00', 
                0.25: '#7fff00',
                0.5: '#ffff00', 
                0.75: '#ff8c00',
                1.0: '#ff0000' 
            }
        });
        if (document.getElementById('toggleHeatmap').checked) heatmapLayer.addTo(map);
    } catch (e) { console.error('Heatmap error:', e); }
}

async function loadSignals() {
    try {
        const res = await fetch('/api/traffic-signals');
        const signals = await res.json();
        signalsLayer.clearLayers();
        signals.forEach(sig => {
            const icon = L.divIcon({ className: '', html: `<div class="signal-marker ${sig.status}">
                <i class="fas fa-traffic-light"></i></div>`, iconSize: [24, 24], iconAnchor: [12, 12] });
            const marker = L.marker([sig.lat, sig.lon], { icon });
            marker.bindPopup(`<div class="popup-content"><h3>Traffic Signal</h3>
                <p><strong>${sig.intersection}</strong></p>
                <p>Status: <span style="color:${sig.status === 'green' ? '#00aa00' : sig.status === 'red' ? '#ff0000' : '#aa8800'}">${sig.status.toUpperCase()}</span></p>
                <p>Queue: ${sig.queue} vehicles</p><p>Wait time: ~${sig.wait_time}s</p>
                <p>Adaptive Mode: ${sig.adaptive ? '✅ ON' : '❌ OFF'}</p></div>`);
            signalsLayer.addLayer(marker);
        });
    } catch (e) { console.error('Signals error:', e); }
}

async function loadPOIs() {
    try {
        const res = await fetch('/api/pois');
        const pois = await res.json();
        poisLayer.clearLayers();
        const icons = { monument: '🗽', park: '🌳', landmark: '🏛️', entertainment: '🎡', museum: '🏛️', attraction: '⛲', beach: '🏖️' };
        pois.forEach(poi => {
            const icon = L.divIcon({ className: '', html: `<div class="poi-marker">${icons[poi.category] || '📍'}</div>`,
                iconSize: [30, 30], iconAnchor: [15, 15] });
            const marker = L.marker([poi.lat, poi.lon], { icon });
            marker.bindPopup(`<div class="popup-content"><h3>${poi.name}</h3>
                <p>${poi.description}</p><p>⭐ ${poi.rating}/5</p>
                <p>Crowd: ${poi.crowd}</p><p>${poi.open ? '🟢 Open' : '🔴 Closed'}</p></div>`);
            poisLayer.addLayer(marker);
        });
    } catch (e) { console.error('POIs error:', e); }
}

async function loadEmergency() {
    try {
        const res = await fetch('/api/emergency-services');
        const services = await res.json();
        emergencyLayer.clearLayers();
        const icons = { hospital: 'fa-hospital', police: 'fa-shield-alt', fire_station: 'fa-fire-extinguisher' };
        services.forEach(svc => {
            const icon = L.divIcon({ className: '', html: `<div class="emergency-marker ${svc.type}">
                <i class="fas ${icons[svc.type] || 'fa-building'}"></i></div>`, iconSize: [32, 32], iconAnchor: [16, 16] });
            const marker = L.marker([svc.lat, svc.lon], { icon });
            marker.bindPopup(`<div class="popup-content"><h3>${svc.name}</h3>
                <p>Type: ${svc.type.replace('_', ' ')}</p><p>📞 ${svc.phone}</p></div>`);
            emergencyLayer.addLayer(marker);
        });
    } catch (e) { console.error('Emergency error:', e); }
}

async function loadDisaster() {
    try {
        const res = await fetch('/api/disaster-zones');
        const zones = await res.json();
        disasterLayer.clearLayers();
        const colors = { flood: '#1e90ff', earthquake: '#8b4513', hurricane: '#ff6347' };
        zones.forEach(z => {
            const circle = L.circle([z.lat, z.lon], { radius: z.radius, color: colors[z.type] || '#ff0000',
                fillColor: colors[z.type] || '#ff0000', fillOpacity: 0.2, weight: 2 });
            circle.bindPopup(`<div class="popup-content"><h3>⚠️ ${z.name}</h3>
                <p>Type: ${z.type}</p><p>Risk: ${z.risk.toUpperCase()}</p>
                <p>Status: ${z.active ? '🔴 ACTIVE ALERT' : '🟢 Monitored'}</p></div>`);
            disasterLayer.addLayer(circle);
        });
    } catch (e) { console.error('Disaster error:', e); }
}

async function loadParking() {
    try {
        const res = await fetch('/api/parking');
        const lots = await res.json();
        parkingLayer.clearLayers();
        lots.forEach(lot => {
            const color = lot.available > 50 ? '#00aa00' : lot.available > 10 ? '#ff8c00' : '#ff0000';
            const icon = L.divIcon({ className: '', html: `<div class="poi-marker" style="border:2px solid ${color}">🅿️</div>`,
                iconSize: [30, 30], iconAnchor: [15, 15] });
            const marker = L.marker([lot.lat, lot.lon], { icon });
            marker.bindPopup(`<div class="popup-content"><h3>${lot.name}</h3>
                <p>Available: <strong style="color:${color}">${lot.available}</strong> / ${lot.capacity}</p>
                <p>Rate: ${lot.rate}</p><p>Occupancy: ${lot.occupancy}%</p></div>`);
            parkingLayer.addLayer(marker);
        });
    } catch (e) { console.error('Parking error:', e); }
}

async function loadReports() {
    try {
        const res = await fetch('/api/reports');
        const reports = await res.json();
        reportsLayer.clearLayers();
        const icons = { accident: '🚗💥', congestion: '🚦', construction: '🚧', hazard: '⚠️', police: '👮', closure: '🚫' };
        reports.forEach(r => {
            if (!r.lat || !r.lon) return;
            const icon = L.divIcon({ className: '', html: `<div class="poi-marker">${icons[r.type] || '📢'}</div>`,
                iconSize: [30, 30], iconAnchor: [15, 15] });
            const marker = L.marker([r.lat, r.lon], { icon });
            marker.bindPopup(`<div class="popup-content"><h3>${r.type.toUpperCase()}</h3>
                <p>${r.description || 'No description'}</p><p>👍 ${r.upvotes} upvotes</p>
                <p>${new Date(r.timestamp).toLocaleString()}</p></div>`);
            reportsLayer.addLayer(marker);
        });
    } catch (e) { console.error('Reports error:', e); }
}

async function loadPredictions() {
    try {
        const res = await fetch('/api/predictions');
        const preds = await res.json();
        if (preds.length > 0) {
            const hour = new Date().getHours();
            const nextHour = preds[0].predictions.find(p => p.hour === (hour + 1) % 24) || preds[0].predictions[0];
            document.getElementById('predVehicles').textContent = nextHour.count;
            document.getElementById('predCongestion').textContent = nextHour.count > 200 ? 'High' : nextHour.count > 100 ? 'Medium' : 'Low';
            document.getElementById('predAdvice').textContent = nextHour.count > 200 ? 'Avoid rush hour' : 'Good to travel';
        }
    } catch (e) { console.error('Predictions error:', e); }
}

async function loadAnalytics() {
    try {
        const res = await fetch('/api/analytics');
        const data = await res.json();
        document.getElementById('envAQI').textContent = data.aqi;
        document.getElementById('envCarbon').textContent = data.carbon_tons;
    } catch (e) { console.error('Analytics error:', e); }
}

function updateStats() {
    let total = 0, bikes = 0, motos = 0, cars = 0, autos = 0, buses = 0, trucks = 0, ambs = 0, police = 0, peds = 0;
    trafficData.forEach(d => {
        total += d.total_vehicles; peds += d.pedestrians || 0;
        bikes += d.vehicle_counts.bike || 0; motos += d.vehicle_counts.motorcycle || 0;
        cars += d.vehicle_counts.car || 0; autos += d.vehicle_counts.auto_rickshaw || 0;
        buses += d.vehicle_counts.bus || 0; trucks += d.vehicle_counts.truck || 0;
        ambs += d.vehicle_counts.ambulance || 0; police += d.vehicle_counts.police || 0;
    });
    const avgCong = trafficData.length ? (trafficData.reduce((a, d) => a + d.density, 0) / trafficData.length).toFixed(0) : 0;
    document.getElementById('statCameras').textContent = trafficData.length;
    document.getElementById('statVehicles').textContent = total.toLocaleString();
    document.getElementById('statCongestion').textContent = avgCong + '%';
    document.getElementById('statPedestrians').textContent = peds.toLocaleString();
    document.getElementById('cntBike').textContent = bikes; document.getElementById('cntMoto').textContent = motos;
    document.getElementById('cntCar').textContent = cars; document.getElementById('cntAuto').textContent = autos;
    document.getElementById('cntBus').textContent = buses; document.getElementById('cntTruck').textContent = trucks;
    document.getElementById('cntAmb').textContent = ambs; document.getElementById('cntPolice').textContent = police;
}

function updateMarkers() {
    markersLayer.clearLayers();
    trafficData.forEach(cam => {
        const level = cam.congestion.level;
        const icon = L.divIcon({ className: '', html: `<div class="custom-marker ${level}"><i class="fas fa-video"></i></div>`,
            iconSize: [35, 35], iconAnchor: [17, 17] });
        const marker = L.marker([cam.lat, cam.lon], { icon });
        marker.bindPopup(`<div class="popup-content"><h3>${cam.name}</h3>
            <p><i class="fas fa-map-marker-alt"></i> ${cam.location}</p>
            <p><i class="fas fa-road"></i> ${cam.road}</p>
            <p><strong>Total:</strong> ${cam.total_vehicles} vehicles</p>
            <p><strong>Speed:</strong> ${cam.avg_speed} mph</p>
            <p><strong>Pedestrians:</strong> ${cam.pedestrians}</p>
            <div class="popup-stats">
                <div class="popup-stat"><i class="fas fa-car"></i> ${cam.vehicle_counts.car}</div>
                <div class="popup-stat"><i class="fas fa-bus"></i> ${cam.vehicle_counts.bus}</div>
                <div class="popup-stat"><i class="fas fa-truck"></i> ${cam.vehicle_counts.truck}</div>
                <div class="popup-stat"><i class="fas fa-motorcycle"></i> ${cam.vehicle_counts.motorcycle}</div>
            </div>
            <button class="popup-btn" onclick="showCameraDetail('${cam.id}')">View Details</button></div>`);
        markersLayer.addLayer(marker);
    });
}

function updateRoads() {
    roadsLayer.clearLayers();
    roadSegments.forEach(road => {
        const polyline = L.polyline(road.coords, { color: road.congestion.color, weight: 6, opacity: 0.8 });
        polyline.bindPopup(`<div class="popup-content"><h3>${road.name}</h3>
            <p>Density: ${road.density}%</p><p>Vehicles: ${road.vehicles}</p>
            <p>Status: ${road.congestion.label}</p></div>`);
        roadsLayer.addLayer(polyline);
    });
}

function updateCameraList() {
    const list = document.getElementById('cameraList');
    list.innerHTML = '';
    trafficData.forEach(cam => {
        const item = document.createElement('div');
        item.className = 'camera-item';
        item.innerHTML = `<div class="name">${cam.name}</div><div class="loc">${cam.location}</div>
            <div class="stats"><span>${cam.total_vehicles} vehicles</span>
            <span class="congestion-badge ${cam.congestion.level}">${cam.congestion.label}</span></div>`;
        item.onclick = () => { map.setView([cam.lat, cam.lon], 14); showCameraDetail(cam.id); };
        list.appendChild(item);
    });
}

async function showCameraDetail(cid) {
    try {
        const res = await fetch(`/api/camera/${cid}`);
        const data = await res.json();
        const cam = data.camera;
        document.getElementById('modalBody').innerHTML = `
            <div class="modal-header"><h2>${cam.name}</h2><p><i class="fas fa-map-marker-alt"></i> ${cam.location}</p></div>
            <div class="modal-stats">
                <div class="modal-stat"><div class="modal-stat-value">${data.total}</div><div class="modal-stat-label">Total Vehicles</div></div>
                <div class="modal-stat"><div class="modal-stat-value">${data.congestion.speed} mph</div><div class="modal-stat-label">Avg Speed</div></div>
                <div class="modal-stat"><div class="modal-stat-value">${data.congestion.label}</div><div class="modal-stat-label">Status</div></div>
            </div>
            <h4>Vehicle Breakdown</h4>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px;">
                ${Object.entries(data.vehicle_counts).map(([k, v]) => `<div class="modal-stat"><div class="modal-stat-value">${v}</div><div class="modal-stat-label">${k}</div></div>`).join('')}
            </div>
            <div class="chart-container"><canvas id="detailChart"></canvas></div>`;
        document.getElementById('modal').classList.remove('hidden');
        setTimeout(() => {
            new Chart(document.getElementById('detailChart'), {
                type: 'bar', data: { labels: data.hourly.map(h => h.hour), datasets: [{ label: 'Vehicles',
                    data: data.hourly.map(h => h.total), backgroundColor: '#1a73e8' }] },
                options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
            });
        }, 100);
    } catch (e) { console.error('Camera detail error:', e); }
}

function closeModal() { document.getElementById('modal').classList.add('hidden'); }

function setupEventListeners() {
    document.getElementById('toggleHeatmap').addEventListener('change', e => e.target.checked ? heatmapLayer?.addTo(map) : map.removeLayer(heatmapLayer));
    document.getElementById('toggleCameras').addEventListener('change', e => e.target.checked ? markersLayer.addTo(map) : map.removeLayer(markersLayer));
    document.getElementById('toggleRoads').addEventListener('change', e => e.target.checked ? roadsLayer.addTo(map) : map.removeLayer(roadsLayer));
    document.getElementById('toggleSignals').addEventListener('change', e => { if (e.target.checked) { loadSignals(); signalsLayer.addTo(map); } else map.removeLayer(signalsLayer); });
    document.getElementById('togglePOIs').addEventListener('change', e => { if (e.target.checked) { loadPOIs(); poisLayer.addTo(map); } else map.removeLayer(poisLayer); });
    document.getElementById('toggleEmergency').addEventListener('change', e => { if (e.target.checked) { loadEmergency(); emergencyLayer.addTo(map); } else map.removeLayer(emergencyLayer); });
    document.getElementById('toggleDisaster').addEventListener('change', e => { if (e.target.checked) { loadDisaster(); disasterLayer.addTo(map); } else map.removeLayer(disasterLayer); });
    document.getElementById('toggleParking').addEventListener('change', e => { if (e.target.checked) { loadParking(); parkingLayer.addTo(map); } else map.removeLayer(parkingLayer); });
    document.getElementById('toggleReports').addEventListener('change', e => { if (e.target.checked) { loadReports(); reportsLayer.addTo(map); } else map.removeLayer(reportsLayer); });
    
    document.getElementById('btnRefresh').addEventListener('click', () => { loadAllData(); });
    document.getElementById('btnCenter').addEventListener('click', () => map.setView([39.8283, -98.5795], 4));
    document.getElementById('btnZoomIn').addEventListener('click', () => map.zoomIn());
    document.getElementById('btnZoomOut').addEventListener('click', () => map.zoomOut());
    document.getElementById('btnFullscreen').addEventListener('click', () => {
        if (!document.fullscreenElement) document.documentElement.requestFullscreen();
        else document.exitFullscreen();
    });
    
    document.getElementById('themeDay').addEventListener('click', () => setTheme('day'));
    document.getElementById('themeNight').addEventListener('click', () => setTheme('night'));
    document.getElementById('themeEmergency').addEventListener('click', () => setTheme('emergency'));
    
    document.getElementById('btnReport').addEventListener('click', submitReport);
    document.getElementById('btnRoute').addEventListener('click', findRoute);
    document.getElementById('fileInput').addEventListener('change', uploadFile);
    
    document.getElementById('modal').addEventListener('click', e => { if (e.target.id === 'modal') closeModal(); });
}

function setTheme(theme) {
    document.body.className = `theme-${theme} mode-normal`;
    document.querySelectorAll('.theme-switcher button').forEach(b => b.classList.remove('active'));
    document.getElementById(`theme${theme.charAt(0).toUpperCase() + theme.slice(1)}`).classList.add('active');
    if (theme === 'emergency') showAlert('⚠️ Emergency mode activated - showing evacuation routes and emergency services');
}

function showAlert(msg) {
    document.getElementById('alertMessage').textContent = msg;
    document.getElementById('alertBanner').classList.remove('hidden');
}

function dismissAlert() { document.getElementById('alertBanner').classList.add('hidden'); }

async function submitReport() {
    if (!reportLocation) { alert('Click on map to set report location'); return; }
    const type = document.getElementById('reportType').value;
    const desc = document.getElementById('reportDesc').value;
    try {
        await fetch('/api/reports', { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, description: desc, lat: reportLocation.lat, lon: reportLocation.lng }) });
        alert('Report submitted successfully!');
        document.getElementById('reportDesc').value = '';
        reportLocation = null;
        if (document.getElementById('toggleReports').checked) loadReports();
    } catch (e) { alert('Failed to submit report'); }
}

async function findRoute() {
    const from = document.getElementById('routeFrom').value;
    const to = document.getElementById('routeTo').value;
    if (!from || !to) { alert('Enter origin and destination'); return; }
    try {
        const res = await fetch('/api/route', { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ from, to }) });
        const data = await res.json();
        const results = document.getElementById('routeResults');
        results.innerHTML = data.routes.map(r => `<div class="route-option">
            <div class="name">${r.name}</div>
            <div class="details">${r.time} min • ${r.dist} mi • ${r.traffic} traffic${r.carbon_saved ? ' • 🌱' + r.carbon_saved : ''}</div>
        </div>`).join('');
        results.classList.remove('hidden');
    } catch (e) { alert('Route finding failed'); }
}

async function uploadFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    const status = document.getElementById('uploadStatus');
    status.textContent = 'Uploading...';
    status.className = '';
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch('/api/upload', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.success) {
            status.textContent = `✅ Detected ${data.detections} vehicles`;
            status.className = 'success';
        } else {
            status.textContent = '❌ ' + data.error;
            status.className = 'error';
        }
    } catch (err) {
        status.textContent = '❌ Upload failed';
        status.className = 'error';
    }
    e.target.value = '';
}

function startTimers() {
    updateTime();
    setInterval(updateTime, 1000);
    setInterval(loadAllData, 30000);
}

function updateTime() {
    const now = new Date();
    document.getElementById('currentTime').textContent = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('currentDate').textContent = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Mobile Menu Functions
function openSidebar() {
    document.getElementById('leftSidebar').classList.add('active');
}

function closeSidebar() {
    document.getElementById('leftSidebar').classList.remove('active');
}

// Mobile menu button handler
document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('mobileMenuBtn');
    if (menuBtn) {
        menuBtn.addEventListener('click', openSidebar);
    }
    
    // Close sidebar when clicking outside
    document.addEventListener('click', (e) => {
        const sidebar = document.getElementById('leftSidebar');
        const menuBtn = document.getElementById('mobileMenuBtn');
        if (sidebar && sidebar.classList.contains('active') && 
            !sidebar.contains(e.target) && !menuBtn.contains(e.target)) {
            closeSidebar();
        }
    });
});

window.showCameraDetail = showCameraDetail;
window.closeSidebar = closeSidebar;

