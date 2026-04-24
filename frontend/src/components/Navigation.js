import React, { useState, useEffect } from 'react';

function Navigation({ route, currentPosition, onStop }) {
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  
  useEffect(() => {
    // Simulate progress
    const interval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
      setProgress(prev => Math.min(prev + 1, 100));
    }, 1000);
    
    return () => clearInterval(interval);
  }, []);
  
  if (!route) return null;
  
  const panelStyle = {
    background: 'white',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
    border: '3px solid #16a34a'
  };
  
  const headerStyle = {
    fontSize: '20px',
    fontWeight: '700',
    marginBottom: '20px',
    color: '#15803d',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  };
  
  const compassStyle = {
    width: '180px',
    height: '180px',
    margin: '0 auto 25px',
    background: 'linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%)',
    borderRadius: '50%',
    border: '5px solid #16a34a',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    boxShadow: '0 8px 25px rgba(22, 163, 74, 0.3)'
  };
  
  const needleStyle = {
    fontSize: '70px',
    lineHeight: 1,
    filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.2))'
  };
  
  const instructionBoxStyle = {
    background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
    padding: '20px',
    borderRadius: '12px',
    marginBottom: '20px',
    border: '2px solid #f59e0b',
    textAlign: 'center',
    boxShadow: '0 4px 15px rgba(245, 158, 11, 0.2)'
  };
  
  const statsStyle = {
    background: '#f0fdf4',
    padding: '20px',
    borderRadius: '12px',
    marginTop: '20px'
  };
  
  const statItemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '12px 0',
    borderBottom: '1px solid #dcfce7',
    fontSize: '15px'
  };
  
  const progressBarStyle = {
    width: '100%',
    height: '12px',
    background: '#e5e7eb',
    borderRadius: '10px',
    overflow: 'hidden',
    marginTop: '20px'
  };
  
  const progressFillStyle = {
    height: '100%',
    background: 'linear-gradient(90deg, #16a34a 0%, #22c55e 100%)',
    borderRadius: '10px',
    transition: 'width 0.5s ease',
    width: `${progress}%`
  };
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        🧭 Active Navigation
      </div>
      
      <div style={compassStyle}>
        <div style={needleStyle}>↑</div>
        <div style={{
          fontSize: '40px',
          fontWeight: '700',
          color: '#15803d',
          marginTop: '5px'
        }}>
          {route.heading_degrees}°
        </div>
        <div style={{
          fontSize: '18px',
          color: '#166534',
          fontWeight: '600'
        }}>
          {route.heading_cardinal}
        </div>
        
        <div style={{
          position: 'absolute',
          top: '8px',
          fontSize: '16px',
          color: '#64748b',
          fontWeight: '600'
        }}>
          N
        </div>
      </div>
      
      <div style={instructionBoxStyle}>
        <div style={{
          fontSize: '18px',
          fontWeight: '700',
          color: '#92400e',
          marginBottom: '10px'
        }}>
          🎯 CURRENT INSTRUCTION
        </div>
        <div style={{
          fontSize: '16px',
          color: '#78350f',
          fontWeight: '600'
        }}>
          Turn boat to heading {route.heading_degrees}° ({route.heading_cardinal})
          <br/>
          and maintain steady course
        </div>
      </div>
      
      <div style={{marginBottom: '20px'}}>
        <div style={{
          fontSize: '14px',
          color: '#64748b',
          marginBottom: '8px',
          fontWeight: '600'
        }}>
          📋 Step-by-Step Instructions:
        </div>
        <ol style={{
          margin: '0',
          paddingLeft: '20px',
          lineHeight: '1.8',
          fontSize: '14px',
          color: '#0f172a'
        }}>
          {route.instructions?.map((instruction, idx) => (
            <li key={idx} style={{marginBottom: '6px'}}>{instruction}</li>
          ))}
        </ol>
      </div>
      
      <div style={statsStyle}>
        <div style={statItemStyle}>
          <span style={{color: '#64748b'}}>Distance to Safety:</span>
          <strong style={{color: '#15803d'}}>
            {route.safety_margin_km.toFixed(1)} km
          </strong>
        </div>
        <div style={statItemStyle}>
          <span style={{color: '#64748b'}}>Estimated Time:</span>
          <strong>{route.duration_hours.toFixed(1)} hours</strong>
        </div>
        <div style={{...statItemStyle, borderBottom: 'none'}}>
          <span style={{color: '#64748b'}}>Fuel Required:</span>
          <strong>{route.fuel_required_liters.toFixed(1)} liters</strong>
        </div>
      </div>
      
      <div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '20px',
          marginBottom: '8px',
          fontSize: '14px',
          color: '#64748b'
        }}>
          <span>Progress</span>
          <span>{progress}% complete</span>
        </div>
        <div style={progressBarStyle}>
          <div style={progressFillStyle}></div>
        </div>
      </div>
      
      <div style={{
        marginTop: '20px',
        padding: '15px',
        background: '#dcfce7',
        borderRadius: '10px',
        fontSize: '14px',
        color: '#166534',
        textAlign: 'center',
        fontWeight: '600'
      }}>
        ✓ Following {route.type.toLowerCase()} route
        <br/>
        <span style={{fontSize: '12px', fontWeight: '400'}}>
          Stay on course to avoid maritime hazards
        </span>
      </div>
      
      {onStop && (
        <button
          onClick={onStop}
          style={{
            width: '100%',
            marginTop: '15px',
            padding: '14px',
            background: '#ef4444',
            color: 'white',
            border: 'none',
            borderRadius: '10px',
            fontSize: '15px',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'all 0.3s'
          }}
          onMouseEnter={(e) => e.target.style.background = '#dc2626'}
          onMouseLeave={(e) => e.target.style.background = '#ef4444'}
        >
          ⏹️ Stop Navigation
        </button>
      )}
    </div>
  );
}

export default Navigation;