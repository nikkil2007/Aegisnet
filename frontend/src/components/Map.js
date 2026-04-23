import React from 'react';

function Map({ vesselPosition, prediction, selectedRoute, onPositionUpdate }) {
  const mapStyle = {
    width: '100%',
    height: '600px',
    background: 'linear-gradient(180deg, #e0f2fe 0%, #bae6fd 100%)',
    border: '3px solid #0ea5e9',
    borderRadius: '10px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    position: 'relative',
    overflow: 'hidden'
  };
  
  const boatStyle = {
    fontSize: '48px',
    marginBottom: '20px'
  };
  
  const infoStyle = {
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '20px',
    borderRadius: '10px',
    boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
    maxWidth: '500px',
    width: '100%'
  };
  
  const positionStyle = {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#0c4a6e',
    marginBottom: '15px',
    textAlign: 'center'
  };
  
  const detailStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '10px',
    fontSize: '14px'
  };
  
  const labelStyle = {
    color: '#64748b'
  };
  
  const valueStyle = {
    fontWeight: '600',
    color: '#0f172a',
    textAlign: 'right'
  };
  
  return (
    <div style={mapStyle}>
      <div style={boatStyle}>🚤</div>
      
      <div style={infoStyle}>
        <div style={positionStyle}>
          📍 Current Position
        </div>
        
        <div style={detailStyle}>
          <span style={labelStyle}>Latitude:</span>
          <span style={valueStyle}>{vesselPosition.lat.toFixed(4)}°N</span>
          
          <span style={labelStyle}>Longitude:</span>
          <span style={valueStyle}>{vesselPosition.lon.toFixed(4)}°E</span>
        </div>
        
        {prediction && (
          <>
            <div style={{height: '1px', background: '#e2e8f0', margin: '15px 0'}}></div>
            
            <div style={{marginBottom: '10px', color: '#0c4a6e', fontWeight: '600'}}>
              ⚠️ Drift Prediction Active
            </div>
            
            <div style={detailStyle}>
              <span style={labelStyle}>Total Points:</span>
              <span style={valueStyle}>{prediction.total_points}</span>
              
              <span style={labelStyle}>Duration:</span>
              <span style={valueStyle}>48 hours</span>
            </div>
          </>
        )}
        
        {selectedRoute && (
          <>
            <div style={{height: '1px', background: '#e2e8f0', margin: '15px 0'}}></div>
            
            <div style={{marginBottom: '10px', color: '#15803d', fontWeight: '600'}}>
              ✅ Route Selected
            </div>
            
            <div style={detailStyle}>
              <span style={labelStyle}>Type:</span>
              <span style={valueStyle}>{selectedRoute.type}</span>
              
              <span style={labelStyle}>Heading:</span>
              <span style={valueStyle}>{selectedRoute.heading}°</span>
            </div>
          </>
        )}
      </div>
      
      <div style={{
        position: 'absolute',
        bottom: '20px',
        fontSize: '12px',
        color: '#64748b',
        background: 'rgba(255,255,255,0.8)',
        padding: '10px 20px',
        borderRadius: '20px'
      }}>
        📝 Interactive map with Leaflet coming soon
      </div>
    </div>
  );
}

export default Map;