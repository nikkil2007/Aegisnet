import React from 'react';

function LocationValidator({ validation }) {
  if (!validation || validation.valid) return null;
  
  const containerStyle = {
    background: '#fef2f2',
    border: '3px solid #dc2626',
    borderRadius: '15px',
    padding: '25px',
    boxShadow: '0 10px 30px rgba(220, 38, 38, 0.2)',
    animation: 'slideIn 0.5s ease-out'
  };
  
  const headerStyle = {
    fontSize: '22px',
    fontWeight: '700',
    color: '#991b1b',
    marginBottom: '15px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px'
  };
  
  const messageStyle = {
    fontSize: '16px',
    color: '#7f1d1d',
    marginBottom: '15px',
    lineHeight: '1.6'
  };
  
  const suggestionStyle = {
    background: '#fee2e2',
    padding: '15px',
    borderRadius: '10px',
    borderLeft: '4px solid #dc2626',
    marginTop: '15px'
  };
  
  const suggestionTitleStyle = {
    fontSize: '14px',
    fontWeight: '700',
    color: '#991b1b',
    marginBottom: '8px'
  };
  
  const suggestionTextStyle = {
    fontSize: '14px',
    color: '#7f1d1d',
    lineHeight: '1.5'
  };
  
  return (
    <>
      <style>{`
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
      
      <div style={containerStyle}>
        <div style={headerStyle}>
          🚫 Location Not Valid for AEGISNET
        </div>
        
        <div style={messageStyle}>
          <strong>Reason:</strong> {validation.message}
        </div>
        
        {validation.distance_from_coast !== undefined && (
          <div style={messageStyle}>
            <strong>Distance from coast:</strong> {validation.distance_from_coast.toFixed(1)} km
          </div>
        )}
        
        {validation.suggestion && (
          <div style={suggestionStyle}>
            <div style={suggestionTitleStyle}>💡 Suggestion:</div>
            <div style={suggestionTextStyle}>{validation.suggestion}</div>
          </div>
        )}
        
        <div style={{
          marginTop: '20px',
          padding: '12px',
          background: 'white',
          borderRadius: '8px',
          fontSize: '13px',
          color: '#64748b'
        }}>
          <strong>Valid zones:</strong> 0.5 km - 200 km from Indian coastline (Tamil Nadu, Kerala, Maharashtra, Gujarat, West Bengal, Odisha, Andhra Pradesh, Karnataka, Goa)
        </div>
      </div>
    </>
  );
}

export default LocationValidator;