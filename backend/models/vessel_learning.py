"""
Vessel speed learning from GPS data
Auto-detects engine status and learns actual boat speed
"""

import numpy as np
from datetime import datetime, timedelta


class VesselSpeedLearner:
    """
    Learns vessel characteristics from GPS data
    """
    
    def __init__(self):
        self.gps_history = []
        self.learned_speeds = {
            'engine_on': None,
            'engine_off': None,
            'confidence': 'low'
        }
    
    def add_gps_point(self, lat, lon, timestamp):
        """
        Add GPS reading to history
        """
        self.gps_history.append({
            'lat': lat,
            'lon': lon,
            'time': timestamp if isinstance(timestamp, datetime) else datetime.fromisoformat(timestamp)
        })
        
        # Keep only last 200 points
        if len(self.gps_history) > 200:
            self.gps_history = self.gps_history[-200:]
        
        # Learn after collecting enough data
        if len(self.gps_history) >= 20:
            self.learn_speeds()
    
    def calculate_speed_between_points(self, point1, point2):
        """
        Calculate speed in km/h between two GPS points
        """
        # Haversine distance
        lat1, lon1 = np.radians(point1['lat']), np.radians(point1['lon'])
        lat2, lon2 = np.radians(point2['lat']), np.radians(point2['lon'])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance_km = 6371 * c
        
        # Time difference in hours
        time_diff = (point2['time'] - point1['time']).total_seconds() / 3600
        
        if time_diff == 0 or time_diff > 1:  # Skip if >1 hour gap
            return None
        
        speed_kmh = distance_km / time_diff
        
        # Sanity check (fishing boats: 0-40 km/h)
        if speed_kmh < 0 or speed_kmh > 40:
            return None
        
        return speed_kmh
    
    def learn_speeds(self):
        """
        Analyze GPS history to learn actual speeds
        """
        speeds = []
        
        for i in range(len(self.gps_history) - 1):
            speed = self.calculate_speed_between_points(
                self.gps_history[i],
                self.gps_history[i + 1]
            )
            if speed is not None:
                speeds.append(speed)
        
        if len(speeds) < 10:
            return
        
        speeds = np.array(speeds)
        
        # Cluster into drifting vs motoring
        # Use k-means-like approach
        drifting_speeds = speeds[speeds < 4]   # < 4 km/h = drifting
        motoring_speeds = speeds[speeds > 8]   # > 8 km/h = engine on
        
        if len(drifting_speeds) >= 5:
            self.learned_speeds['engine_off'] = float(np.median(drifting_speeds))
        
        if len(motoring_speeds) >= 5:
            self.learned_speeds['engine_on'] = float(np.median(motoring_speeds))
            
            # Update confidence
            if len(motoring_speeds) >= 20:
                self.learned_speeds['confidence'] = 'high'
            elif len(motoring_speeds) >= 10:
                self.learned_speeds['confidence'] = 'medium'
    
    def get_current_engine_status(self):
        """
        Detect if engine is currently ON or OFF
        """
        if len(self.gps_history) < 2:
            return False  # Default: assume drifting
        
        # Check last few points
        recent_points = self.gps_history[-min(6, len(self.gps_history)):]
        
        if len(recent_points) < 2:
            return False
        
        recent_speed = self.calculate_speed_between_points(
            recent_points[-2],
            recent_points[-1]
        )
        
        if recent_speed is None:
            return False
        
        # Threshold detection
        if recent_speed < 3:
            return False  # Engine OFF (drifting)
        elif recent_speed > 8:
            return True   # Engine ON
        else:
            return False  # Uncertain, assume drifting (safer)
    
    def get_vessel_speed(self):
        """
        Get best estimate of vessel's engine speed
        """
        if self.learned_speeds['engine_on']:
            return self.learned_speeds['engine_on']
        else:
            return 15.0  # Default fishing boat speed
    
    def get_status_summary(self):
        """
        Get learning status summary
        """
        return {
            'total_points': len(self.gps_history),
            'learned_engine_speed': self.learned_speeds['engine_on'],
            'learned_drift_speed': self.learned_speeds['engine_off'],
            'confidence': self.learned_speeds['confidence'],
            'engine_currently_on': self.get_current_engine_status()
        }