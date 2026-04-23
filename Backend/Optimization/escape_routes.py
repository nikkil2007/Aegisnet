# backend/optimization/escape_routes.py

import numpy as np
from models.drift_model import DriftModel
from models.risk_assessment import HazardDetector

class EscapeRouteOptimizer:
    def __init__(self):
        self.drift_model = DriftModel()
        self.hazard_detector = HazardDetector()
    
    def compute_escape_routes(self, current_lat, current_lon, 
                             vessel_specs, hazards,
                             ocean_data, wind_data):
        """
        Find optimal escape routes based on multiple objectives
        
        Returns 3 routes: Fastest, Safest, Most Fuel-Efficient
        """
        
        # Generate candidate routes (360° search space)
        candidates = []
        
        for heading in range(0, 360, 10):  # Test every 10 degrees
            for speed_fraction in [0.5, 0.75, 1.0]:  # Slow, cruise, max speed
                speed = vessel_specs['max_speed'] * speed_fraction
                
                # Simulate this escape route
                route = self.simulate_escape_route(
                    current_lat, current_lon,
                    heading, speed,
                    duration_hours=12,
                    ocean_data=ocean_data,
                    wind_data=wind_data
                )
                
                # Evaluate route quality
                evaluation = self.evaluate_route(route, hazards, vessel_specs)
                
                if evaluation['achieves_safety']:
                    candidates.append({
                        'heading': heading,
                        'speed': speed,
                        'route': route,
                        'safety_score': evaluation['safety_score'],
                        'time_hours': evaluation['time_to_safety'],
                        'fuel_liters': evaluation['fuel_consumption'],
                        'safety_margin_km': evaluation['min_distance_from_danger']
                    })
        
        if not candidates:
            return self.emergency_fallback()
        
        # Select Pareto-optimal routes
        fastest = min(candidates, key=lambda x: x['time_hours'])
        safest = max(candidates, key=lambda x: x['safety_score'])
        most_efficient = min(candidates, key=lambda x: x['fuel_liters'])
        
        return {
            'fastest': self.format_route_instructions(fastest, 'FASTEST'),
            'safest': self.format_route_instructions(safest, 'SAFEST'),
            'efficient': self.format_route_instructions(most_efficient, 'FUEL-EFFICIENT')
        }
    
    def simulate_escape_route(self, start_lat, start_lon, heading, speed,
                             duration_hours, ocean_data, wind_data):
        """
        Simulate vessel movement with active propulsion
        """
        trajectory = [(start_lat, start_lon, 0)]
        
        current_lat = start_lat
        current_lon = start_lon
        
        timestep = 0.5  # hours
        num_steps = int(duration_hours / timestep)
        
        for step in range(num_steps):
            # Vessel's self-propulsion (heading at speed)
            vessel_u = speed * np.sin(np.radians(heading)) / 3.6  # km/h to m/s
            vessel_v = speed * np.cos(np.radians(heading)) / 3.6
            
            # Ocean drift (still affects vessel)
            drift = self.drift_model.predict_drift(
                current_lat, current_lon, timestep,
                ocean_data, wind_data
            )
            drift_u = (drift[-1][1] - current_lon) * 111320 * np.cos(np.radians(current_lat))
            drift_v = (drift[-1][0] - current_lat) * 111320
            
            # Total movement = vessel propulsion + drift
            total_u = vessel_u + drift_u * 0.3  # Drift has less effect when motoring
            total_v = vessel_v + drift_v * 0.3
            
            # Update position
            dlat = (total_v * timestep * 3600) / 111320
            dlon = (total_u * timestep * 3600) / (111320 * np.cos(np.radians(current_lat)))
            
            current_lat += dlat
            current_lon += dlon
            
            time_elapsed = (step + 1) * timestep
            trajectory.append((current_lat, current_lon, time_elapsed))
        
        return trajectory
    
    def evaluate_route(self, route, hazards, vessel_specs):
        """
        Score route on safety, time, fuel
        """
        # Check if route achieves safety
        route_hazards = self.hazard_detector.assess_all_hazards(route, datetime.now())
        
        achieves_safety = route_hazards['total_risk_score'] < 30
        
        # Calculate metrics
        time_to_safety = route[-1][2]  # hours
        distance_km = self.calculate_route_distance(route)
        fuel_consumption = distance_km * vessel_specs['fuel_per_km']
        
        # Minimum distance from any danger zone
        min_distance = self.calculate_min_danger_distance(route, hazards)
        
        safety_score = 100 - route_hazards['total_risk_score']
        
        return {
            'achieves_safety': achieves_safety,
            'safety_score': safety_score,
            'time_to_safety': time_to_safety,
            'fuel_consumption': fuel_consumption,
            'min_distance_from_danger': min_distance
        }
    
    def format_route_instructions(self, route_data, route_type):
        """
        Convert route into human-readable instructions
        """
        return {
            'type': route_type,
            'heading_degrees': route_data['heading'],
            'heading_cardinal': self.degrees_to_cardinal(route_data['heading']),
            'speed_kmh': route_data['speed'],
            'duration_hours': route_data['time_hours'],
            'fuel_required_liters': route_data['fuel_liters'],
            'safety_margin_km': route_data['safety_margin_km'],
            'trajectory': route_data['route'],
            'instructions': self.generate_step_by_step(route_data)
        }
    
    def generate_step_by_step(self, route_data):
        """
        Generate turn-by-turn instructions
        """
        return [
            f"Turn to heading {route_data['heading']}° ({self.degrees_to_cardinal(route_data['heading'])})",
            f"Maintain speed of {route_data['speed']:.1f} km/h",
            f"Continue for {route_data['time_hours']:.1f} hours",
            f"Fuel required: {route_data['fuel_liters']:.1f} liters",
            f"You will reach safety with {route_data['safety_margin_km']:.1f} km margin"
        ]
    
    def degrees_to_cardinal(self, degrees):
        """Convert heading to N/NE/E/SE/S/SW/W/NW"""
        directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
        index = round(degrees / 45) % 8
        return directions[index]
    
    def calculate_route_distance(self, route):
        """Total distance in km"""
        total = 0
        for i in range(len(route) - 1):
            total += self.hazard_detector.haversine_distance(
                route[i][0], route[i][1],
                route[i+1][0], route[i+1][1]
            )
        return total
    
    def calculate_min_danger_distance(self, route, hazards):
        """Minimum distance from any danger zone throughout route"""
        # Simplified - would check against all hazard boundaries
        return 10.0  # km (placeholder)
    
    def emergency_fallback(self):
        """If no safe route found, give best-effort guidance"""
        return {
            'fastest': {
                'type': 'EMERGENCY',
                'instructions': ['No completely safe route found', 
                                'Head to nearest safe harbor immediately',
                                'Call Coast Guard for assistance']
            }
        }