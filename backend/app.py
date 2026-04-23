"""
AEGISNET 2.0 - Main Flask API
Provides drift prediction and risk assessment endpoints
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.drift_model import DriftModel
from models.ensemble import EnsembleDriftModel
from models.risk_assessment import RiskAssessment
from utils.data_fetch import (
    fetch_ocean_currents,
    fetch_wind_data,
    fetch_tide_data,
    fetch_cyclone_data
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize models
drift_model = DriftModel()
ensemble_model = EnsembleDriftModel(num_simulations=50)  # Reduced for speed
risk_assessment = RiskAssessment()

print("=" * 60)
print("🌊 AEGISNET 2.0 - Ocean Decision Intelligence System")
print("=" * 60)
print("✅ Models initialized")
print("🚀 Server ready")
print("=" * 60)


@app.route('/')
def home():
    """API home page"""
    return jsonify({
        'name': 'AEGISNET 2.0 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            '/api/predict': 'POST - Drift prediction',
            '/api/test': 'GET - Test API',
            '/api/health': 'GET - Health check'
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})


@app.route('/api/test')
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'API is working!',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Request body:
    {
        "lat": 12.5,
        "lon": 79.9,
        "duration_hours": 48,
        "engine_on": false
    }
    """
    try:
        data = request.json
        
        # Extract parameters
        lat = float(data.get('lat', 12.5))
        lon = float(data.get('lon', 79.9))
        duration_hours = float(data.get('duration_hours', 48))
        engine_on = data.get('engine_on', False)
        
        print(f"\n📍 Prediction request:")
        print(f"   Position: {lat}°N, {lon}°E")
        print(f"   Duration: {duration_hours} hours")
        print(f"   Engine: {'ON' if engine_on else 'OFF'}")
        
        # Fetch environmental data
        print("   Fetching environmental data...")
        ocean_currents = fetch_ocean_currents(lat, lon)
        wind_data = fetch_wind_data(lat, lon)
        
        print(f"   Ocean current: {ocean_currents['magnitude']:.2f} m/s")
        print(f"   Wind speed: {wind_data['speed']:.2f} m/s")
        
        # Run drift prediction
        print("   Running drift model...")
        trajectory = drift_model.predict_drift(
            lat, lon,
            duration_hours,
            ocean_currents,
            wind_data,
            engine_on
        )
        
        # Assess risks
        print("   Assessing risks...")
        risks = risk_assessment.assess_all_risks(trajectory)
        
        print(f"   ✅ Risk score: {risks['total_risk_score']}/100")
        
        # Format response
        response = {
            'status': 'success',
            'input': {
                'lat': lat,
                'lon': lon,
                'duration_hours': duration_hours,
                'engine_on': engine_on
            },
            'environmental_data': {
                'ocean_currents': ocean_currents,
                'wind': wind_data
            },
            'prediction': {
                'trajectory': [
                    {
                        'lat': float(t[0]),
                        'lon': float(t[1]),
                        'time_hours': float(t[2])
                    }
                    for t in trajectory[::4]  # Sample every 4th point
                ],
                'total_points': len(trajectory)
            },
            'risks': risks,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/quick-test', methods=['GET'])
def quick_test():
    """Quick test with default parameters"""
    try:
        # Default: Rameswaram fisherman
        lat = 12.5
        lon = 79.9
        
        ocean_currents = fetch_ocean_currents(lat, lon)
        wind_data = fetch_wind_data(lat, lon)
        
        trajectory = drift_model.predict_drift(
            lat, lon,
            24,  # 24 hours
            ocean_currents,
            wind_data,
            engine_on=False
        )
        
        risks = risk_assessment.assess_all_risks(trajectory)
        
        return jsonify({
            'status': 'success',
            'message': 'Quick test successful',
            'start_position': {'lat': lat, 'lon': lon},
            'predicted_position_24h': {
                'lat': trajectory[-1][0],
                'lon': trajectory[-1][1]
            },
            'drift_distance_km': drift_model.haversine_distance(
                lat, lon,
                trajectory[-1][0], trajectory[-1][1]
            ),
            'risk_score': risks['total_risk_score'],
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    print("\n🌊 Starting AEGISNET 2.0 Backend Server...")
    print("📡 API will be available at: http://localhost:5000")
    print("\nTest endpoints:")
    print("  http://localhost:5000/")
    print("  http://localhost:5000/api/test")
    print("  http://localhost:5000/api/quick-test")
    print("\n" + "=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)