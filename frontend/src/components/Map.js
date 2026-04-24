import React from 'react';

function Map({ vesselPosition, prediction, selectedRoute, locationValidation, onPositionUpdate }) {
  const mapStyle = {
    width: '100%',
    height: '600px',
    background: 'linear-gradient(180deg, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%)',
    border: '3px solid #0ea5e9',
    borderRadius: '15px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '30px',
    position: 'relative',
    overflow: 'hidden',
    boxShadow: '0 10px 30px rgba(0,0,0,0.15)'
  };
  
  // Add wave animation
  const waveStyle = {
    position: 'absolute',
    bottom: 0,
    left: 0,
    width: '100%',
    height: '100px',
    background: 'linear-gradient(transparent, rgba(255,255,255,0.3))',
    animation: 'wave 3s ease-in-out infinite'
  };
  
  const boatStyle = {
    fontSize: '64px',
    marginBottom: '20px',
    animation: 'float 2s ease-in-out infinite',
    filter: 'drop-shadow(0 5px 10px rgba(0,0,0,0.2))'
  };
  
  const infoBoxStyle = {
    background: 'rgba(255, 255, 255, 0.98)',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 8px 25px rgba(0,0,0,0.15)',
    maxWidth: '600px',
    width: '100%',
    zIndex: 10
  };
  
  const titleStyle = {
    fontSize: '20px',
    fontWeight: '700',
    color: '#0c4a6e',
    marginBottom: '20px',
    textAlign: 'center',
    borderBottom: '2px solid #e0f2fe',
    paddingBottom: '10px'
  };
  
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: '140px 1fr',
    gap: '12px',
    fontSize: '15px'
  };
  
  const labelStyle = {
    color: '#64748b',
    fontWeight: '500'
  };
  
  const valueStyle = {
    fontWeight: '600',
    color: '#0f172a'
  };
  
  const dividerStyle = {
    height: '1px',
    background: 'linear-gradient(to right, transparent, #e2e8f0, transparent)',
    margin: '15px 0'
  };
  
  const badgeStyle = {
    display: 'inline-block',
    padding: '6px 12px',
    borderRadius: '6px',
    fontSize: '13px',
    fontWeight: '600'
  };
  
  // Determine location status
  const getLocationBadge = () => {
    if (!locationValidation) return null;
    
    if (locationValidation.valid) {
      return (
        <span style={{...badgeStyle, background: '#dcfce7', color: '#166534'}}>
          ✓ Valid Maritime Zone
        </span>
      );
    } else {
      return (
        <span style={{...badgeStyle, background: '#fee2e2', color: '#991b1b'}}>
          ✗ {locationValidation.reason.replace(/_/g, ' ').toUpperCase()}
        </span>
      );
    }
  };
  
  return (
    <div style={mapStyle}>
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-10px); }
        }
        @keyframes wave {
          0%, 100% { transform: translateX(0); }
          50% { transform: translateX(-20px); }
        }
      `}</style>
      
      <div style={waveStyle}></div>
      
      <div style={boatStyle}>🚤</div>
      
      <div style={infoBoxStyle}>
        <div style={titleStyle}>
          📍 Vessel Position
        </div>
        
        <div style={gridStyle}>
          <span style={labelStyle}>Latitude:</span>
          <span style={valueStyle}>{vesselPosition.lat.toFixed(6)}°N</span>
          
          <span style={labelStyle}>Longitude:</span>
          <span style={valueStyle}>{vesselPosition.lon.toFixed(6)}°E</span>
        </div>
        
        {locationValidation && (
          <>
            <div style={dividerStyle}></div>
            <div style={{marginBottom: '12px'}}>
              {getLocationBadge()}
            </div>
            
            {locationValidation.valid && (
              <div style={gridStyle}>
                <span style={labelStyle}>Region:</span>
                <span style={valueStyle}>{locationValidation.region}</span>
                
                <span style={labelStyle}>From Coast:</span>
                <span style={valueStyle}>{locationValidation.distance_from_coast.toFixed(1)} km</span>
              </div>
            )}
          </>
        )}
        
        {prediction && locationValidation?.valid && (
          <>
            <div style={dividerStyle}></div>
            
            <div style={{marginBottom: '12px', color: '#0c4a6e', fontWeight: '600', fontSize: '16px'}}>
              ⚠️ Drift Prediction Active
            </div>
            
            <div style={gridStyle}>
              <span style={labelStyle}>Duration:</span>
              <span style={valueStyle}>48 hours</span>
              
              <span style={labelStyle}>Data Points:</span>
              <span style={valueStyle}>{prediction.total_points}</span>
              
              <span style={labelStyle}>Engine Status:</span>
              <span style={{
                ...badgeStyle,
                background: prediction.engine_on ? '#dcfce7' : '#fef3c7',
                color: prediction.engine_on ? '#166534' : '#92400e'
              }}>
                {prediction.engine_on ? '✓ ON' : '○ OFF (Drifting)'}
              </span>
            </div>
          </>
        )}
        
        {selectedRoute && (
          <>
            <div style={dividerStyle}></div>
            
            <div style={{marginBottom: '12px', color: '#15803d', fontWeight: '600', fontSize: '16px'}}>
              ✅ Escape Route Active
            </div>
            
            <div style={gridStyle}>
              <span style={labelStyle}>Route Type:</span>
              <span style={valueStyle}>{selectedRoute.type}</span>
              
              <span style={labelStyle}>Heading:</span>
              <span style={valueStyle}>{selectedRoute.heading_degrees}° ({selectedRoute.heading_cardinal})</span>
              
              <span style={labelStyle}>ETA:</span>
              <span style={valueStyle}>{selectedRoute.duration_hours.toFixed(1)} hours</span>
            </div>
          </>
        )}
      </div>
      
      <div style={{
        position: 'absolute',
        bottom: '15px',
        fontSize: '13px',
        color: 'rgba(255,255,255,0.9)',
        background: 'rgba(14, 165, 233, 0.8)',
        padding: '8px 20px',
        borderRadius: '20px',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
      }}>
        📝 Interactive Leaflet map integration coming in production
      </div>
    </div>
  );
}

export default Map;