"""
Multi-hazard risk assessment
Detects all 6 types of maritime hazards
"""

import numpy as np
from datetime import datetime


class RiskAssessment:
    """
    Comprehensive hazard detection system
    """
    
    def __init__(self):
        # Maritime boundaries
        self.boundaries = {
            'india_sri_lanka': {
                'lat_range': (8.0, 11.0),
                'lon_threshold': 79.8,
                'buffer_km': 5
            },
            'india_pakistan': {
                'lat_range': (23.0, 24.5),
                'lon_threshold': 68.2,
                'buffer_km': 5
            }
        }
        
        # Restricted zones
        self.restricted_zones = [
            {
                'name': 'Naval Exercise Zone - Mumbai',
                'center_lat': 18.8,
                'center_lon': 72.7,
                'radius_km': 30,
                'type': 'military'
            }
        ]
    
    def assess_all_risks(self, trajectory, current_time=None):
        """
        Check all 6 hazard types
        """
        if current_time is None:
            current_time = datetime.now()
        
        risks = {
            'boundary_crossing': self.check_boundary_crossing(trajectory),
            'cyclone': self.check_cyclone_risk(trajectory),
            'high_tide': self.check_tide_risk(current_time, trajectory[0]),
            'strong_currents': self.check_current_strength(trajectory),
            'restricted_zone': self.check_restricted_zones(trajectory),
            'shallow_water': self.check_shallow_water(trajectory),
            'timestamp': current_time.isoformat()
        }
        
        risks['total_risk_score'] = self.compute_total_risk(risks)
        
        return risks
    
    def check_boundary_crossing(self, trajectory):
        """Maritime boundary crossing detection"""
        boundary = self.boundaries['india_sri_lanka']
        crossings = []
        
        for lat, lon, time in trajectory:
            if boundary['lat_range'][0] <= lat <= boundary['lat_range'][1]:
                distance = (lon - boundary['lon_threshold']) * 111.32 * np.cos(np.radians(lat))
                
                if distance > -5:
                    crossings.append({
                        'time_hours': float(time),
                        'distance_km': float(distance),
                        'crossed': distance > 0,
                        'position': (float(lat), float(lon))
                    })
        
        if crossings:
            first = min(crossings, key=lambda x: x['time_hours'])
            return {
                'detected': True,
                'severity': 'HIGH' if first['crossed'] else 'MEDIUM',
                'first_crossing_time': first['time_hours'],
                'closest_approach': min(c['distance_km'] for c in crossings),
                'details': crossings
            }
        
        return {'detected': False}
    
    def check_cyclone_risk(self, trajectory):
        """Cyclone intersection detection"""
        from backend.utils.data_fetch import fetch_cyclone_data
        
        cyclones = fetch_cyclone_data()
        
        if not cyclones:
            return {'detected': False}
        
        for cyclone in cyclones:
            for lat, lon, time in trajectory:
                distance = self.haversine_distance(
                    lat, lon, cyclone['center_lat'], cyclone['center_lon']
                )
                
                if distance < cyclone['radius_km']:
                    return {
                        'detected': True,
                        'severity': 'CRITICAL',
                        'cyclone_name': cyclone['name'],
                        'entry_time': float(time),
                        'distance_from_center': float(distance),
                        'wind_speed_kmh': cyclone['wind_speed_kmh']
                    }
        
        return {'detected': False}
    
    def check_tide_risk(self, current_time, start_position):
        """Dangerous tide detection"""
        from backend.utils.data_fetch import fetch_tide_data
        
        lat, lon, _ = start_position
        tide = fetch_tide_data(lat, lon, current_time)
        
        if tide['is_dangerous']:
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'tide_height': tide['height'],
                'next_high_tide_hours': tide['next_high_tide_hours']
            }
        
        return {'detected': False}
    
    def check_current_strength(self, trajectory):
        """Strong current detection"""
        from backend.utils.data_fetch import fetch_ocean_currents
        
        lat, lon, _ = trajectory[0]
        currents = fetch_ocean_currents(lat, lon)
        
        magnitude = currents['magnitude']
        
        if magnitude > 1.5:  # Strong current threshold
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'current_speed_ms': float(magnitude),
                'current_direction': float(currents['direction'])
            }
        
        return {'detected': False}
    
    def check_restricted_zones(self, trajectory):
        """Restricted zone entry detection"""
        violations = []
        
        for lat, lon, time in trajectory:
            for zone in self.restricted_zones:
                distance = self.haversine_distance(
                    lat, lon, zone['center_lat'], zone['center_lon']
                )
                
                if distance < zone['radius_km']:
                    violations.append({
                        'time_hours': float(time),
                        'zone_name': zone['name'],
                        'zone_type': zone['type'],
                        'distance_from_center_km': float(distance)
                    })
        
        if violations:
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'violations': violations
            }
        
        return {'detected': False}
    
    def check_shallow_water(self, trajectory):
        """Shallow water / reef detection"""
        # Simplified: check if very close to known shallow areas
        # Real implementation would use bathymetry data
        
        known_shallow_areas = [
            {'lat': 9.3, 'lon': 79.2, 'radius_km': 10, 'name': 'Palk Bay Shallows'}
        ]
        
        for lat, lon, time in trajectory:
            for area in known_shallow_areas:
                distance = self.haversine_distance(
                    lat, lon, area['lat'], area['lon']
                )
                
                if distance < area['radius_km']:
                    return {
                        'detected': True,
                        'severity': 'MEDIUM',
                        'area_name': area['name'],
                        'entry_time': float(time),
                        'distance_km': float(distance)
                    }
        
        return {'detected': False}
    
    def compute_total_risk(self, risks):
        """Aggregate risk score"""
        weights = {
            'cyclone': 100,
            'boundary_crossing': 80,
            'shallow_water': 60,
            'restricted_zone': 50,
            'high_tide': 40,
            'strong_currents': 30
        }
        
        total = 0
        for risk_type, weight in weights.items():
            if risks.get(risk_type, {}).get('detected', False):
                total += weight
        
        return min(total, 100)
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Distance in km"""
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        return 6371 * c