# backend/models/drift_model.py

import numpy as np
from datetime import datetime, timedelta

class DriftModel:
    def __init__(self):
        self.timestep_hours = 0.5  # 30-minute intervals
        
    def predict_drift(self, start_lat, start_lon, duration_hours, 
                      ocean_currents, wind_data, vessel_type='fishing_boat'):
        """
        Predict drift trajectory using Lagrangian particle tracking
        
        Parameters:
        - start_lat, start_lon: Initial position
        - duration_hours: How far to predict
        - ocean_currents: Dict with 'u' and 'v' components
        - wind_data: Dict with 'speed' and 'direction'
        - vessel_type: Affects wind leeway
        
        Returns:
        - List of (lat, lon, time) positions
        """
        
        # Initialize trajectory
        trajectory = [(start_lat, start_lon, 0)]
        
        current_lat = start_lat
        current_lon = start_lon
        
        num_steps = int(duration_hours / self.timestep_hours)
        
        for step in range(num_steps):
            # Get current ocean velocity at this position
            ocean_u = self.interpolate_current(current_lat, current_lon, 
                                                ocean_currents['u'])
            ocean_v = self.interpolate_current(current_lat, current_lon, 
                                                ocean_currents['v'])
            
            # Calculate wind-induced drift (leeway)
            wind_leeway = self.calculate_wind_leeway(
                wind_data['speed'], 
                wind_data['direction'],
                vessel_type
            )
            
            # Total velocity = ocean current + wind leeway
            total_u = ocean_u + wind_leeway['u']
            total_v = ocean_v + wind_leeway['v']
            
            # Update position (convert m/s to lat/lon displacement)
            dlat = (total_v * self.timestep_hours * 3600) / 111320  # meters to degrees
            dlon = (total_u * self.timestep_hours * 3600) / (111320 * np.cos(np.radians(current_lat)))
            
            current_lat += dlat
            current_lon += dlon
            
            time_elapsed = (step + 1) * self.timestep_hours
            trajectory.append((current_lat, current_lon, time_elapsed))
        
        return trajectory
    
    def calculate_wind_leeway(self, wind_speed, wind_direction, vessel_type):
        """
        Wind-induced drift (leeway)
        Typical: 2-5% of wind speed at 10-40° to wind direction
        """
        leeway_coefficients = {
            'fishing_boat': 0.03,  # 3% of wind speed
            'dinghy': 0.05,
            'person_in_water': 0.035
        }
        
        coeff = leeway_coefficients.get(vessel_type, 0.03)
        leeway_angle = 20  # degrees right of wind direction
        
        # Convert to components
        effective_direction = wind_direction + leeway_angle
        leeway_speed = wind_speed * coeff
        
        leeway_u = leeway_speed * np.sin(np.radians(effective_direction))
        leeway_v = leeway_speed * np.cos(np.radians(effective_direction))
        
        return {'u': leeway_u, 'v': leeway_v}
    
    def interpolate_current(self, lat, lon, current_grid):
        """
        Interpolate current value at exact lat/lon from gridded data
        """
        # Simplified - real implementation uses scipy.interpolate
        return current_grid.mean()  # Placeholder