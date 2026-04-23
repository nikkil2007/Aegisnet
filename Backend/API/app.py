# backend/api/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
sys.path.append('..')

from models.ensemble import EnsembleDriftModel
from models.risk_assessment import HazardDetector
from optimization.escape_routes import EscapeRouteOptimizer
from utils.data_fetch import fetch_ocean_currents, fetch_wind_data, fetch_tide_data

app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Initialize models
ensemble_model = EnsembleDriftModel(num_simulations=500)  # Reduce for speed
hazard_detector = HazardDetector()
route_optimizer = EscapeRouteOptimizer()

@app.route('/api/predict', methods=['POST'])
def predict_drift():
    """
    Main prediction endpoint
    
    Request body:
    {
        "lat": 12.5,
        "lon": 79.9,
        "vessel_type": "fishing_boat",
        "vessel_specs": {
            "max_speed": 15,
            "fuel_per_km": 0.5
        }
    }
    """
    data = request.json
    
    # Extract parameters
    lat = data['lat']
    lon = data['lon']
    vessel_type = data.get('vessel_type', 'fishing_boat')
    vessel_specs = data.get('vessel_specs', {
        'max_speed': 15,
        'fuel_per_km': 0.5
    })
    
    # Fetch environmental data
    ocean_data = fetch_ocean_currents(lat, lon, datetime.now())
    wind_data = fetch_wind_data(lat, lon, datetime.now())
    
    # Run ensemble prediction
    probability_cone = ensemble_model.predict_ensemble(
        lat, lon, 
        duration_hours=72,
        ocean_currents=ocean_data,
        wind_data=wind_data,
        vessel_type=vessel_type
    )
    
    # Extract most likely trajectory for hazard detection
    most_likely_trajectory = [
        (cone['most_likely'][0], cone['most_likely'][1], time)
        for time, cone in probability_cone.items()
    ]
    
    # Assess hazards
    hazards = hazard_detector.assess_all_hazards(
        most_likely_trajectory,
        datetime.now()
    )
    
    # If at risk, compute escape routes
    escape_routes = None
    if hazards['total_risk_score'] > 50:
        escape_routes = route_optimizer.compute_escape_routes(
            lat, lon,
            vessel_specs,
            hazards,
            ocean_data,
            wind_data
        )
    
    # Format response
    response = {
        'prediction': {
            'probability_cone': probability_cone,
            'most_likely_path': most_likely_trajectory
        },
        'hazards': hazards,
        'escape_routes': escape_routes,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(response)

@app.route('/api/hazards/current', methods=['GET'])
def get_current_hazards():
    """
    Get current hazards in a region (cyclones, high tides, etc.)
    """
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    radius_km = float(request.args.get('radius', 100))
    
    # This would fetch current hazards
    from utils.data_fetch import fetch_cyclone_data
    
    cyclones = fetch_cyclone_data()
    tide = fetch_tide_data(lat, lon, datetime.now())
    
    hazards = {
        'cyclones_nearby': [c for c in cyclones 
                           if hazard_detector.haversine_distance(
                               lat, lon, c['center_lat'], c['center_lon']
                           ) < radius_km],
        'tide_status': tide,
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(hazards)

@app.route('/api/navigation/update', methods=['POST'])
def navigation_update():
    """
    Real-time navigation guidance update
    
    Called every 5-10 minutes from mobile app
    """
    data = request.json
    
    current_lat = data['current_lat']
    current_lon = data['current_lon']
    planned_route = data['planned_route']  # Which route user selected
    
    # Recompute prediction from new position
    # Check if still on safe path
    # Provide course corrections if needed
    
    return jsonify({
        'status': 'on_course',
        'distance_to_safety': 12.5,
        'eta_minutes': 180,
        'next_update_minutes': 10
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)