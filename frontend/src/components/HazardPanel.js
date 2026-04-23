import React from 'react';

function HazardPanel({ risks }) {
  if (!risks) {
    return null;
  }
  
  const panelStyle = {
    background: 'white',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.2)'
  };
  
  const headerStyle = {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#0f172a'
  };
  
  const riskScore = risks.total_risk_score || 0;
  const getRiskColor = () => {
    if (riskScore > 70) return '#dc2626';
    if (riskScore > 40) return '#f97316';
    return '#16a34a';
  };
  
  const scoreStyle = {
    background: getRiskColor(),
    color: 'white',
    padding: '30px',
    borderRadius: '10px',
    textAlign: 'center',
    marginBottom: '20px'
  };
  
  const hazardItemStyle = {
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '10px',
    borderLeft: '4px solid'
  };
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>⚠️ Hazard Assessment</div>
      
      <div style={scoreStyle}>
        <div style={{fontSize: '48px', fontWeight: 'bold'}}>{riskScore}</div>
        <div style={{fontSize: '14px', opacity: 0.9}}>Total Risk Score</div>
      </div>
      
      <div>
        {risks.boundary_crossing?.detected && (
          <div style={{
            ...hazardItemStyle,
            background: '#fee2e2',
            borderColor: '#dc2626'
          }}>
            <div style={{fontWeight: 'bold', marginBottom: '5px', color: '#991b1b'}}>
              🚨 Border Crossing Risk
            </div>
            <div style={{fontSize: '14px', color: '#7f1d1d'}}>
              Expected in {risks.boundary_crossing.first_crossing_time.toFixed(1)} hours
            </div>
          </div>
        )}
        
        {risks.cyclone?.detected && (
          <div style={{
            ...hazardItemStyle,
            background: '#fef3c7',
            borderColor: '#f59e0b'
          }}>
            <div style={{fontWeight: 'bold', marginBottom: '5px', color: '#92400e'}}>
              🌀 Cyclone Risk
            </div>
            <div style={{fontSize: '14px', color: '#78350f'}}>
              {risks.cyclone.cyclone_name || 'Active cyclone detected'}
            </div>
          </div>
        )}
        
        {risks.high_tide?.detected && (
          <div style={{
            ...hazardItemStyle,
            background: '#dbeafe',
            borderColor: '#3b82f6'
          }}>
            <div style={{fontWeight: 'bold', marginBottom: '5px', color: '#1e3a8a'}}>
              🌊 High Tide Warning
            </div>
            <div style={{fontSize: '14px', color: '#1e40af'}}>
              Tide height: {risks.high_tide.tide_height?.toFixed(2)}m
            </div>
          </div>
        )}
        
        {!risks.boundary_crossing?.detected && 
         !risks.cyclone?.detected && 
         !risks.high_tide?.detected && (
          <div style={{
            ...hazardItemStyle,
            background: '#dcfce7',
            borderColor: '#16a34a'
          }}>
            <div style={{fontWeight: 'bold', color: '#166534'}}>
              ✅ No Immediate Hazards Detected
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default HazardPanel;