"""
AEGISNET 2.0 - Complete Flask API
All features: location validation, route optimization, vessel learning
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.drift_model import DriftModel
from models.ensemble import EnsembleDriftModel
from models.risk_assessment import RiskAssessment
from models.vessel_learning import VesselSpeedLearner
from models.route_optimizer import RouteOptimizer
from utils.data_fetch import (
    fetch_ocean_currents, fetch_wind_data, fetch_tide_data, fetch_cyclone_data
)
from utils.location_validator import LocationValidator

app = Flask(__name__)
CORS(app)

# Initialize models
drift_model = DriftModel()
ensemble_model = EnsembleDriftModel(num_simulations=50)
risk_assessment = RiskAssessment()
route_optimizer = RouteOptimizer()
location_validator = LocationValidator()

# Store vessel learners per user
vessel_learners = {}

print("=" * 70)
print("🌊 AEGISNET 2.0 - Complete Ocean Decision Intelligence System")
print("=" * 70)
print("✅ Drift Model Ready")
print("✅ Risk Assessment Ready")
print("✅ Route Optimizer Ready")
print("✅ Location Validator Ready")
print("✅ Vessel Learning Ready")
print("🚀 Full System Online")
print("=" * 70)


@app.route('/')
def home():
    return jsonify({
        'name': 'AEGISNET 2.0 - Complete API',
        'version': '2.0.0',
        'status': 'running',
        'features': [
            'Drift prediction (ensemble)',
            'Multi-hazard risk assessment (6 types)',
            'Route optimization (3 options)',
            'Location validation (coastal waters only)',
            'Vessel learning (GPS-based)',
            'Engine status detection'
        ],
        'endpoints': {
            '/api/predict': 'POST - Full prediction with route optimization',
            '/api/validate-location': 'POST - Check if location is valid',
            '/api/vessel-status': 'POST - Get vessel learning status'
        }
    })


@app.route('/api/validate-location', methods=['POST'])
def validate_location():
    """
    Validate if location is in valid maritime zone
    """
    try:
        data = request.json
        lat = float(data.get('lat'))
        lon = float(data.get('lon'))
        
        validation = location_validator.validate_location(lat, lon)
        
        return jsonify(validation)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    COMPLETE PREDICTION ENDPOINT
    - Validates location
    - Runs drift prediction
    - Assesses all hazards
    - Computes escape routes if needed
    - Learns vessel characteristics
    """
    try:
        data = request.json
        
        lat = float(data.get('lat', 12.5))
        lon = float(data.get('lon', 79.9))
        duration_hours = float(data.get('duration_hours', 48))
        vessel_id = data.get('vessel_id', 'default')
        
        print(f"\n{'='*60}")
        print(f"📍 FULL PREDICTION REQUEST")
        print(f"   Position: {lat}°N, {lon}°E")
        print(f"   Vessel ID: {vessel_id}")
        print(f"{'='*60}")
        
        # STEP 1: Validate location
        print("STEP 1: Validating location...")
        validation = location_validator.validate_location(lat, lon)
        
        if not validation['valid']:
            print(f"❌ Invalid location: {validation['reason']}")
            return jsonify({
                'status': 'error',
                'error_type': 'invalid_location',
                'validation': validation
            }), 400
        
        print(f"✅ Valid location: {validation['region']}")
        print(f"   Distance from coast: {validation['distance_from_coast']:.1f} km")
        
        # STEP 2: Get or create vessel learner
        print("STEP 2: Vessel learning...")
        if vessel_id not in vessel_learners:
            vessel_learners[vessel_id] = VesselSpeedLearner()
        
        learner = vessel_learners[vessel_id]
        learner.add_gps_point(lat, lon, datetime.now())
        
        engine_on = learner.get_current_engine_status()
        vessel_speed = learner.get_vessel_speed()
        learning_status = learner.get_status_summary()
        
        print(f"   Engine status: {'ON' if engine_on else 'OFF'}")
        print(f"   Vessel speed: {vessel_speed:.1f} km/h")
        print(f"   Learning confidence: {learning_status['confidence']}")
        
        # STEP 3: Fetch environmental data
        print("STEP 3: Fetching environmental data...")
        ocean_currents = fetch_ocean_currents(lat, lon)
        wind_data = fetch_wind_data(lat, lon)
        
        print(f"   Ocean current: {ocean_currents['magnitude']:.2f} m/s @ {ocean_currents['direction']:.0f}°")
        print(f"   Wind: {wind_data['speed']:.2f} m/s @ {wind_data['direction']:.0f}°")
        
        # STEP 4: Run drift prediction
        print("STEP 4: Running drift model...")
        trajectory = drift_model.predict_drift(
            lat, lon, duration_hours,
            ocean_currents, wind_data,
            engine_on=engine_on
        )
        
        print(f"   ✅ Generated {len(trajectory)} trajectory points")
        
        # STEP 5: Assess all risks
        print("STEP 5: Assessing risks...")
        risks = risk_assessment.assess_all_risks(trajectory)
        
        print(f"   Total risk score: {risks['total_risk_score']}/100")
        
        detected_hazards = [k for k, v in risks.items() 
                           if isinstance(v, dict) and v.get('detected')]
        if detected_hazards:
            print(f"   ⚠️ Detected hazards: {', '.join(detected_hazards)}")
        else:
            print("   ✅ No hazards detected")
        
        # STEP 6: Compute escape routes if high risk
        escape_routes = None
        if risks['total_risk_score'] > 50:
            print("STEP 6: Computing escape routes...")
            escape_routes = route_optimizer.compute_escape_routes(
                lat, lon, vessel_speed, risks,
                ocean_currents, wind_data
            )
            print(f"   ✅ Generated 3 escape route options")
        else:
            print("STEP 6: Skipped (risk score < 50)")
        
        # STEP 7: Format response
        response = {
            'status': 'success',
            'location_validation': validation,
            'vessel_status': learning_status,
            'environmental_data': {
                'ocean_currents': ocean_currents,
                'wind': wind_data
            },
            'prediction': {
                'trajectory': [
                    {'lat': float(t[0]), 'lon': float(t[1]), 'time_hours': float(t[2])}
                    for t in trajectory[::4]
                ],
                'engine_on': engine_on,
                'total_points': len(trajectory)
            },
            'risks': risks,
            'escape_routes': escape_routes,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"{'='*60}")
        print("✅ PREDICTION COMPLETE")
        print(f"{'='*60}\n")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/vessel-status', methods=['POST'])
def vessel_status():
    """Get vessel learning status"""
    try:
        data = request.json
        vessel_id = data.get('vessel_id', 'default')
        
        if vessel_id in vessel_learners:
            status = vessel_learners[vessel_id].get_status_summary()
            return jsonify({'status': 'success', 'vessel_status': status})
        else:
            return jsonify({
                'status': 'success',
                'vessel_status': {
                    'total_points': 0,
                    'confidence': 'none',
                    'message': 'No GPS data collected yet'
                }
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n🌊 Starting AEGISNET 2.0 Complete Backend Server...")
    print("📡 API: http://localhost:5000\n")
    app.run(debug=True, host='0.0.0.0', port=5000)