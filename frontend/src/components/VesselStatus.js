import React from 'react';

function VesselStatus({ status }) {
  if (!status || status.total_points === 0) return null;
  
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
  
  const gridStyle = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '15px',
    marginBottom: '15px'
  };
  
  const statBoxStyle = {
    background: '#f8fafc',
    padding: '15px',
    borderRadius: '10px',
    textAlign: 'center'
  };
  
  const statLabelStyle = {
    fontSize: '12px',
    color: '#64748b',
    marginBottom: '6px'
  };
  
  const statValueStyle = {
    fontSize: '20px',
    fontWeight: '700',
    color: '#0f172a'
  };
  
  const getConfidenceBadge = () => {
    const colors = {
      'high': { bg: '#dcfce7', text: '#166534' },
      'medium': { bg: '#fef3c7', text: '#92400e' },
      'low': { bg: '#fee2e2', text: '#991b1b' },
      'none': { bg: '#f1f5f9', text: '#475569' }
    };
    
    const color = colors[status.confidence] || colors.none;
    
    return (
      <div style={{
        background: color.bg,
        color: color.text,
        padding: '8px 16px',
        borderRadius: '8px',
        fontSize: '14px',
        fontWeight: '600',
        textAlign: 'center'
      }}>
        {status.confidence.toUpperCase()} Confidence
      </div>
    );
  };
  
  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        🚤 Vessel Learning Status
      </div>
      
      <div style={gridStyle}>
        <div style={statBoxStyle}>
          <div style={statLabelStyle}>GPS Points</div>
          <div style={statValueStyle}>{status.total_points}</div>
        </div>
        
        <div style={statBoxStyle}>
          <div style={statLabelStyle}>Engine Status</div>
          <div style={statValueStyle}>
            {status.engine_currently_on ? '✓ ON' : '○ OFF'}
          </div>
        </div>
      </div>
      
      {status.learned_engine_speed && (
        <div style={{
          background: '#f0fdf4',
          padding: '15px',
          borderRadius: '10px',
          marginBottom: '15px'
        }}>
          <div style={{fontSize: '13px', color: '#166534', marginBottom: '6px'}}>
            Learned Speed (Engine ON)
          </div>
          <div style={{fontSize: '24px', fontWeight: '700', color: '#15803d'}}>
            {status.learned_engine_speed.toFixed(1)} km/h
          </div>
        </div>
      )}
      
      {getConfidenceBadge()}
      
      <div style={{
        marginTop: '15px',
        fontSize: '12px',
        color: '#64748b',
        textAlign: 'center',
        padding: '10px',
        background: '#f8fafc',
        borderRadius: '8px'
      }}>
        System learns your boat's actual speed from GPS data for more accurate predictions
      </div>
    </div>
  );
}

export default VesselStatus;