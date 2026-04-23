// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import Map from './components/Map';
import DriftCone from './components/DriftCone';
import HazardPanel from './components/HazardPanel';
import RouteSelector from './components/RouteSelector';
import Navigation from './components/Navigation';
import axios from 'axios';
import './App.css';

function App() {
  const [vesselPosition, setVesselPosition] = useState({
    lat: 12.5,
    lon: 79.9
  });
  
  const [prediction, setPrediction] = useState(null);
  const [hazards, setHazards] = useState(null);
  const [escapeRoutes, setEscapeRoutes] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [isNavigating, setIsNavigating] = useState(false);
  
  const [loading, setLoading] = useState(false);
  
  // Run prediction
  const runPrediction = async () => {
    setLoading(true);
    
    try {
      const response = await axios.post('http://localhost:5000/api/predict', {
        lat: vesselPosition.lat,
        lon: vesselPosition.lon,
        vessel_type: 'fishing_boat',
        vessel_specs: {
          max_speed: 15,
          fuel_per_km: 0.5
        }
      });
      
      setPrediction(response.data.prediction);
      setHazards(response.data.hazards);
      setEscapeRoutes(response.data.escape_routes);
    } catch (error) {
      console.error('Prediction error:', error);
    }
    
    setLoading(false);
  };
  
  // Update vessel position (simulated GPS)
  const updatePosition = (lat, lon) => {
    setVesselPosition({ lat, lon });
  };
  
  // Start navigation with selected route
  const startNavigation = (route) => {
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
            {loading ? 'Predicting...' : 'Run Drift Prediction'}
          </button>
        </div>
        
        <div className="sidebar">
          {hazards && (
            <HazardPanel hazards={hazards} />
          )}
          
          {escapeRoutes && !isNavigating && (
            <RouteSelector 
              routes={escapeRoutes}
              onSelectRoute={startNavigation}
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
