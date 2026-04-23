"""
Multi-hazard risk assessment
Detects boundary crossings, cyclones, tides, etc.
"""

import numpy as np
from datetime import datetime


class RiskAssessment:
    """
    Assess multiple maritime hazards
    """
    
    def __init__(self):
        # India-Sri Lanka maritime boundary (simplified)
        self.boundaries = {
            'india_sri_lanka': {
                'type': 'line',
                'lat_range': (8.0, 11.0),
                'lon_threshold': 79.8,  # Simplified: east of this = Sri Lankan waters
                'buffer_km': 5
            }
        }
    
    def assess_all_risks(self, trajectory, current_time=None):
        """
        Check trajectory against all hazards
        
        Args:
            trajectory: List of (lat, lon, time) tuples
            current_time: Reference time (default: now)
        
        Returns:
            Dict with risk assessment
        """
        if current_time is None:
            current_time = datetime.now()
        
        risks = {
            'boundary_crossing': self.check_boundary_crossing(trajectory),
            'cyclone': self.check_cyclone_risk(trajectory),
            'high_tide': self.check_tide_risk(current_time),
            'timestamp': current_time.isoformat()
        }
        
        # Compute total risk score
        risks['total_risk_score'] = self.compute_total_risk(risks)
        
        return risks
    
    def check_boundary_crossing(self, trajectory):
        """
        Check if trajectory crosses maritime boundary
        """
        boundary = self.boundaries['india_sri_lanka']
        
        crossings = []
        
        for lat, lon, time in trajectory:
            # Check if in boundary zone
            if boundary['lat_range'][0] <= lat <= boundary['lat_range'][1]:
                distance_from_boundary = (lon - boundary['lon_threshold']) * 111.32 * np.cos(np.radians(lat))
                
                if distance_from_boundary > -5:  # Within 5 km or crossed
                    crossings.append({
                        'time_hours': float(time),
                        'distance_km': float(distance_from_boundary),
                        'crossed': distance_from_boundary > 0,
                        'position': (float(lat), float(lon))
                    })
        
        if crossings:
            first_crossing = min(crossings, key=lambda x: x['time_hours'])
            
            return {
                'detected': True,
                'severity': 'HIGH' if first_crossing['crossed'] else 'MEDIUM',
                'first_crossing_time': first_crossing['time_hours'],
                'closest_approach': min(c['distance_km'] for c in crossings),
                'details': crossings
            }
        
        return {'detected': False}
    
    def check_cyclone_risk(self, trajectory):
        """
        Check if trajectory intersects cyclone
        Currently returns no risk (can be extended)
        """
        # Fetch cyclone data
        from utils.data_fetch import fetch_cyclone_data
        
        cyclones = fetch_cyclone_data()
        
        if not cyclones:
            return {'detected': False}
        
        # Check intersection
        for cyclone in cyclones:
            for lat, lon, time in trajectory:
                distance = self.haversine_distance(
                    lat, lon,
                    cyclone['center_lat'],
                    cyclone['center_lon']
                )
                
                if distance < cyclone['radius_km']:
                    return {
                        'detected': True,
                        'severity': 'CRITICAL',
                        'cyclone_name': cyclone['name'],
                        'entry_time': float(time),
                        'distance_from_center': float(distance)
                    }
        
        return {'detected': False}
    
    def check_tide_risk(self, current_time):
        """
        Check for dangerous tidal conditions
        """
        from utils.data_fetch import fetch_tide_data
        
        # Use arbitrary coastal location for demo
        tide = fetch_tide_data(12.9, 79.3, current_time)
        
        if tide['is_dangerous']:
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'tide_height': tide['height'],
                'next_high_tide_hours': tide['next_high_tide_hours']
            }
        
        return {'detected': False}
    
    def compute_total_risk(self, risks):
        """
        Aggregate risk score (0-100)
        """
        weights = {
            'boundary_crossing': 80,
            'cyclone': 100,
            'high_tide': 40
        }
        
        total = 0
        
        for risk_type, weight in weights.items():
            if risks.get(risk_type, {}).get('detected', False):
                total += weight
        
        return min(total, 100)
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in km"""
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return 6371 * c