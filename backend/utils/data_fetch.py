"""
Environmental data fetching utilities
Provides ocean currents, wind, tide, and cyclone data
"""

import requests
from datetime import datetime
import numpy as np


def fetch_ocean_currents(lat, lon, date=None):
    """
    Fetch ocean current data
    Returns simulated realistic data for demo
    """
    if date is None:
        date = datetime.now()
    
    try:
        # Simulated ocean currents (realistic for Indian coastal waters)
        # Typical: 0.3-0.8 m/s with tidal variation
        
        hour = date.hour
        
        # Base current (southeast direction typical for Bay of Bengal)
        base_u = 0.35  # East-west component (m/s)
        base_v = -0.55  # North-south component (m/s)
        
        # Add tidal variation (semi-diurnal)
        tidal_u = 0.15 * np.sin(2 * np.pi * hour / 12.42)
        tidal_v = 0.20 * np.cos(2 * np.pi * hour / 12.42)
        
        # Add small random variation
        noise_u = np.random.normal(0, 0.05)
        noise_v = np.random.normal(0, 0.05)
        
        u_current = base_u + tidal_u + noise_u
        v_current = base_v + tidal_v + noise_v
        
        return {
            'u': float(u_current),
            'v': float(v_current),
            'magnitude': float(np.sqrt(u_current**2 + v_current**2)),
            'direction': float(np.arctan2(u_current, v_current) * 180 / np.pi),
            'timestamp': date.isoformat()
        }
    
    except Exception as e:
        print(f"Error in fetch_ocean_currents: {e}")
        return {
            'u': 0.4,
            'v': -0.6,
            'magnitude': 0.72,
            'direction': 146.3,
            'timestamp': datetime.now().isoformat()
        }


def fetch_wind_data(lat, lon, date=None):
    """
    Fetch wind data
    Returns simulated realistic data for demo
    """
    if date is None:
        date = datetime.now()
    
    try:
        # Simulated wind (typical coastal winds)
        # Daytime: stronger, from sea
        # Night: weaker, variable
        
        hour = date.hour
        
        # Diurnal variation
        if 6 <= hour <= 18:
            # Daytime: sea breeze
            base_speed = 4.5  # m/s (16 km/h)
            base_direction = 45  # Northeast
        else:
            # Nighttime: land breeze
            base_speed = 2.5  # m/s (9 km/h)
            base_direction = 225  # Southwest
        
        # Add random variation
        speed = base_speed + np.random.normal(0, 0.5)
        direction = base_direction + np.random.normal(0, 15)
        
        return {
            'speed': float(max(0, speed)),  # m/s
            'speed_kmh': float(max(0, speed) * 3.6),  # km/h
            'direction': float(direction % 360),  # degrees
            'timestamp': date.isoformat()
        }
    
    except Exception as e:
        print(f"Error in fetch_wind_data: {e}")
        return {
            'speed': 3.5,
            'speed_kmh': 12.6,
            'direction': 45,
            'timestamp': datetime.now().isoformat()
        }


def fetch_tide_data(lat, lon, date=None):
    """
    Fetch tidal data using harmonic constituents
    """
    if date is None:
        date = datetime.now()
    
    try:
        hour = date.hour
        minute = date.minute
        day = date.day
        
        # Time in hours
        time_hours = hour + minute / 60.0
        
        # Principal tidal constituents
        M2 = 1.2 * np.cos(2 * np.pi * time_hours / 12.42)  # Principal lunar
        S2 = 0.5 * np.cos(2 * np.pi * time_hours / 12.00)  # Principal solar
        K1 = 0.3 * np.cos(2 * np.pi * time_hours / 23.93)  # Lunar diurnal
        
        # Spring-neap cycle (simplified)
        spring_neap = 0.3 * np.cos(2 * np.pi * day / 14.77)
        
        tide_height = M2 + S2 + K1 + spring_neap
        
        return {
            'height': float(tide_height),
            'is_high_tide': bool(tide_height > 1.0),
            'is_dangerous': bool(tide_height > 1.5),
            'next_high_tide_hours': float(12.42 - (time_hours % 12.42)),
            'timestamp': date.isoformat()
        }
    
    except Exception as e:
        print(f"Error in fetch_tide_data: {e}")
        return {
            'height': 0.5,
            'is_high_tide': False,
            'is_dangerous': False,
            'next_high_tide_hours': 6.0,
            'timestamp': datetime.now().isoformat()
        }


def fetch_cyclone_data():
    """
    Fetch active cyclone data
    Returns empty list for demo (no active cyclones)
    """
    try:
        # For demo: no active cyclones
        # In production: integrate with IMD API
        
        active_cyclones = []
        
        # Uncomment to test cyclone detection:
        # active_cyclones = [{
        #     'name': 'Test Cyclone',
        #     'center_lat': 13.5,
        #     'center_lon': 80.2,
        #     'radius_km': 300,
        #     'wind_speed_kmh': 120,
        #     'category': 'severe'
        # }]
        
        return active_cyclones
    
    except Exception as e:
        print(f"Error in fetch_cyclone_data: {e}")
        return []