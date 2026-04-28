"""
Demo scenarios for AEGISNET presentation
Showcases all features without needing live data
"""

import numpy as np
from datetime import datetime

class DemoScenarios:
    """
    Preset scenarios for demonstration
    Each scenario shows different capabilities of AEGISNET
    """
    
    @staticmethod
    def get_scenario(lat, lon):
        """
        Returns demo data based on position
        Scenarios are triggered by specific coordinates
        """
        
        # Define scenario regions
        scenarios = [
        {
            'name': 'SCENARIO 1: Safe Fishing',
            'lat_range': (10.45, 10.55),   # Bay of Bengal
            'lon_range': (79.80, 79.90),
            'description': 'Normal fishing conditions - No hazards',
            'data': DemoScenarios.scenario_1_safe_fishing()
        },
        {
            'name': 'SCENARIO 2: Border Crossing Warning',
            'lat_range': (9.70, 9.80),     # Near IMBL
            'lon_range': (79.65, 79.75),
            'description': 'Drifting toward Sri Lankan waters',
            'data': DemoScenarios.scenario_2_border_crossing()
        },
        {
            'name': 'SCENARIO 3: Cyclone Danger',
            'lat_range': (13.20, 13.30),   # Bay of Bengal (cyclone zone)
            'lon_range': (80.40, 80.50),
            'description': 'Active cyclone in Bay of Bengal',
            'data': DemoScenarios.scenario_3_cyclone()
        },
        {
            'name': 'SCENARIO 4: Strong Currents',
            'lat_range': (11.75, 11.85),   # Palk Strait
            'lon_range': (79.90, 80.00),
            'description': 'Fast drift due to strong ocean currents',
            'data': DemoScenarios.scenario_4_strong_currents()
        },
        {
            'name': 'SCENARIO 5: Multiple Hazards',
            'lat_range': (9.30, 9.40),     # Near Mannar
            'lon_range': (79.50, 79.60),
            'description': 'High tide + Border + Strong currents',
            'data': DemoScenarios.scenario_5_multiple_hazards()
        },
        {
            'name': 'SCENARIO 6: Emergency',
            'lat_range': (10.00, 10.10),   # Critical zone
            'lon_range': (79.77, 79.87),
            'description': 'Surrounded by hazards - Emergency',
            'data': DemoScenarios.scenario_6_emergency()
        }
        ]
        
        # Check which scenario matches
        for scenario in scenarios:
            if (scenario['lat_range'][0] <= lat <= scenario['lat_range'][1] and
                scenario['lon_range'][0] <= lon <= scenario['lon_range'][1]):
                
                print(f"\n{'='*70}")
                print(f"🎬 DEMO MODE: {scenario['name']}")
                print(f"📝 {scenario['description']}")
                print(f"{'='*70}\n")
                
                return scenario['data']
        
        # Default to scenario 1 if no match
        print("\n⚠️ Position outside demo zones - using Scenario 1 (Safe Fishing)\n")
        return DemoScenarios.scenario_1_safe_fishing()
    
    # ========================================================================
    # SCENARIO 1: SAFE FISHING - NO HAZARDS
    # ========================================================================
    @staticmethod
    def scenario_1_safe_fishing():
        """
        Perfect conditions for fishing
        - Low wind, low current
        - No hazards detected
        - Risk score: 5/100
        """
        return {
            'ocean_currents': {
                'u': 0.15,  # Weak current
                'v': -0.20,
                'magnitude': 0.25,
                'direction': 143
            },
            'wind': {
                'speed': 2.5,  # Light breeze
                'speed_kmh': 9.0,
                'direction': 45
            },
            'risks': {
                'boundary_crossing': {'detected': False},
                'cyclone': {'detected': False},
                'high_tide': {'detected': False},
                'strong_currents': {'detected': False},
                'restricted_zone': {'detected': False},
                'shallow_water': {'detected': False},
                'total_risk_score': 5
            },
            'drift_multiplier': 1.0,  # Normal drift
            'engine_on': False
        }
    
    # ========================================================================
    # SCENARIO 2: BORDER CROSSING WARNING
    # ========================================================================
    @staticmethod
    def scenario_2_border_crossing():
        """
        Drifting toward Sri Lankan maritime boundary
        - Moderate wind pushing southeast
        - Will cross border in 18 hours
        - Risk score: 75/100
        - Shows escape routes
        """
        return {
            'ocean_currents': {
                'u': 0.45,  # Strong eastward push
                'v': -0.55,  # Strong southward push
                'magnitude': 0.71,
                'direction': 141
            },
            'wind': {
                'speed': 5.5,  # Moderate wind
                'speed_kmh': 19.8,
                'direction': 135  # Southeast
            },
            'risks': {
                'boundary_crossing': {
                    'detected': True,
                    'severity': 'HIGH',
                    'first_crossing_time': 18.5,  # Hours
                    'closest_approach': -0.5,  # Will cross by 500m
                    'details': [
                        {
                            'time_hours': 18.5,
                            'distance_km': -0.5,
                            'crossed': True,
                            'position': (9.65, 79.82)
                        }
                    ]
                },
                'cyclone': {'detected': False},
                'high_tide': {'detected': False},
                'strong_currents': {'detected': False},
                'restricted_zone': {'detected': False},
                'shallow_water': {'detected': False},
                'total_risk_score': 75
            },
            'drift_multiplier': 1.8,  # Faster drift
            'engine_on': False,
            'escape_routes_needed': True
        }
    
    # ========================================================================
    # SCENARIO 3: CYCLONE DANGER
    # ========================================================================
    @staticmethod
    def scenario_3_cyclone():
        """
        Active cyclone approaching
        - Very high winds (90 km/h)
        - Rapid drift toward cyclone eye
        - Risk score: 95/100 (CRITICAL)
        - Multiple escape routes shown
        """
        return {
            'ocean_currents': {
                'u': 0.8,  # Very strong current
                'v': -1.2,
                'magnitude': 1.44,
                'direction': 146
            },
            'wind': {
                'speed': 25.0,  # Storm-force winds
                'speed_kmh': 90.0,
                'direction': 150
            },
            'risks': {
                'boundary_crossing': {'detected': False},
                'cyclone': {
                    'detected': True,
                    'severity': 'CRITICAL',
                    'cyclone_name': 'Cyclone Michaung',
                    'entry_time': 12.0,  # Will enter cyclone in 12 hours
                    'distance_from_center': 85,  # km
                    'wind_speed_kmh': 120
                },
                'high_tide': {'detected': False},
                'strong_currents': {
                    'detected': True,
                    'severity': 'HIGH',
                    'current_speed_ms': 1.44,
                    'current_direction': 146
                },
                'restricted_zone': {'detected': False},
                'shallow_water': {'detected': False},
                'total_risk_score': 95
            },
            'drift_multiplier': 3.5,  # Extreme drift
            'engine_on': False,
            'escape_routes_needed': True,
            'active_cyclone': {
                'name': 'Cyclone Michaung',
                'center_lat': 14.2,
                'center_lon': 80.8,
                'radius_km': 250,
                'wind_speed_kmh': 120,
                'movement_direction': 315,
                'movement_speed_kmh': 18
            }
        }
    
    # ========================================================================
    # SCENARIO 4: STRONG CURRENTS
    # ========================================================================
    @staticmethod
    def scenario_4_strong_currents():
        """
        Fast drift due to strong monsoon currents
        - High current speed (1.5 m/s)
        - Moderate wind
        - Will drift 25 km in 24 hours
        - Risk score: 45/100
        """
        return {
            'ocean_currents': {
                'u': 0.9,
                'v': -1.2,
                'magnitude': 1.5,  # Very strong
                'direction': 143
            },
            'wind': {
                'speed': 4.5,
                'speed_kmh': 16.2,
                'direction': 120
            },
            'risks': {
                'boundary_crossing': {'detected': False},
                'cyclone': {'detected': False},
                'high_tide': {'detected': False},
                'strong_currents': {
                    'detected': True,
                    'severity': 'MEDIUM',
                    'current_speed_ms': 1.5,
                    'current_direction': 143
                },
                'restricted_zone': {'detected': False},
                'shallow_water': {'detected': False},
                'total_risk_score': 45
            },
            'drift_multiplier': 2.5,  # Very fast drift
            'engine_on': False
        }
    
    # ========================================================================
    # SCENARIO 5: MULTIPLE HAZARDS
    # ========================================================================
    @staticmethod
    def scenario_5_multiple_hazards():
        """
        Combination of threats
        - High tide (dangerous)
        - Border crossing
        - Strong currents
        - Risk score: 85/100
        """
        return {
            'ocean_currents': {
                'u': 0.65,
                'v': -0.75,
                'magnitude': 1.0,
                'direction': 139
            },
            'wind': {
                'speed': 6.5,
                'speed_kmh': 23.4,
                'direction': 140
            },
            'risks': {
                'boundary_crossing': {
                    'detected': True,
                    'severity': 'HIGH',
                    'first_crossing_time': 22.0,
                    'closest_approach': -1.2,
                    'details': [
                        {
                            'time_hours': 22.0,
                            'distance_km': -1.2,
                            'crossed': True,
                            'position': (9.35, 79.83)
                        }
                    ]
                },
                'cyclone': {'detected': False},
                'high_tide': {
                    'detected': True,
                    'severity': 'MEDIUM',
                    'tide_height': 1.8,  # meters
                    'next_high_tide_hours': 3.5
                },
                'strong_currents': {
                    'detected': True,
                    'severity': 'MEDIUM',
                    'current_speed_ms': 1.0,
                    'current_direction': 139
                },
                'restricted_zone': {'detected': False},
                'shallow_water': {'detected': False},
                'total_risk_score': 85
            },
            'drift_multiplier': 2.0,
            'engine_on': False,
            'escape_routes_needed': True
        }
    
    # ========================================================================
    # SCENARIO 6: EMERGENCY - NO SAFE ROUTE
    # ========================================================================
    @staticmethod
    def scenario_6_emergency():
        """
        Worst case scenario
        - Surrounded by hazards
        - Border very close
        - Cyclone approaching
        - Strong currents
        - No completely safe escape route
        - Risk score: 100/100
        - Emergency protocols triggered
        """
        return {
            'ocean_currents': {
                'u': 1.1,
                'v': -1.3,
                'magnitude': 1.7,
                'direction': 140
            },
            'wind': {
                'speed': 18.0,
                'speed_kmh': 64.8,
                'direction': 145
            },
            'risks': {
                'boundary_crossing': {
                    'detected': True,
                    'severity': 'CRITICAL',
                    'first_crossing_time': 6.0,
                    'closest_approach': -3.0,
                    'details': [
                        {
                            'time_hours': 6.0,
                            'distance_km': -3.0,
                            'crossed': True,
                            'position': (9.95, 79.88)
                        }
                    ]
                },
                'cyclone': {
                    'detected': True,
                    'severity': 'CRITICAL',
                    'cyclone_name': 'Cyclone Emergency',
                    'entry_time': 8.0,
                    'distance_from_center': 45,
                    'wind_speed_kmh': 140
                },
                'high_tide': {
                    'detected': True,
                    'severity': 'HIGH',
                    'tide_height': 2.1,
                    'next_high_tide_hours': 1.5
                },
                'strong_currents': {
                    'detected': True,
                    'severity': 'HIGH',
                    'current_speed_ms': 1.7,
                    'current_direction': 140
                },
                'restricted_zone': {
                    'detected': True,
                    'severity': 'MEDIUM',
                    'violations': [
                        {
                            'time_hours': 10.0,
                            'zone_name': 'Naval Exercise Zone',
                            'zone_type': 'military',
                            'distance_from_center_km': 8.0
                        }
                    ]
                },
                'shallow_water': {'detected': False},
                'total_risk_score': 100
            },
            'drift_multiplier': 4.0,  # Extreme
            'engine_on': False,
            'escape_routes_needed': True,
            'emergency_mode': True,
            'active_cyclone': {
                'name': 'Cyclone Emergency',
                'center_lat': 10.5,
                'center_lon': 80.2,
                'radius_km': 200,
                'wind_speed_kmh': 140,
                'movement_direction': 290,
                'movement_speed_kmh': 22
            }
        }