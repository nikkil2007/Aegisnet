// ============================================================================
// AEGISNET 2.0 - FIXED VERSION
// All errors resolved
// ============================================================================

const API_URL = 'http://localhost:5000';
const VESSEL_ID = 'demo_vessel_001';

let currentPosition = {
    lat: 10.5,
    lon: 79.85
};

let state = {
    map: null,
    boatMarker: null,
    trajectoryLayer: null,
    boundaryLayers: [],
    routeLayers: [],
    safetyMarker: null,
    positionLocked: false,
    locationValid: false,
    predictionData: null,
    riskData: null,
    vesselStatus: null,
    escapeRoutes: null,
    selectedRoute: null,
    isNavigating: false,
    currentHeading: 0
};

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🌊 AEGISNET 2.0 Loading...');
    
    // Landing screen
    const enterBtn = document.getElementById('enter-btn');
    if (enterBtn) {
        enterBtn.addEventListener('click', function() {
            console.log('🚀 Initiating system...');
            
            const landingScreen = document.getElementById('landing-screen');
            if (landingScreen) {
                landingScreen.style.display = 'none';
            }
            
            setTimeout(() => {
                initializeMap();
                updatePositionDisplay();
                
                document.getElementById('vessel-lat').value = currentPosition.lat.toFixed(6);
                document.getElementById('vessel-lon').value = currentPosition.lon.toFixed(6);
                
                console.log('✅ System initialized');
            }, 100);
        });
    }
    
    // Run prediction button
    const runBtn = document.getElementById('run-btn');
    if (runBtn) {
        runBtn.addEventListener('click', function() {
            const lat = parseFloat(document.getElementById('vessel-lat').value);
            const lon = parseFloat(document.getElementById('vessel-lon').value);
            
            if (isNaN(lat) || isNaN(lon)) {
                showAlert('❌ INVALID COORDINATES', 'error');
                return;
            }
            
            if (!state.positionLocked) {
                currentPosition.lat = lat;
                currentPosition.lon = lon;
                updateBoatPosition(lat, lon, 0);
                updatePositionDisplay();
            }
            
            runPrediction();
        });
    }
    
    // Scenario button
    const scenarioBtn = document.getElementById('scenario-btn');
    if (scenarioBtn) {
        scenarioBtn.addEventListener('click', openModal);
    }
    
    // Reset button
    const resetBtn = document.getElementById('reset-btn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetSystem);
    }
    
    // Stop navigation button
    const stopNavBtn = document.getElementById('stop-nav-btn');
    if (stopNavBtn) {
        stopNavBtn.addEventListener('click', stopNavigation);
    }
});

// ============================================================================
// MAP INITIALIZATION
// ============================================================================

function initializeMap() {
    console.log('🗺️ Initializing map...');
    
    const indianWatersBounds = [
        [6.0, 68.0],
        [24.0, 98.0]
    ];
    
    state.map = L.map('map', {
        center: [currentPosition.lat, currentPosition.lon],
        zoom: 8,
        minZoom: 6,
        maxZoom: 14,
        maxBounds: indianWatersBounds,
        maxBoundsViscosity: 1.0
    });
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(state.map);
    
    drawMaritimeBoundaries();
    addBoatMarker(currentPosition.lat, currentPosition.lon, 0);
    
    state.map.on('click', function(e) {
        if (!state.positionLocked && !state.isNavigating) {
            currentPosition.lat = e.latlng.lat;
            currentPosition.lon = e.latlng.lng;
            updateBoatPosition(e.latlng.lat, e.latlng.lng, state.currentHeading);
            updatePositionDisplay();
            
            document.getElementById('vessel-lat').value = e.latlng.lat.toFixed(6);
            document.getElementById('vessel-lon').value = e.latlng.lng.toFixed(6);
        }
    });
    
    console.log('✅ Map initialized');
}

function drawMaritimeBoundaries() {
    state.boundaryLayers.forEach(layer => state.map.removeLayer(layer));
    state.boundaryLayers = [];
    
    const imblCoordinates = [
        [9.15, 79.35],
        [9.20, 79.50],
        [9.30, 79.65],
        [9.45, 79.75],
        [9.65, 79.80],
        [9.85, 79.83],
        [10.10, 79.85],
        [10.35, 79.87],
        [10.60, 79.88]
    ];
    
    const boundaryLine = L.polyline(imblCoordinates, {
        color: '#ef4444',
        weight: 4,
        opacity: 0.9,
        dashArray: '15,10'
    }).addTo(state.map);
    
    const warningZone = imblCoordinates.map(coord => [coord[0], coord[1] - 0.05]);
    
    const warningLine = L.polyline(warningZone, {
        color: '#fbbf24',
        weight: 2,
        opacity: 0.6,
        dashArray: '5,5'
    }).addTo(state.map);
    
    const labelMarker = L.marker([9.5, 79.7], {
        icon: L.divIcon({
            className: 'boundary-label',
            html: '<div style="background: rgba(239, 68, 68, 0.9); color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; font-size: 11px; white-space: nowrap;">🚨 INDIA-SRI LANKA MARITIME BOUNDARY</div>',
            iconSize: [200, 30],
            iconAnchor: [100, 15]
        })
    }).addTo(state.map);
    
    state.boundaryLayers.push(boundaryLine, warningLine, labelMarker);
}

// ============================================================================
// BOAT MARKER
// ============================================================================

function getBoatIcon(heading = 0) {
    const svgIcon = `
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" 
             style="width: 52px; height: 52px; display: block; 
                    filter: drop-shadow(0px 4px 8px rgba(0,0,0,0.8)); 
                    transform: rotate(${heading}deg); 
                    transition: transform 0.8s ease-out;">
            <path d="M50 10 L70 75 L50 65 L30 75 Z" 
                  fill="#38bdf8" 
                  stroke="#0ea5e9" 
                  stroke-width="3" 
                  stroke-linejoin="round"/>
            <circle cx="50" cy="15" r="6" fill="#fbbf24" stroke="#f59e0b" stroke-width="2"/>
            <text x="50" y="95" 
                  font-family="Arial" 
                  font-size="12" 
                  fill="#fff" 
                  text-anchor="middle" 
                  stroke="#000" 
                  stroke-width="1">
                ${heading.toFixed(0)}°
            </text>
        </svg>
    `;
    
    return L.divIcon({
        className: 'boat-marker-container',
        html: svgIcon,
        iconSize: [52, 52],
        iconAnchor: [26, 26]
    });
}

function addBoatMarker(lat, lon, heading = 0) {
    if (state.boatMarker) {
        state.map.removeLayer(state.boatMarker);
    }
    
    state.currentHeading = heading;
    
    state.boatMarker = L.marker([lat, lon], {
        icon: getBoatIcon(heading),
        draggable: false,
        zIndexOffset: 1000
    }).addTo(state.map);
}

function updateBoatPosition(lat, lon, heading = 0) {
    state.currentHeading = heading;
    
    if (state.boatMarker) {
        state.boatMarker.setLatLng([lat, lon]);
        state.boatMarker.setIcon(getBoatIcon(heading));
    } else {
        addBoatMarker(lat, lon, heading);
    }
}

// ============================================================================
// API CALLS
// ============================================================================

async function runPrediction() {
    state.positionLocked = true;
    
    showAlert('🔄 RUNNING ANALYSIS...', 'info', 2000);
    
    try {
        console.log('Making API call to:', `${API_URL}/api/predict`);
        
        const response = await fetch(`${API_URL}/api/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lat: currentPosition.lat,
                lon: currentPosition.lon,
                duration_hours: 48,
                vessel_id: VESSEL_ID
            })
        });
        
        const data = await response.json();
        console.log('API Response:', data);
        
        if (data.status === 'error') {
            if (data.error_type === 'invalid_location') {
                handleInvalidLocation(data.validation);
                state.positionLocked = false;
                return;
            }
            throw new Error(data.message || 'Prediction failed');
        }
        
        // Success - update all state
        state.locationValid = true;
        state.predictionData = data.prediction;
        state.riskData = data.risks;
        state.vesselStatus = data.vessel_status;
        state.escapeRoutes = data.escape_routes;
        
        // Update UI
        updateLocationStatus(data.location_validation);
        updateVesselStatus(data.vessel_status);
        updateRiskAssessment(data.risks);
        displayTrajectory(data.prediction.trajectory);
        displayHazards(data.risks);
        
        if (data.risks.total_risk_score > 50 && data.escape_routes) {
            displayEscapeRoutes(data.escape_routes);
        } else {
            hideElement('route-section');
        }
        
        showAlert('✅ ANALYSIS COMPLETE', 'success', 3000);
        
    } catch (error) {
        console.error('Prediction error:', error);
        showAlert(`❌ ERROR: ${error.message}`, 'error');
        state.positionLocked = false;
    }
}

// ============================================================================
// UI UPDATES (FIXED - ALL SAFE CHECKS)
// ============================================================================

function updatePositionDisplay() {
    const positionBadge = document.getElementById('position-badge');
    if (positionBadge) {
        positionBadge.textContent = `${currentPosition.lat.toFixed(4)}°N, ${currentPosition.lon.toFixed(4)}°E`;
    }
}

function handleInvalidLocation(validation) {
    state.locationValid = false;
    
    // Safe update with null checks
    safeSetText('location-status', 'INVALID');
    safeSetClass('location-status', 'indicator-value', 'zone-invalid');
    safeSetText('zone-name', validation.reason || 'INVALID');
    
    let alertMsg = `⚠️ LOCATION INVALID\n\n${validation.message}`;
    if (validation.suggestion) {
        alertMsg += `\n\n💡 ${validation.suggestion}`;
    }
    
    showAlert(alertMsg, 'error', 8000);
    
    clearTrajectory();
    hideElement('hazard-group');
    hideElement('route-section');
}

function updateLocationStatus(validation) {
    if (!validation) return;
    
    if (validation.valid) {
        safeSetText('location-status', validation.region.toUpperCase());
        safeSetClass('location-status', 'indicator-value');
        
        safeSetText('zone-name', validation.region);
        safeSetText('coast-dist', `${validation.distance_from_coast.toFixed(1)} km`);
        
        if (validation.warning && validation.warning.length > 0) {
            showAlert(`⚠️ ${validation.warning[0]}`, 'warning', 5000);
        }
    }
}

function updateVesselStatus(status) {
    if (!status) return;
    
    if (status.engine_currently_on) {
        safeSetText('engine-state', 'ACTIVE');
        safeSetClass('engine-state', 'info-value', 'engine-on');
    } else {
        safeSetText('engine-state', 'OFF (DRIFTING)');
        safeSetClass('engine-state', 'info-value', 'engine-off');
    }
    
    if (status.learned_engine_speed) {
        safeSetText('vessel-speed', `${status.learned_engine_speed.toFixed(1)} km/h`);
    } else {
        safeSetText('vessel-speed', 'LEARNING...');
    }
}

function updateRiskAssessment(risks) {
    if (!risks) return;
    
    const score = risks.total_risk_score;
    const riskDisplay = document.getElementById('risk-display');
    
    if (riskDisplay) {
        riskDisplay.textContent = score;
        riskDisplay.className = 'indicator-value';
        
        if (score > 70) {
            riskDisplay.classList.add('risk-critical');
        } else if (score > 40) {
            riskDisplay.classList.add('risk-high');
        } else if (score > 20) {
            riskDisplay.classList.add('risk-medium');
        } else {
            riskDisplay.classList.add('risk-low');
        }
    }
}

function displayHazards(risks) {
    if (!risks) return;
    
    const hazardList = document.getElementById('hazard-list');
    const hazardGroup = document.getElementById('hazard-group');
    
    if (!hazardList || !hazardGroup) return;
    
    hazardList.innerHTML = '';
    
    const hazardTypes = [
        { key: 'boundary_crossing', icon: '🚨', name: 'BORDER CROSSING' },
        { key: 'cyclone', icon: '🌀', name: 'CYCLONE RISK' },
        { key: 'high_tide', icon: '🌊', name: 'HIGH TIDE' },
        { key: 'strong_currents', icon: '💧', name: 'STRONG CURRENTS' },
        { key: 'restricted_zone', icon: '⛔', name: 'RESTRICTED ZONE' },
        { key: 'shallow_water', icon: '⚓', name: 'SHALLOW WATER' }
    ];
    
    let hasHazards = false;
    
    hazardTypes.forEach(hazard => {
        const data = risks[hazard.key];
        
        if (data && data.detected) {
            hasHazards = true;
            
            let details = '';
            if (data.first_crossing_time) {
                details = `ETA: ${data.first_crossing_time.toFixed(1)} HR`;
            } else if (data.entry_time) {
                details = `Entry: ${data.entry_time.toFixed(1)} HR`;
            } else if (data.severity) {
                details = `Severity: ${data.severity}`;
            }
            
            const item = document.createElement('div');
            item.className = 'hazard-item';
            item.innerHTML = `
                <div class="hazard-name">${hazard.icon} ${hazard.name}</div>
                <div class="hazard-detail">${details}</div>
            `;
            
            hazardList.appendChild(item);
        }
    });
    
    if (hasHazards) {
        hazardGroup.style.display = 'block';
    } else {
        hazardGroup.style.display = 'none';
    }
}

function displayEscapeRoutes(routes) {
    if (!routes) return;
    
    const routeCards = document.getElementById('route-cards');
    const routeSection = document.getElementById('route-section');
    
    if (!routeCards || !routeSection) return;
    
    routeCards.innerHTML = '';
    
    const routeConfigs = [
        { key: 'fastest', class: 'fastest', icon: '⚡', label: 'FASTEST' },
        { key: 'safest', class: 'safest', icon: '🛡️', label: 'SAFEST' },
        { key: 'efficient', class: 'efficient', icon: '⛽', label: 'EFFICIENT' }
    ];
    
    routeConfigs.forEach(config => {
        const route = routes[config.key];
        
        if (!route || route.type === 'EMERGENCY') return;
        
        const card = document.createElement('div');
        card.className = `route-card ${config.class}`;
        card.onclick = () => selectRoute(config.key);
        
        card.innerHTML = `
            <div class="route-title">${config.icon} ${config.label}</div>
            <div class="route-info">
                Heading: ${route.heading_degrees}° (${route.heading_cardinal})<br>
                Duration: ${route.duration_hours.toFixed(1)} HR<br>
                Fuel: ${route.fuel_required_liters.toFixed(1)} L<br>
                Safety: ${route.safety_margin_km.toFixed(1)} km
            </div>
        `;
        
        routeCards.appendChild(card);
    });
    
    routeSection.classList.remove('hidden');
}

// ============================================================================
// TRAJECTORY DISPLAY
// ============================================================================

function displayTrajectory(trajectory) {
    clearTrajectory();
    
    if (!trajectory || trajectory.length === 0) return;
    
    const coords = trajectory.map(p => [p.lat, p.lon]);
    
    // Calculate heading
    if (coords.length >= 2) {
        const heading = calculateBearing(
            coords[0][0], coords[0][1],
            coords[1][0], coords[1][1]
        );
        updateBoatPosition(currentPosition.lat, currentPosition.lon, heading);
    }
    
    // Draw trajectory
    state.trajectoryLayer = L.polyline(coords, {
        color: '#fbbf24',
        weight: 4,
        opacity: 0.8,
        dashArray: '10,5'
    }).addTo(state.map);
    
    // Time markers
    const keyPoints = [
        { idx: 0, label: 'NOW', color: '#10b981' },
        { idx: Math.floor(trajectory.length * 0.25), label: '12H', color: '#fbbf24' },
        { idx: Math.floor(trajectory.length * 0.5), label: '24H', color: '#f97316' },
        { idx: Math.floor(trajectory.length * 0.75), label: '36H', color: '#ef4444' },
        { idx: trajectory.length - 1, label: '48H', color: '#dc2626' }
    ];
    
    keyPoints.forEach(point => {
        if (point.idx < trajectory.length) {
            const pos = trajectory[point.idx];
            L.circleMarker([pos.lat, pos.lon], {
                radius: 7,
                fillColor: point.color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 1
            }).bindTooltip(point.label, { permanent: point.idx === 0 || point.idx === trajectory.length - 1 })
              .addTo(state.map);
        }
    });
    
    // Fit bounds
    state.map.fitBounds(state.trajectoryLayer.getBounds(), { 
        padding: [80, 80],
        maxZoom: 11
    });
}

function calculateBearing(lat1, lon1, lat2, lon2) {
    const toRad = deg => deg * Math.PI / 180;
    const toDeg = rad => rad * 180 / Math.PI;
    
    const dLon = toRad(lon2 - lon1);
    const y = Math.sin(dLon) * Math.cos(toRad(lat2));
    const x = Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
              Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLon);
    
    let bearing = toDeg(Math.atan2(y, x));
    return (bearing + 360) % 360;
}

function clearTrajectory() {
    if (state.trajectoryLayer) {
        state.map.removeLayer(state.trajectoryLayer);
        state.trajectoryLayer = null;
    }
}

// ============================================================================
// ROUTE SELECTION & NAVIGATION
// ============================================================================

function selectRoute(routeKey) {
    const route = state.escapeRoutes[routeKey];
    if (!route) return;
    
    state.selectedRoute = route;
    state.isNavigating = true;
    
    // Hide routes, show navigation
    hideElement('route-section');
    showElement('nav-section');
    
    // Update compass
    safeSetText('compass-reading', `${route.heading_degrees}°`);
    safeSetText('compass-direction', route.heading_cardinal);
    
    // Update instructions
    const navInstructions = document.getElementById('nav-instructions');
    if (navInstructions && route.instructions) {
        navInstructions.innerHTML = route.instructions
            .map(inst => `• ${inst}`)
            .join('<br>');
    }
    
    // Draw route on map
    drawRoute(route);
    
    showAlert(`🧭 NAVIGATION ACTIVE - ${route.type}`, 'success');
}

function drawRoute(route) {
    // Clear previous
    state.routeLayers.forEach(layer => state.map.removeLayer(layer));
    state.routeLayers = [];
    
    if (route.trajectory && route.trajectory.length > 0) {
        const coords = route.trajectory.map(p => [p.lat, p.lon]);
        
        const routeLine = L.polyline(coords, {
            color: '#10b981',
            weight: 5,
            opacity: 0.9
        }).addTo(state.map);
        
        state.routeLayers.push(routeLine);
        
        // Safety zone marker
        const dest = route.trajectory[route.trajectory.length - 1];
        
        const safetyMarker = L.marker([dest.lat, dest.lon], {
            icon: L.divIcon({
                className: 'safety-marker',
                html: '<div style="background: #10b981; color: white; padding: 8px 12px; border-radius: 20px; font-weight: bold; font-size: 12px; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.5); border: 2px solid white;">✓ SAFETY ZONE</div>',
                iconSize: [120, 30],
                iconAnchor: [60, 15]
            })
        }).addTo(state.map);
        
        state.routeLayers.push(safetyMarker);
        
        updateBoatPosition(currentPosition.lat, currentPosition.lon, route.heading_degrees);
    }
}

function stopNavigation() {
    state.isNavigating = false;
    state.selectedRoute = null;
    
    hideElement('nav-section');
    
    // Clear route layers
    state.routeLayers.forEach(layer => state.map.removeLayer(layer));
    state.routeLayers = [];
    
    updateBoatPosition(currentPosition.lat, currentPosition.lon, 0);
    
    // Show routes again if available
    if (state.escapeRoutes) {
        displayEscapeRoutes(state.escapeRoutes);
    }
    
    showAlert('⏹️ NAVIGATION STOPPED', 'info');
}

// ============================================================================
// RESET SYSTEM
// ============================================================================

function resetSystem() {
    state.positionLocked = false;
    
    clearTrajectory();
    state.routeLayers.forEach(layer => state.map.removeLayer(layer));
    state.routeLayers = [];
    
    state.predictionData = null;
    state.riskData = null;
    state.vesselStatus = null;
    state.escapeRoutes = null;
    state.selectedRoute = null;
    state.isNavigating = false;
    
    hideElement('hazard-group');
    hideElement('route-section');
    hideElement('nav-section');
    
    safeSetText('location-status', 'STANDBY');
    safeSetText('risk-display', '--');
    safeSetText('zone-name', '--');
    safeSetText('coast-dist', '-- km');
    safeSetText('engine-state', '--');
    safeSetText('vessel-speed', '--');
    
    updateBoatPosition(currentPosition.lat, currentPosition.lon, 0);
    state.map.setView([currentPosition.lat, currentPosition.lon], 8);
    
    showAlert('🔄 SYSTEM RESET', 'success', 3000);
}

// ============================================================================
// DEMO SCENARIOS
// ============================================================================

function loadScenario(scenarioNumber) {
    const scenarios = {
        1: { lat: 10.50, lon: 79.85, name: 'SAFE FISHING' },
        2: { lat: 9.75, lon: 79.70, name: 'BORDER WARNING' },
        3: { lat: 13.25, lon: 80.45, name: 'CYCLONE DANGER' },
        4: { lat: 11.80, lon: 79.95, name: 'STRONG CURRENTS' },
        5: { lat: 9.35, lon: 79.55, name: 'MULTIPLE HAZARDS' },
        6: { lat: 10.05, lon: 79.82, name: 'EMERGENCY' }
    };
    
    const scenario = scenarios[scenarioNumber];
    if (!scenario) return;
    
    closeModal();
    resetSystem();
    
    setTimeout(() => {
        currentPosition.lat = scenario.lat;
        currentPosition.lon = scenario.lon;
        
        document.getElementById('vessel-lat').value = scenario.lat.toFixed(6);
        document.getElementById('vessel-lon').value = scenario.lon.toFixed(6);
        
        updateBoatPosition(scenario.lat, scenario.lon, 0);
        updatePositionDisplay();
        
        state.map.setView([scenario.lat, scenario.lon], 10);
        
        showAlert(`🎬 SCENARIO ${scenarioNumber}: ${scenario.name}`, 'info', 2000);
        
        setTimeout(() => {
            runPrediction();
        }, 1000);
    }, 500);
}

// ============================================================================
// UI UTILITIES (SAFE HELPERS)
// ============================================================================

function safeSetText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

function safeSetClass(elementId, ...classNames) {
    const element = document.getElementById(elementId);
    if (element) {
        element.className = classNames.join(' ');
    }
}

function showElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.remove('hidden');
    }
}

function hideElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add('hidden');
    }
}

function togglePanel(panelId) {
    const panel = document.getElementById(panelId);
    if (panel) {
        panel.classList.toggle('collapsed');
    }
}

function openModal() {
    showElement('scenario-modal');
}

function closeModal() {
    hideElement('scenario-modal');
}

function showAlert(message, type = 'info', duration = 5000) {
    const alertToast = document.getElementById('alert-toast');
    if (!alertToast) return;
    
    alertToast.textContent = message;
    alertToast.className = 'alert-toast';
    
    if (type === 'error') {
        alertToast.style.background = 'rgba(220, 38, 38, 0.95)';
        alertToast.style.color = 'white';
    } else if (type === 'success') {
        alertToast.style.background = 'rgba(16, 185, 129, 0.95)';
        alertToast.style.color = 'white';
    } else if (type === 'warning') {
        alertToast.style.background = 'rgba(245, 158, 11, 0.95)';
        alertToast.style.color = 'white';
    } else {
        alertToast.style.background = 'rgba(14, 165, 233, 0.95)';
        alertToast.style.color = 'white';
    }
    
    alertToast.classList.remove('hidden');
    
    setTimeout(() => {
        alertToast.classList.add('hidden');
    }, duration);
}

// ============================================================================
// GLOBAL EXPORTS
// ============================================================================

window.togglePanel = togglePanel;
window.openModal = openModal;
window.closeModal = closeModal;
window.loadScenario = loadScenario;
window.selectRoute = selectRoute;

console.log('%c🌊 AEGISNET 2.0 ', 'background: #0ea5e9; color: white; font-size: 20px; font-weight: bold; padding: 10px;');
console.log('%cReady to initialize', 'color: #38bdf8; font-size: 14px;');