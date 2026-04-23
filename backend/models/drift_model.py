"""
Core drift prediction model
Lagrangian particle tracking with wind leeway
"""

import numpy as np
from datetime import datetime, timedelta


class DriftModel:
    """
    Predicts vessel drift using ocean currents and wind
    """
    
    def __init__(self):
        self.timestep_minutes = 30  # 30-minute intervals
        self.earth_radius_km = 6371
    
    def predict_drift(self, start_lat, start_lon, duration_hours,
                     ocean_currents, wind_data, engine_on=False):
        """
        Predict drift trajectory
        
        Args:
            start_lat: Starting latitude
            start_lon: Starting longitude
            duration_hours: How far ahead to predict
            ocean_currents: Dict with 'u' and 'v' components (m/s)
            wind_data: Dict with 'speed' and 'direction' (m/s, degrees)
            engine_on: If True, reduce drift effect
        
        Returns:
            List of (lat, lon, time_hours) tuples
        """
        trajectory = [(start_lat, start_lon, 0)]
        
        current_lat = start_lat
        current_lon = start_lon
        
        num_steps = int(duration_hours * 60 / self.timestep_minutes)
        timestep_hours = self.timestep_minutes / 60.0
        
        for step in range(num_steps):
            # Ocean current components
            ocean_u = ocean_currents['u']  # m/s east
            ocean_v = ocean_currents['v']  # m/s north
            
            # Wind leeway (wind-induced drift)
            wind_leeway = self.calculate_wind_leeway(
                wind_data['speed'],
                wind_data['direction']
            )
            
            # Engine effect
            if engine_on:
                drift_factor = 0.3  # Engine reduces drift to 30%
            else:
                drift_factor = 1.0  # Full drift when engine off
            
            # Total drift velocity
            total_u = (ocean_u + wind_leeway['u']) * drift_factor
            total_v = (ocean_v + wind_leeway['v']) * drift_factor
            
            # Convert m/s to degrees displacement
            # 1 degree latitude ≈ 111.32 km
            # 1 degree longitude ≈ 111.32 km * cos(latitude)
            
            meters_per_hour = timestep_hours * 3600
            
            dlat = (total_v * meters_per_hour) / (111320)
            dlon = (total_u * meters_per_hour) / (111320 * np.cos(np.radians(current_lat)))
            
            current_lat += dlat
            current_lon += dlon
            
            time_elapsed = (step + 1) * timestep_hours
            trajectory.append((current_lat, current_lon, time_elapsed))
        
        return trajectory
    
    def calculate_wind_leeway(self, wind_speed, wind_direction):
        """
        Calculate wind-induced drift (leeway)
        Typical: 2-4% of wind speed at 10-30° to wind direction
        """
        leeway_coefficient = 0.03  # 3% of wind speed
        leeway_angle = 20  # degrees right of downwind
        
        # Effective direction (downwind + leeway angle)
        effective_direction = (wind_direction + 180 + leeway_angle) % 360
        
        # Leeway speed
        leeway_speed = wind_speed * leeway_coefficient
        
        # Convert to u, v components
        leeway_u = leeway_speed * np.sin(np.radians(effective_direction))
        leeway_v = leeway_speed * np.cos(np.radians(effective_direction))
        
        return {
            'u': float(leeway_u),
            'v': float(leeway_v),
            'speed': float(leeway_speed),
            'direction': float(effective_direction)
        }
    
    def haversine_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two points (km)
        """
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        return self.earth_radius_km * c