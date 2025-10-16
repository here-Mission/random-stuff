# api_server.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
from security_sandbox import SecuritySandbox

app = Flask(__name__)
CORS(app)

# Global sandbox instance
sandbox = None

@app.route('/api/sandbox/initialize', methods=['POST'])
def initialize_sandbox():
    global sandbox
    data = request.json
    vehicle_id = data.get('vehicle_id', 'TRUCK_001')
    
    sandbox = SecuritySandbox()
    sandbox.initialize_sandbox(vehicle_id)
    sandbox.train_threat_model(training_cycles=50)
    
    return jsonify({
        'success': True,
        'sandbox_id': sandbox.sandbox_id,
        'message': 'Sandbox initialized and trained'
    })

@app.route('/api/sandbox/status', methods=['GET'])
def get_status():
    if not sandbox:
        return jsonify({'error': 'Sandbox not initialized'}), 400
    
    return jsonify(sandbox.get_sandbox_status())

@app.route('/api/sandbox/simulate', methods=['POST'])
def run_simulation():
    if not sandbox:
        return jsonify({'error': 'Sandbox not initialized'}), 400
    
    data = request.json
    attack_type = data.get('attack_type', 'replay_attack')
    
    # Run simulation in background
    result = sandbox.run_attack_simulation(attack_type)
    
    return jsonify(result)

@app.route('/api/sandbox/results', methods=['GET'])
def get_results():
    if not sandbox:
        return jsonify({'error': 'Sandbox not initialized'}), 400
    
    return jsonify({
        'results': sandbox.test_results,
        'total': len(sandbox.test_results)
    })

if __name__ == '__main__':
    print("\n🚀 Digital Twin Security Sandbox API Server")
    print("=" * 60)
    app.run(debug=True, port=5000)
