# backend/utils/data_fetch.py

import requests
from datetime import datetime, timedelta
import numpy as np

def fetch_ocean_currents(lat, lon, date):
    """
    Fetch ocean current data from HYCOM
    """
    # HYCOM OPeNDAP URL
    base_url = "https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0"
    
    # Parameters
    params = {
        'var': 'water_u,water_v',  # U and V current components
        'north': lat + 2,
        'south': lat - 2,
        'east': lon + 2,
        'west': lon - 2,
        'time': date.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
    
    # Note: This is pseudocode - actual HYCOM access requires netCDF4
    # Real implementation:
    from netCDF4 import Dataset
    
    dataset = Dataset(f"{base_url}?{encode_params(params)}")
    u_current = dataset.variables['water_u'][:]
    v_current = dataset.variables['water_v'][:]
    
    return {
        'u': u_current,  # East-west component
        'v': v_current,  # North-south component
        'lat': lat,
        'lon': lon,
        'time': date
    }

def fetch_wind_data(lat, lon, date):
    """
    Fetch wind data from NASA POWER API
    """
    url = "https://power.larc.nasa.gov/api/temporal/hourly/point"
    
    params = {
        'parameters': 'WS10M,WD10M',  # Wind speed and direction at 10m
        'community': 'RE',
        'longitude': lon,
        'latitude': lat,
        'start': date.strftime('%Y%m%d'),
        'end': date.strftime('%Y%m%d'),
        'format': 'JSON'
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    return {
        'wind_speed': data['properties']['parameter']['WS10M'],
        'wind_direction': data['properties']['parameter']['WD10M']
    }

def fetch_tide_data(lat, lon, date):
    """
    Fetch tidal predictions
    """
    # For Indian coast: Use INCOIS tide tables
    # For hackathon: Use astronomical tide prediction
    
    from scipy import signal
    
    # Simplified tidal model (M2, S2, K1, O1 constituents)
    # Real implementation needs actual harmonic constants
    
    hour_of_day = date.hour
    day_of_year = date.timetuple().tm_yday
    
    # Tidal harmonics (simplified)
    M2 = 1.2 * np.cos(2 * np.pi * hour_of_day / 12.42)  # Principal lunar
    S2 = 0.5 * np.cos(2 * np.pi * hour_of_day / 12.00)  # Principal solar
    
    tide_height = M2 + S2  # meters above mean sea level
    
    return {
        'height': tide_height,
        'is_high_tide': tide_height > 1.0,
        'is_dangerous': tide_height > 1.5
    }

def fetch_cyclone_data():
    """
    Fetch active cyclone information
    """
    # IMD Cyclone Warning Division
    # Website: https://mausam.imd.gov.in/
    
    # For demo: Use IBTrACS (International Best Track Archive)
    ibtracks_url = "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/"
    
    # Sample structure
    active_cyclones = [
        {
            'name': 'Cyclone Michaung',
            'center_lat': 13.5,
            'center_lon': 80.2,
            'radius_km': 300,
            'wind_speed_kmh': 120,
            'movement_direction': 315,  # Northwest
            'movement_speed_kmh': 15
        }
    ]
    
    return active_cyclones