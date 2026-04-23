# backend/models/risk_assessment.py
from Backend.Utils.data_fetch import fetch_tide_data
import json
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points

class HazardDetector:
    def __init__(self):
        self.load_boundaries()
        self.load_restricted_zones()
    
    def load_boundaries(self):
        """Load maritime boundary data"""
        with open('../data/boundaries/india_maritime.json') as f:
            self.boundaries = json.load(f)
    
    def load_restricted_zones(self):
        """Load fishing restrictions, naval areas, etc."""
        self.restricted_zones = [
            {
                'name': 'Naval Exercise Zone - Mumbai',
                'center_lat': 18.9,
                'center_lon': 72.8,
                'radius_km': 50,
                'type': 'military'
            }
        ]
    
    def assess_all_hazards(self, trajectory, current_time):
        """
        Check trajectory against ALL hazard types
        
        Returns dict of risks with timing and severity
        """
        hazards = {
            'boundary_crossing': self.check_boundary_crossing(trajectory),
            'cyclone_risk': self.check_cyclone_intersection(trajectory, current_time),
            'high_tide_danger': self.check_tide_hazard(trajectory, current_time),
            'strong_currents': self.check_current_strength(trajectory),
            'restricted_zone': self.check_restricted_zones(trajectory),
            'shallow_water': self.check_depth(trajectory)
        }
        
        # Compute overall risk score
        hazards['total_risk_score'] = self.compute_total_risk(hazards)
        
        return hazards
    
    def check_boundary_crossing(self, trajectory):
        """Detect if trajectory crosses maritime boundary"""
        boundary_line = LineString(
            self.boundaries['india_sri_lanka_boundary']['coordinates']
        )
        
        crossings = []
        
        for i, (lat, lon, time) in enumerate(trajectory):
            point = Point(lon, lat)
            distance_km = self.point_to_line_distance(point, boundary_line)
            
            if distance_km < 5:  # Within 5km of boundary
                crossings.append({
                    'time_hours': time,
                    'distance_km': distance_km,
                    'position': (lat, lon),
                    'crossed': distance_km < 0.1  # Actually crossed
                })
        
        if crossings:
            return {
                'detected': True,
                'severity': 'HIGH',
                'first_crossing_time': crossings[0]['time_hours'],
                'closest_approach': min(c['distance_km'] for c in crossings),
                'details': crossings
            }
        
        return {'detected': False}
    
    def check_cyclone_intersection(self, trajectory, current_time):
        """Check if trajectory enters cyclone path"""
        # Fetch active cyclones
        from utils.data_fetch import fetch_cyclone_data
        cyclones = fetch_cyclone_data()
        
        risks = []
        
        for cyclone in cyclones:
            for lat, lon, time in trajectory:
                # Project cyclone position at this future time
                cyclone_future = self.project_cyclone_position(
                    cyclone, 
                    current_time + timedelta(hours=time)
                )
                
                # Calculate distance from projected cyclone center
                distance_km = self.haversine_distance(
                    lat, lon,
                    cyclone_future['lat'], cyclone_future['lon']
                )
                
                if distance_km < cyclone['radius_km']:
                    risks.append({
                        'time_hours': time,
                        'cyclone_name': cyclone['name'],
                        'distance_from_center_km': distance_km,
                        'expected_wind_speed': self.estimate_wind_at_distance(
                            distance_km, cyclone['wind_speed_kmh']
                        )
                    })
        
        if risks:
            return {
                'detected': True,
                'severity': 'CRITICAL',
                'first_entry_time': min(r['time_hours'] for r in risks),
                'max_wind_speed': max(r['expected_wind_speed'] for r in risks),
                'details': risks
            }
        
        return {'detected': False}
    
    def check_tide_hazard(self, trajectory, current_time):
        """Check for dangerous tidal conditions"""
        from utils.data_fetch import fetch_tide_data
        
        dangerous_times = []
        
        for lat, lon, time in trajectory:
            tide = fetch_tide_data(
                lat, lon, 
                current_time + timedelta(hours=time)
            )
            
            if tide['is_dangerous']:
                dangerous_times.append({
                    'time_hours': time,
                    'tide_height_m': tide['height'],
                    'position': (lat, lon)
                })
        
        if dangerous_times:
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'dangerous_periods': dangerous_times
            }
        
        return {'detected': False}
    
    def check_current_strength(self, trajectory):
        """Detect unusually strong currents"""
        # Check if ocean currents exceed safe threshold
        strong_current_threshold = 1.5  # m/s
        
        # This would use actual current data at trajectory points
        # Placeholder for demo
        return {'detected': False}
    
    def check_restricted_zones(self, trajectory):
        """Check if entering restricted fishing zones"""
        violations = []
        
        for lat, lon, time in trajectory:
            for zone in self.restricted_zones:
                distance_km = self.haversine_distance(
                    lat, lon,
                    zone['center_lat'], zone['center_lon']
                )
                
                if distance_km < zone['radius_km']:
                    violations.append({
                        'time_hours': time,
                        'zone_name': zone['name'],
                        'zone_type': zone['type'],
                        'distance_from_center_km': distance_km
                    })
        
        if violations:
            return {
                'detected': True,
                'severity': 'MEDIUM',
                'violations': violations
            }
        
        return {'detected': False}
    
    def check_depth(self, trajectory):
        """Check for shallow water / reef hazards"""
        # Would require bathymetry data
        # Placeholder
        return {'detected': False}
    
    def compute_total_risk(self, hazards):
        """Aggregate risk score from all hazards"""
        weights = {
            'cyclone_risk': 100,
            'boundary_crossing': 80,
            'high_tide_danger': 40,
            'strong_currents': 30,
            'restricted_zone': 50,
            'shallow_water': 60
        }
        
        total = 0
        for hazard_type, weight in weights.items():
            if hazards[hazard_type]['detected']:
                total += weight
        
        return min(total, 100)  # Cap at 100
    
    # Helper functions
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance in km between two points"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371  # Earth radius in km
        
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def point_to_line_distance(self, point, line):
        """Distance from point to nearest point on line"""
        nearest = nearest_points(point, line)[1]
        return self.haversine_distance(
            point.y, point.x,
            nearest.y, nearest.x
        )
    
    def project_cyclone_position(self, cyclone, future_time):
        """Project where cyclone will be at future time"""
        # Simplified linear projection
        hours_ahead = (future_time - datetime.now()).total_seconds() / 3600
        
        distance_km = cyclone['movement_speed_kmh'] * hours_ahead
        
        # Convert to lat/lon displacement
        direction_rad = np.radians(cyclone['movement_direction'])
        dlat = (distance_km * np.cos(direction_rad)) / 111.32
        dlon = (distance_km * np.sin(direction_rad)) / (111.32 * np.cos(np.radians(cyclone['center_lat'])))
        
        return {
            'lat': cyclone['center_lat'] + dlat,
            'lon': cyclone['center_lon'] + dlon
        }
    
    def estimate_wind_at_distance(self, distance_km, center_wind_speed):
        """Estimate wind speed at distance from cyclone center"""
        # Simplified model: wind decreases with distance from center
        if distance_km < 50:
            return center_wind_speed
        elif distance_km < 100:
            return center_wind_speed * 0.7
        elif distance_km < 200:
            return center_wind_speed * 0.4
        else:
            return center_wind_speed * 0.2