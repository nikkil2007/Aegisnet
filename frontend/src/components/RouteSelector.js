import React from 'react';

function RouteSelector({ routes, onSelectRoute }) {
  if (!routes) return null;
  
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
  
  const routeOptions = [
    {
      key: 'fastest',
      icon: '⚡',
      label: 'FASTEST',
      color: '#fef3c7',
      borderColor: '#f59e0b',
      description: 'Quickest route to safety'
    },
    {
      key: 'safest',
      icon: '🛡️',
      label: 'SAFEST',
      color: '#dcfce7',
      borderColor: '#16a34a',
      description: 'Maximum safety margin',
      recommended: true
    },
    {
      key: 'efficient',
      icon: '⛽',
      label: 'FUEL-EFFICIENT',
      color: '#dbeafe',
      borderColor: '#0284c7',
      description: 'Lowest fuel consumption'
    }
  ];
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        🧭 Escape Route Options
      </div>
      
      {routeOptions.map(option => {
        const route = routes[option.key];
        
        if (!route || route.type === 'EMERGENCY') {
          if (option.key === 'fastest' && route?.type === 'EMERGENCY') {
            return (
              <div key={option.key} style={{
                padding: '20px',
                background: '#fee2e2',
                border: '3px solid #dc2626',
                borderRadius: '12px',
                marginBottom: '15px'
              }}>
                <div style={{fontSize: '18px', fontWeight: '700', color: '#991b1b', marginBottom: '15px'}}>
                  🚨 EMERGENCY - NO SAFE ROUTE FOUND
                </div>
                {route.instructions.map((inst, idx) => (
                  <div key={idx} style={{
                    padding: '8px 0',
                    color: '#7f1d1d',
                    fontSize: '14px'
                  }}>
                    {inst}
                  </div>
                ))}
              </div>
            );
          }
          return null;
        }
        
        return (
          <div
            key={option.key}
            style={{
              padding: '20px',
              background: option.color,
              border: `2px solid ${option.borderColor}`,
              borderRadius: '12px',
              marginBottom: '15px',
              position: 'relative',
              transition: 'all 0.3s',
              cursor: 'pointer'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-2px)';
              e.currentTarget.style.boxShadow = '0 8px 20px rgba(0,0,0,0.15)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {option.recommended && (
              <div style={{
                position: 'absolute',
                top: '-10px',
                right: '15px',
                background: '#16a34a',
                color: 'white',
                padding: '4px 12px',
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: '700',
                boxShadow: '0 2px 8px rgba(22, 163, 74, 0.4)'
              }}>
                ⭐ RECOMMENDED
              </div>
            )}
            
            <div style={{
              fontSize: '20px',
              fontWeight: '700',
              marginBottom: '8px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px'
            }}>
              <span style={{fontSize: '24px'}}>{option.icon}</span>
              <span>{option.label}</span>
            </div>
            
            <div style={{fontSize: '13px', color: '#64748b', marginBottom: '15px'}}>
              {option.description}
            </div>
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: '120px 1fr',
              gap: '10px',
              fontSize: '14px',
              marginBottom: '15px'
            }}>
              <span style={{color: '#64748b'}}>Heading:</span>
              <span style={{fontWeight: '600'}}>
                {route.heading_degrees}° ({route.heading_cardinal})
              </span>
              
              <span style={{color: '#64748b'}}>Duration:</span>
              <span style={{fontWeight: '600'}}>
                {route.duration_hours.toFixed(1)} hours
              </span>
              
              <span style={{color: '#64748b'}}>Fuel:</span>
              <span style={{fontWeight: '600'}}>
                {route.fuel_required_liters.toFixed(1)} liters
              </span>
              
              <span style={{color: '#64748b'}}>Safety Margin:</span>
              <span style={{fontWeight: '600', color: '#16a34a'}}>
                {route.safety_margin_km.toFixed(1)} km
              </span>
            </div>
            
            <button
              onClick={() => onSelectRoute(route)}
              style={{
                width: '100%',
                padding: '14px',
                background: option.borderColor,
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '15px',
                fontWeight: '600',
                cursor: 'pointer',
                transition: 'all 0.3s',
                boxShadow: `0 4px 12px ${option.borderColor}40`
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'scale(1.02)';
                e.target.style.boxShadow = `0 6px 16px ${option.borderColor}60`;
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'scale(1)';
                e.target.style.boxShadow = `0 4px 12px ${option.borderColor}40`;
              }}
            >
              ✓ Select This Route
            </button>
          </div>
        );
      })}
    </div>
  );
}

export default RouteSelector;