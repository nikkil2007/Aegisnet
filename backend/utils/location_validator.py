"""
Location validation - ensures app only works in coastal waters
"""

from geopy.distance import geodesic
import numpy as np


class LocationValidator:
    """
    Validates if location is in valid maritime zone
    """
    
    def __init__(self):
        # Indian coastal coordinates (simplified)
        self.coastal_regions = {
            'tamil_nadu': {
                'name': 'Tamil Nadu Coast',
                'bounds': {
                    'lat_min': 8.0,
                    'lat_max': 13.5,
                    'lon_min': 77.5,
                    'lon_max': 80.5
                },
                'coastal_points': [
                    (13.09, 80.28),  # Chennai
                    (12.92, 79.28),  # Rameswaram
                    (10.79, 79.84),  # Karaikal
                    (8.08, 77.54)    # Kanyakumari
                ]
            },
            'kerala': {
                'name': 'Kerala Coast',
                'bounds': {
                    'lat_min': 8.0,
                    'lat_max': 12.8,
                    'lon_min': 74.5,
                    'lon_max': 76.0
                },
                'coastal_points': [
                    (11.87, 75.37),  # Kozhikode
                    (9.97, 76.28),   # Kochi
                    (8.52, 76.94)    # Trivandrum
                ]
            },
            'maharashtra': {
                'name': 'Maharashtra Coast',
                'bounds': {
                    'lat_min': 15.5,
                    'lat_max': 20.0,
                    'lon_min': 72.0,
                    'lon_max': 73.5
                },
                'coastal_points': [
                    (18.93, 72.83),  # Mumbai
                    (17.00, 73.30),  # Ratnagiri
                    (15.85, 73.67)   # Goa
                ]
            }
        }
        
        # Maximum distance from coast (km)
        self.max_offshore_distance = 200  # 200 km (exclusive economic zone)
        self.min_offshore_distance = 0.5   # 500m (must be in water)
    
    def validate_location(self, lat, lon):
        """
        Check if location is valid for maritime operations
        
        Returns:
            dict with validation result
        """
        # Check if in any coastal region bounds
        region = self.find_region(lat, lon)
        
        if not region:
            return {
                'valid': False,
                'reason': 'location_out_of_bounds',
                'message': 'Location is outside Indian coastal waters. AEGISNET only works in Indian maritime zones.',
                'suggestion': 'Move to coastal area (Tamil Nadu, Kerala, Maharashtra, Gujarat, West Bengal, Odisha, Andhra Pradesh, Karnataka, or Goa)'
            }
        
        # Check distance from coast
        distance_from_coast = self.calculate_distance_from_coast(lat, lon, region)
        
        if distance_from_coast < self.min_offshore_distance:
            return {
                'valid': False,
                'reason': 'too_close_to_shore',
                'message': f'You are on land or too close to shore ({distance_from_coast:.2f} km). AEGISNET is for vessels at sea.',
                'distance_from_coast': distance_from_coast,
                'suggestion': 'Move at least 500m offshore to start using AEGISNET'
            }
        
        if distance_from_coast > self.max_offshore_distance:
            return {
                'valid': False,
                'reason': 'too_far_offshore',
                'message': f'You are too far from coast ({distance_from_coast:.1f} km). AEGISNET works up to 200 km offshore.',
                'distance_from_coast': distance_from_coast,
                'suggestion': 'This system is designed for coastal fishing vessels, not deep-sea operations'
            }
        
        # Valid location
        return {
            'valid': True,
            'region': region['name'],
            'distance_from_coast': distance_from_coast,
            'message': f'Valid location in {region["name"]} ({distance_from_coast:.1f} km from coast)',
            'warning': self.get_location_warnings(distance_from_coast)
        }
    
    def find_region(self, lat, lon):
        """Find which coastal region this location belongs to"""
        for region_key, region_data in self.coastal_regions.items():
            bounds = region_data['bounds']
            
            if (bounds['lat_min'] <= lat <= bounds['lat_max'] and
                bounds['lon_min'] <= lon <= bounds['lon_max']):
                return region_data
        
        return None
    
    def calculate_distance_from_coast(self, lat, lon, region):
        """
        Calculate minimum distance from coast
        """
        min_distance = float('inf')
        
        for coast_lat, coast_lon in region['coastal_points']:
            distance = geodesic((lat, lon), (coast_lat, coast_lon)).km
            min_distance = min(min_distance, distance)
        
        return min_distance
    
    def get_location_warnings(self, distance_from_coast):
        """
        Get warnings based on distance from coast
        """
        warnings = []
        
        if distance_from_coast > 150:
            warnings.append('You are far from shore. Ensure adequate fuel for return journey.')
        
        if distance_from_coast > 100:
            warnings.append('Limited mobile network coverage expected at this distance.')
        
        if distance_from_coast < 2:
            warnings.append('Very close to shore. Watch for shallow waters and reefs.')
        
        return warnings