import React from 'react';

function HazardPanel({ risks }) {
  if (!risks) return null;
  
  const panelStyle = {
    background: 'white',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.15)'
  };
  
  const headerStyle = {
    fontSize: '20px',
    fontWeight: '700',
    marginBottom: '20px',
    color: '#0f172a',
    display: 'flex',
    alignItems: 'center',
    gap: '10px'
  };
  
  const riskScore = risks.total_risk_score || 0;
  
  const getRiskColor = () => {
    if (riskScore > 70) return '#dc2626';
    if (riskScore > 40) return '#f97316';
    return '#16a34a';
  };
  
  const getRiskLabel = () => {
    if (riskScore > 70) return 'HIGH RISK';
    if (riskScore > 40) return 'MEDIUM RISK';
    return 'LOW RISK';
  };
  
  const scoreStyle = {
    background: getRiskColor(),
    color: 'white',
    padding: '30px',
    borderRadius: '12px',
    textAlign: 'center',
    marginBottom: '20px',
    boxShadow: `0 8px 20px ${getRiskColor()}40`
  };
  
  const hazards = [
    {
      key: 'boundary_crossing',
      icon: '🚨',
      name: 'Border Crossing',
      color: '#dc2626',
      bgColor: '#fee2e2'
    },
    {
      key: 'cyclone',
      icon: '🌀',
      name: 'Cyclone Risk',
      color: '#7c2d12',
      bgColor: '#fef3c7'
    },
    {
      key: 'high_tide',
      icon: '🌊',
      name: 'High Tide',
      color: '#1e40af',
      bgColor: '#dbeafe'
    },
    {
      key: 'strong_currents',
      icon: '💧',
      name: 'Strong Currents',
      color: '#0369a1',
      bgColor: '#e0f2fe'
    },
    {
      key: 'restricted_zone',
      icon: '⛔',
      name: 'Restricted Zone',
      color: '#b91c1c',
      bgColor: '#fef2f2'
    },
    {
      key: 'shallow_water',
      icon: '⚓',
      name: 'Shallow Water',
      color: '#b45309',
      bgColor: '#fef9c3'
    }
  ];
  
  const detectedHazards = hazards.filter(h => risks[h.key]?.detected);
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        ⚠️ Multi-Hazard Assessment
      </div>
      
      <div style={scoreStyle}>
        <div style={{fontSize: '56px', fontWeight: '700', marginBottom: '8px'}}>
          {riskScore}
        </div>
        <div style={{fontSize: '16px', opacity: 0.95, fontWeight: '600'}}>
          {getRiskLabel()}
        </div>
        <div style={{fontSize: '13px', opacity: 0.8, marginTop: '8px'}}>
          Total Risk Score
        </div>
      </div>
      
      <div>
        {detectedHazards.length === 0 ? (
          <div style={{
            padding: '20px',
            background: '#dcfce7',
            borderRadius: '10px',
            color: '#166534',
            textAlign: 'center',
            fontSize: '15px',
            fontWeight: '600'
          }}>
            ✅ No Immediate Hazards Detected
            <div style={{fontSize: '13px', marginTop: '8px', fontWeight: '400'}}>
              All maritime conditions are currently safe
            </div>
          </div>
        ) : (
          detectedHazards.map((hazard, idx) => {
            const data = risks[hazard.key];
            
            return (
              <div
                key={idx}
                style={{
                  padding: '18px',
                  background: hazard.bgColor,
                  borderLeft: `4px solid ${hazard.color}`,
                  borderRadius: '10px',
                  marginBottom: '12px'
                }}
              >
                <div style={{
                  fontWeight: '700',
                  marginBottom: '8px',
                  color: hazard.color,
                  fontSize: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px'
                }}>
                  <span>{hazard.icon}</span>
                  <span>{hazard.name}</span>
                  {data.severity && (
                    <span style={{
                      marginLeft: 'auto',
                      fontSize: '12px',
                      padding: '4px 10px',
                      background: 'white',
                      borderRadius: '6px'
                    }}>
                      {data.severity}
                    </span>
                  )}
                </div>
                
                <div style={{fontSize: '14px', color: hazard.color}}>
                  {data.first_crossing_time && (
                    <div>⏱️ ETA: {data.first_crossing_time.toFixed(1)} hours</div>
                  )}
                  {data.entry_time && (
                    <div>⏱️ Entry: {data.entry_time.toFixed(1)} hours</div>
                  )}
                  {data.cyclone_name && (
                    <div>🌀 {data.cyclone_name}</div>
                  )}
                  {data.wind_speed_kmh && (
                    <div>💨 Wind: {data.wind_speed_kmh} km/h</div>
                  )}
                  {data.tide_height && (
                    <div>🌊 Tide: {data.tide_height.toFixed(2)}m</div>
                  )}
                  {data.current_speed_ms && (
                    <div>💧 Current: {data.current_speed_ms.toFixed(2)} m/s</div>
                  )}
                  {data.closest_approach && (
                    <div>📍 Closest: {data.closest_approach.toFixed(1)} km</div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default HazardPanel;