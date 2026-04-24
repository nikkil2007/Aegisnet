"""
Escape route optimization
Calculates optimal paths to avoid hazards
"""

import numpy as np
from .drift_model import DriftModel


class RouteOptimizer:
    """
    Computes optimal escape routes based on multiple objectives
    """
    
    def __init__(self):
        self.drift_model = DriftModel()
    
    def compute_escape_routes(self, current_lat, current_lon, 
                             vessel_speed, hazards,
                             ocean_currents, wind_data):
        """
        Find 3 optimal escape routes: Fastest, Safest, Most Efficient
        
        Returns:
            Dict with 3 route options
        """
        print(f"Computing escape routes from {current_lat:.4f}, {current_lon:.4f}")
        
        # Test multiple headings
        candidate_routes = []
        
        for heading in range(0, 360, 15):  # Every 15 degrees
            for speed_fraction in [0.7, 0.85, 1.0]:  # Different speeds
                
                speed = vessel_speed * speed_fraction
                
                # Simulate this route
                route = self.simulate_escape_route(
                    current_lat, current_lon,
                    heading, speed,
                    duration_hours=8,
                    ocean_currents=ocean_currents,
                    wind_data=wind_data
                )
                
                # Evaluate route
                evaluation = self.evaluate_route(route, hazards, vessel_speed, speed)
                
                if evaluation['achieves_safety']:
                    candidate_routes.append({
                        'heading_degrees': heading,
                        'heading_cardinal': self.degrees_to_cardinal(heading),
                        'speed_kmh': speed,
                        'speed_fraction': speed_fraction,
                        'trajectory': route,
                        'safety_score': evaluation['safety_score'],
                        'time_hours': evaluation['time_to_safety'],
                        'fuel_liters': evaluation['fuel_consumption'],
                        'safety_margin_km': evaluation['min_danger_distance']
                    })
        
        if not candidate_routes:
            print("⚠️ No safe routes found! Using emergency fallback")
            return self.emergency_fallback(current_lat, current_lon)
        
        print(f"✅ Found {len(candidate_routes)} candidate routes")
        
        # Select best routes
        fastest = min(candidate_routes, key=lambda x: x['time_hours'])
        safest = max(candidate_routes, key=lambda x: x['safety_score'])
        efficient = min(candidate_routes, key=lambda x: x['fuel_liters'])
        
        return {
            'fastest': self.format_route(fastest, 'FASTEST'),
            'safest': self.format_route(safest, 'SAFEST'),
            'efficient': self.format_route(efficient, 'FUEL-EFFICIENT')
        }
    
    def simulate_escape_route(self, start_lat, start_lon, heading, speed,
                             duration_hours, ocean_currents, wind_data):
        """
        Simulate vessel movement with engine on
        """
        trajectory = [(start_lat, start_lon, 0)]
        
        current_lat = start_lat
        current_lon = start_lon
        
        timestep_hours = 0.5
        num_steps = int(duration_hours / timestep_hours)
        
        for step in range(num_steps):
            # Vessel propulsion (m/s)
            vessel_u = (speed / 3.6) * np.sin(np.radians(heading))
            vessel_v = (speed / 3.6) * np.cos(np.radians(heading))
            
            # Ocean drift (reduced when engine on)
            drift_u = ocean_currents['u'] * 0.3
            drift_v = ocean_currents['v'] * 0.3
            
            # Wind leeway (reduced when engine on)
            wind_leeway = self.drift_model.calculate_wind_leeway(
                wind_data['speed'], wind_data['direction']
            )
            leeway_u = wind_leeway['u'] * 0.2
            leeway_v = wind_leeway['v'] * 0.2
            
            # Total movement
            total_u = vessel_u + drift_u + leeway_u
            total_v = vessel_v + drift_v + leeway_v
            
            # Update position
            meters_per_step = timestep_hours * 3600
            
            dlat = (total_v * meters_per_step) / 111320
            dlon = (total_u * meters_per_step) / (111320 * np.cos(np.radians(current_lat)))
            
            current_lat += dlat
            current_lon += dlon
            
            time_elapsed = (step + 1) * timestep_hours
            trajectory.append((current_lat, current_lon, time_elapsed))
        
        return trajectory
    
    def evaluate_route(self, route, hazards, max_speed, actual_speed):
        """
        Score a route on safety, time, and fuel
        """
        # Calculate time to safety
        time_to_safety = route[-1][2]
        
        # Calculate fuel consumption
        # Fuel consumption increases with speed squared
        speed_factor = (actual_speed / max_speed) ** 2
        base_consumption = 0.5  # L/km at cruise speed
        consumption_rate = base_consumption * speed_factor
        
        distance_km = self.calculate_route_distance(route)
        fuel_consumption = distance_km * consumption_rate
        
        # Calculate min distance from danger
        min_danger_distance = self.calculate_min_danger_distance(route, hazards)
        
        # Safety score (0-100)
        if min_danger_distance < 5:
            safety_score = 20  # Still in danger
        elif min_danger_distance < 10:
            safety_score = 50  # Marginal safety
        elif min_danger_distance < 20:
            safety_score = 75  # Good safety
        else:
            safety_score = 95  # Excellent safety
        
        # Achieves safety if min distance > 5 km
        achieves_safety = min_danger_distance > 5
        
        return {
            'achieves_safety': achieves_safety,
            'safety_score': safety_score,
            'time_to_safety': time_to_safety,
            'fuel_consumption': fuel_consumption,
            'min_danger_distance': min_danger_distance
        }
    
    def calculate_route_distance(self, route):
        """Total distance in km"""
        total = 0
        for i in range(len(route) - 1):
            total += self.drift_model.haversine_distance(
                route[i][0], route[i][1],
                route[i+1][0], route[i+1][1]
            )
        return total
    
    def calculate_min_danger_distance(self, route, hazards):
        """
        Calculate minimum distance from any danger zone
        """
        # Simplified: distance from boundary
        # Real implementation: check all hazard types
        
        boundary_lon = 79.8  # India-Sri Lanka boundary (simplified)
        
        min_distance = float('inf')
        
        for lat, lon, time in route:
            # Distance from boundary (approximation)
            distance = abs(lon - boundary_lon) * 111.32 * np.cos(np.radians(lat))
            min_distance = min(min_distance, distance)
        
        return max(0, min_distance)
    
    def format_route(self, route_data, route_type):
        """
        Format route for API response
        """
        return {
            'type': route_type,
            'heading_degrees': route_data['heading_degrees'],
            'heading_cardinal': route_data['heading_cardinal'],
            'speed_kmh': route_data['speed_kmh'],
            'duration_hours': route_data['time_hours'],
            'fuel_required_liters': route_data['fuel_liters'],
            'safety_margin_km': route_data['safety_margin_km'],
            'trajectory': [
                {'lat': t[0], 'lon': t[1], 'time': t[2]}
                for t in route_data['trajectory'][::4]  # Sample
            ],
            'instructions': [
                f"Turn to heading {route_data['heading_degrees']}° ({route_data['heading_cardinal']})",
                f"Maintain speed of {route_data['speed_kmh']:.1f} km/h",
                f"Continue for {route_data['time_hours']:.1f} hours",
                f"Fuel required: {route_data['fuel_liters']:.1f} liters",
                f"Safety margin: {route_data['safety_margin_km']:.1f} km from danger"
            ]
        }
    
    def degrees_to_cardinal(self, degrees):
        """Convert heading to compass direction"""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(degrees / 22.5) % 16
        return directions[index]
    
    def emergency_fallback(self, lat, lon):
        """
        Emergency response when no safe route found
        """
        return {
            'fastest': {
                'type': 'EMERGENCY',
                'heading_degrees': 270,
                'heading_cardinal': 'W',
                'instructions': [
                    '🚨 NO COMPLETELY SAFE ROUTE FOUND',
                    'Head WEST (270°) immediately',
                    'Call Coast Guard: 1554',
                    'Activate emergency beacon if available',
                    'Maintain maximum safe speed'
                ]
            },
            'safest': None,
            'efficient': None
        }