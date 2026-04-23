import React from 'react';

function RouteSelector({ onSelectRoute }) {
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
  
  // Demo routes
  const routes = [
    {
      type: 'FASTEST',
      icon: '⚡',
      heading: 315,
      cardinal: 'NW',
      duration: 2.5,
      fuel: 14,
      safety: 8,
      color: '#fef3c7'
    },
    {
      type: 'SAFEST',
      icon: '🛡️',
      heading: 285,
      cardinal: 'WNW',
      duration: 4,
      fuel: 10,
      safety: 18,
      color: '#dcfce7'
    },
    {
      type: 'FUEL-EFFICIENT',
      icon: '⛽',
      heading: 270,
      cardinal: 'W',
      duration: 5.5,
      fuel: 7,
      safety: 12,
      color: '#dbeafe'
    }
  ];
  
  const routeCardStyle = {
    padding: '20px',
    borderRadius: '10px',
    marginBottom: '15px',
    border: '2px solid #cbd5e1'
  };
  
  const buttonStyle = {
    width: '100%',
    padding: '12px',
    background: '#0ea5e9',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    marginTop: '10px'
  };
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>🧭 Escape Route Options</div>
      
      {routes.map((route, idx) => (
        <div 
          key={idx}
          style={{...routeCardStyle, background: route.color}}
        >
          <div style={{fontSize: '18px', fontWeight: 'bold', marginBottom: '15px'}}>
            {route.icon} {route.type}
          </div>
          
          <div style={{fontSize: '14px', lineHeight: '2'}}>
            <div><strong>Heading:</strong> {route.heading}° ({route.cardinal})</div>
            <div><strong>Duration:</strong> {route.duration} hours</div>
            <div><strong>Fuel:</strong> {route.fuel} liters</div>
            <div><strong>Safety Margin:</strong> {route.safety} km</div>
          </div>
          
          <button 
            style={buttonStyle}
            onClick={() => onSelectRoute(route)}
            onMouseOver={(e) => e.target.style.background = '#0284c7'}
            onMouseOut={(e) => e.target.style.background = '#0ea5e9'}
          >
            Select This Route
          </button>
        </div>
      ))}
    </div>
  );
}

export default RouteSelector;