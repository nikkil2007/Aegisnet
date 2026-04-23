# backend/models/ensemble.py

import numpy as np
from drift_model import DriftModel

class EnsembleDriftModel:
    def __init__(self, num_simulations=1000):
        self.num_simulations = num_simulations
        self.base_model = DriftModel()
    
    def predict_ensemble(self, start_lat, start_lon, duration_hours,
                        ocean_currents, wind_data, vessel_type='fishing_boat'):
        """
        Run Monte Carlo ensemble simulations
        """
        all_trajectories = []
        
        for i in range(self.num_simulations):
            # Perturb inputs within uncertainty bounds
            perturbed_currents = self.perturb_currents(ocean_currents)
            perturbed_wind = self.perturb_wind(wind_data)
            perturbed_start = self.perturb_position(start_lat, start_lon)
            
            # Run drift model with perturbed inputs
            trajectory = self.base_model.predict_drift(
                perturbed_start['lat'],
                perturbed_start['lon'],
                duration_hours,
                perturbed_currents,
                perturbed_wind,
                vessel_type
            )
            
            all_trajectories.append(trajectory)
        
        return self.compute_probability_cone(all_trajectories)
    
    def perturb_currents(self, currents):
        """Add random noise to current data"""
        noise_std = 0.1  # 10% uncertainty
        return {
            'u': currents['u'] + np.random.normal(0, noise_std * abs(currents['u'])),
            'v': currents['v'] + np.random.normal(0, noise_std * abs(currents['v']))
        }
    
    def perturb_wind(self, wind):
        """Add random noise to wind data"""
        return {
            'speed': wind['speed'] + np.random.normal(0, 0.15 * wind['speed']),
            'direction': wind['direction'] + np.random.normal(0, 10)  # ±10 degrees
        }
    
    def perturb_position(self, lat, lon):
        """Add GPS uncertainty"""
        return {
            'lat': lat + np.random.normal(0, 0.0001),  # ~10m uncertainty
            'lon': lon + np.random.normal(0, 0.0001)
        }
    
    def compute_probability_cone(self, all_trajectories):
        """
        Convert ensemble trajectories into probability distribution
        """
        # Group positions by time step
        time_steps = {}
        
        for trajectory in all_trajectories:
            for lat, lon, time in trajectory:
                if time not in time_steps:
                    time_steps[time] = []
                time_steps[time].append((lat, lon))
        
        # Compute percentile contours for each time
        probability_cone = {}
        
        for time, positions in time_steps.items():
            lats = [p[0] for p in positions]
            lons = [p[1] for p in positions]
            
            probability_cone[time] = {
                'most_likely': (np.median(lats), np.median(lons)),
                'confidence_50': self.compute_contour(lats, lons, 50),
                'confidence_70': self.compute_contour(lats, lons, 70),
                'confidence_90': self.compute_contour(lats, lons, 90),
                'uncertainty': np.std(lats) + np.std(lons)
            }
        
        return probability_cone
    
    def compute_contour(self, lats, lons, percentile):
        """Compute ellipse containing percentile% of points"""
        from scipy.spatial import ConvexHull
        
        # Simplified: use bounding ellipse
        center_lat = np.mean(lats)
        center_lon = np.mean(lons)
        
        # Standard deviations scaled to percentile
        scale = percentile / 100.0
        radius_lat = np.std(lats) * scale
        radius_lon = np.std(lons) * scale
        
        return {
            'center': (center_lat, center_lon),
            'radius_lat': radius_lat,
            'radius_lon': radius_lon
        }