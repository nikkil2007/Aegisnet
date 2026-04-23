"""
Ensemble drift forecasting
Monte Carlo simulations for uncertainty quantification
"""

import numpy as np
from .drift_model import DriftModel


class EnsembleDriftModel:
    """
    Run multiple drift simulations with perturbed inputs
    to generate probabilistic forecasts
    """
    
    def __init__(self, num_simulations=100):
        self.num_simulations = num_simulations
        self.base_model = DriftModel()
    
    def predict_ensemble(self, start_lat, start_lon, duration_hours,
                        ocean_currents, wind_data, engine_on=False):
        """
        Run ensemble simulations
        
        Returns:
            Dict with time-indexed predictions and confidence intervals
        """
        all_trajectories = []
        
        for i in range(self.num_simulations):
            # Perturb inputs
            perturbed_currents = self.perturb_currents(ocean_currents)
            perturbed_wind = self.perturb_wind(wind_data)
            perturbed_position = self.perturb_position(start_lat, start_lon)
            
            # Run drift model
            trajectory = self.base_model.predict_drift(
                perturbed_position['lat'],
                perturbed_position['lon'],
                duration_hours,
                perturbed_currents,
                perturbed_wind,
                engine_on
            )
            
            all_trajectories.append(trajectory)
        
        # Compute statistics
        return self.compute_statistics(all_trajectories)
    
    def perturb_currents(self, currents):
        """Add uncertainty to ocean currents"""
        return {
            'u': currents['u'] + np.random.normal(0, 0.1),
            'v': currents['v'] + np.random.normal(0, 0.1)
        }
    
    def perturb_wind(self, wind):
        """Add uncertainty to wind"""
        return {
            'speed': max(0, wind['speed'] + np.random.normal(0, 0.5)),
            'direction': (wind['direction'] + np.random.normal(0, 10)) % 360
        }
    
    def perturb_position(self, lat, lon):
        """Add GPS uncertainty"""
        return {
            'lat': lat + np.random.normal(0, 0.0001),  # ~10m
            'lon': lon + np.random.normal(0, 0.0001)
        }
    
    def compute_statistics(self, all_trajectories):
        """
        Compute ensemble statistics at each time step
        """
        # Group by time
        time_groups = {}
        
        for trajectory in all_trajectories:
            for lat, lon, time in trajectory:
                time_key = round(time, 1)  # Round to 0.1 hour
                
                if time_key not in time_groups:
                    time_groups[time_key] = {'lats': [], 'lons': []}
                
                time_groups[time_key]['lats'].append(lat)
                time_groups[time_key]['lons'].append(lon)
        
        # Compute statistics for each time
        result = {}
        
        for time, positions in time_groups.items():
            lats = np.array(positions['lats'])
            lons = np.array(positions['lons'])
            
            result[time] = {
                'mean_lat': float(np.mean(lats)),
                'mean_lon': float(np.mean(lons)),
                'std_lat': float(np.std(lats)),
                'std_lon': float(np.std(lons)),
                'p50_lat': float(np.percentile(lats, 50)),
                'p50_lon': float(np.percentile(lons, 50)),
                'p90_lat': float(np.percentile(lats, 90)),
                'p90_lon': float(np.percentile(lons, 90))
            }
        
        return result