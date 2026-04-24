import React, { useState } from 'react';
import axios from 'axios';
import Map from './components/Map';
import HazardPanel from './components/HazardPanel';
import RouteSelector from './components/RouteSelector';
import Navigation from './components/Navigation';
import VesselStatus from './components/VesselStatus';
import LocationValidator from './components/LocationValidator';
import './App.css';

const API_URL = 'http://localhost:5000';

function App() {
  const [vesselPosition, setVesselPosition] = useState({
    lat: 12.5,
    lon: 79.9
  });
  
  const [locationValidation, setLocationValidation] = useState(null);
  const [vesselStatus, setVesselStatus] = useState(null);
  const [environmentalData, setEnvironmentalData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [risks, setRisks] = useState(null);
  const [escapeRoutes, setEscapeRoutes] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const validateAndPredict = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('🔍 Validating location and running prediction...');
      
      const response = await axios.post(`${API_URL}/api/predict`, {
        lat: vesselPosition.lat,
        lon: vesselPosition.lon,
        duration_hours: 48,
        vessel_id: 'demo_vessel_001'
      });
      
      console.log('✅ API Response:', response.data);
      
      // Update all state
      setLocationValidation(response.data.location_validation);
      setVesselStatus(response.data.vessel_status);
      setEnvironmentalData(response.data.environmental_data);
      setPrediction(response.data.prediction);
      setRisks(response.data.risks);
      setEscapeRoutes(response.data.escape_routes);
      
    } catch (err) {
      console.error('❌ Error:', err);
      
      if (err.response && err.response.data.error_type === 'invalid_location') {
        setLocationValidation(err.response.data.validation);
        setError(null);
      } else {
        setError(
          err.response?.data?.message || 
          'Failed to connect to backend. Make sure Flask server is running on http://localhost:5000'
        );
      }
    }
    
    setLoading(false);
  };
  
  const updatePosition = (lat, lon) => {
    setVesselPosition({ lat, lon });
    // Reset state when position changes
    setLocationValidation(null);
    setPrediction(null);
    setRisks(null);
    setEscapeRoutes(null);
    setSelectedRoute(null);
    setIsNavigating(false);
  };
  
  const selectRoute = (route) => {
    setSelectedRoute(route);
    setIsNavigating(true);
  };
  
  const stopNavigation = () => {
    setIsNavigating(false);
    setSelectedRoute(null);
  };
  
  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🌊 AEGISNET 2.0</h1>
          <p>Autonomous Ocean Decision Intelligence System</p>
        </div>
        <div className="header-stats">
          {vesselStatus && vesselStatus.confidence !== 'none' && (
            <div className="stat-badge">
              <span className="stat-label">Learning:</span>
              <span className="stat-value">{vesselStatus.confidence}</span>
            </div>
          )}
          {risks && (
            <div className={`stat-badge risk-${getRiskLevel(risks.total_risk_score)}`}>
              <span className="stat-label">Risk:</span>
              <span className="stat-value">{risks.total_risk_score}/100</span>
            </div>
          )}
        </div>
      </header>
      
      <div className="main-container">
        <div className="map-section">
          <Map 
            vesselPosition={vesselPosition}
            prediction={prediction}
            selectedRoute={selectedRoute}
            locationValidation={locationValidation}
            onPositionUpdate={updatePosition}
          />
          
          {/* Location validation display */}
          {locationValidation && !locationValidation.valid && (
            <LocationValidator validation={locationValidation} />
          )}
          
          {/* Controls */}
          <div className="controls">
            <button 
              onClick={validateAndPredict}
              disabled={loading}
              className="predict-button"
            >
              {loading ? (
                <>🔄 Processing...</>
              ) : (
                <>🎯 Run Drift Prediction</>
              )}
            </button>
            
            {isNavigating && (
              <button 
                onClick={stopNavigation}
                className="stop-button"
              >
                ⏹️ Stop Navigation
              </button>
            )}
          </div>
          
          {/* Error display */}
          {error && (
            <div className="error-box">
              <strong>❌ Error:</strong> {error}
            </div>
          )}
          
          {/* Environmental data display */}
          {environmentalData && locationValidation?.valid && (
            <div className="env-data">
              <h3>🌊 Environmental Conditions</h3>
              <div className="env-grid">
                <div className="env-item">
                  <span className="env-icon">💨</span>
                  <div>
                    <div className="env-label">Wind</div>
                    <div className="env-value">
                      {environmentalData.wind.speed_kmh.toFixed(1)} km/h @ {environmentalData.wind.direction.toFixed(0)}°
                    </div>
                  </div>
                </div>
                <div className="env-item">
                  <span className="env-icon">🌊</span>
                  <div>
                    <div className="env-label">Ocean Current</div>
                    <div className="env-value">
                      {environmentalData.ocean_currents.magnitude.toFixed(2)} m/s @ {environmentalData.ocean_currents.direction.toFixed(0)}°
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        <div className="sidebar">
          {/* Vessel status */}
          {vesselStatus && vesselStatus.total_points > 0 && (
            <VesselStatus status={vesselStatus} />
          )}
          
          {/* Hazard panel */}
          {risks && locationValidation?.valid && (
            <HazardPanel risks={risks} />
          )}
          
          {/* Route selector */}
          {!isNavigating && escapeRoutes && risks && risks.total_risk_score > 50 && (
            <RouteSelector 
              routes={escapeRoutes}
              onSelectRoute={selectRoute}
            />
          )}
          
          {/* Navigation */}
          {isNavigating && selectedRoute && (
            <Navigation 
              route={selectedRoute}
              currentPosition={vesselPosition}
              onStop={stopNavigation}
            />
          )}
        </div>
      </div>
    </div>
  );
}

function getRiskLevel(score) {
  if (score > 70) return 'high';
  if (score > 40) return 'medium';
  return 'low';
}

export default App;