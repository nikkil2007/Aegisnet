import React, { useState } from 'react';
import axios from 'axios';
import Map from './components/Map';
import HazardPanel from './components/HazardPanel';
import RouteSelector from './components/RouteSelector';
import Navigation from './components/Navigation';
import './App.css';

const API_URL = 'http://localhost:5000';

function App() {
  const [vesselPosition, setVesselPosition] = useState({
    lat: 12.5,
    lon: 79.9
  });
  
  const [prediction, setPrediction] = useState(null);
  const [risks, setRisks] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const runPrediction = async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log('Calling API...');
      
      const response = await axios.post(`${API_URL}/api/predict`, {
        lat: vesselPosition.lat,
        lon: vesselPosition.lon,
        duration_hours: 48,
        engine_on: false
      });
      
      console.log('API Response:', response.data);
      
      setPrediction(response.data.prediction);
      setRisks(response.data.risks);
      
    } catch (err) {
      console.error('Prediction error:', err);
      setError(err.response?.data?.message || 'Failed to connect to backend. Make sure the Flask server is running on http://localhost:5000');
    }
    
    setLoading(false);
  };
  
  const updatePosition = (lat, lon) => {
    setVesselPosition({ lat, lon });
  };
  
  const selectRoute = (route) => {
    setSelectedRoute(route);
    setIsNavigating(true);
  };
  
  return (
    <div className="App">
      <header className="App-header">
        <h1>🌊 AEGISNET 2.0</h1>
        <p>Ocean Decision Intelligence System</p>
      </header>
      
      <div className="main-container">
        <div className="map-section">
          <Map 
            vesselPosition={vesselPosition}
            prediction={prediction}
            selectedRoute={selectedRoute}
            onPositionUpdate={updatePosition}
          />
          
          <button 
            onClick={runPrediction}
            disabled={loading}
            className="predict-button"
          >
            {loading ? '🔄 Predicting...' : '🎯 Run Drift Prediction'}
          </button>
          
          {error && (
            <div className="error">
              <strong>❌ Error:</strong> {error}
            </div>
          )}
        </div>
        
        <div className="sidebar">
          {risks && (
            <HazardPanel risks={risks} />
          )}
          
          {!isNavigating && risks && risks.total_risk_score > 50 && (
            <RouteSelector 
              onSelectRoute={selectRoute}
            />
          )}
          
          {isNavigating && selectedRoute && (
            <Navigation 
              route={selectedRoute}
              currentPosition={vesselPosition}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;