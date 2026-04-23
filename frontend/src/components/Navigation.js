import React from 'react';

function Navigation({ route, currentPosition }) {
  if (!route) return null;
  
  const panelStyle = {
    background: 'white',
    padding: '25px',
    borderRadius: '15px',
    boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
    border: '3px solid #16a34a'
  };
  
  const headerStyle = {
    fontSize: '20px',
    fontWeight: 'bold',
    marginBottom: '20px',
    color: '#15803d'
  };
  
  const compassStyle = {
    width: '150px',
    height: '150px',
    margin: '0 auto 20px',
    background: 'white',
    borderRadius: '50%',
    border: '4px solid #16a34a',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative'
  };
  
  const needleStyle = {
    fontSize: '60px',
    lineHeight: 1
  };
  
  const statsStyle = {
    background: '#f0fdf4',
    padding: '15px',
    borderRadius: '8px',
    marginTop: '20px'
  };
  
  const statItemStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    borderBottom: '1px solid #dcfce7'
  };
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>🧭 Active Navigation</div>
      
      <div style={compassStyle}>
        <div style={needleStyle}>↑</div>
        <div style={{fontSize: '32px', fontWeight: 'bold', color: '#15803d'}}>
          {route.heading}°
        </div>
        <div style={{fontSize: '16px', color: '#64748b'}}>
          {route.cardinal}
        </div>
      </div>
      
      <div style={{
        background: '#fef3c7',
        padding: '15px',
        borderRadius: '8px',
        marginBottom: '20px',
        textAlign: 'center',
        fontWeight: '600',
        color: '#92400e'
      }}>
        Turn boat to heading {route.heading}° ({route.cardinal})
      </div>
      
      <div style={statsStyle}>
        <div style={statItemStyle}>
          <span>Distance to Safety:</span>
          <strong>{route.safety} km</strong>
        </div>
        <div style={statItemStyle}>
          <span>Estimated Time:</span>
          <strong>{route.duration} hours</strong>
        </div>
        <div style={{...statItemStyle, borderBottom: 'none'}}>
          <span>Fuel Required:</span>
          <strong>{route.fuel} liters</strong>
        </div>
      </div>
      
      <div style={{
        marginTop: '15px',
        padding: '10px',
        background: '#dcfce7',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#166534',
        textAlign: 'center'
      }}>
        ✓ Following safest route to avoid border crossing
      </div>
    </div>
  );
}

export default Navigation;