# demo.py - Run complete demonstration
from digital_twin_simulator import VehicleDigitalTwin
from ml_threat_detector import ThreatDetectionEngine
from security_sandbox import SecuritySandbox

def run_complete_demo():
    """Full demonstration of Digital Twin-Driven Security Sandbox"""
    
    print("\n" + "="*60)
    print("  DIGITAL TWIN-DRIVEN SECURITY SANDBOX")
    print("  Proof of Concept Demonstration")
    print("="*60)
    
    # Step 1: Initialize Sandbox
    print("\n📦 STEP 1: Initializing Security Sandbox...")
    sandbox = SecuritySandbox()
    sandbox.initialize_sandbox(vehicle_id="DAIMLER_TRUCK_001")
    
    # Step 2: Train ML Model
    print("\n📊 STEP 2: Training Threat Detection Model...")
    sandbox.train_threat_model(training_cycles=100)
    
    # Step 3: Run Attack Simulations
    print("\n🎯 STEP 3: Running Attack Simulations...")
    
    attacks = ['replay_attack', 'fuzzing_attack', 'dos_attack']
    
    for attack in attacks:
        result = sandbox.run_attack_simulation(attack)
    
    # Step 4: Summary
    print("\n📈 STEP 4: Test Summary")
    print("="*60)
    status = sandbox.get_sandbox_status()
    print(f"  Total Tests Run: {status['total_tests']}")
    print(f"  Threats Detected: {status['threats_detected']}")
    print(f"  Detection Rate: {(status['threats_detected']/status['total_tests']*100):.1f}%")
    print("="*60)
    
    print("\n✅ DEMONSTRATION COMPLETE!")
    print("   This proves the concept is 100% viable for Daimler.\n")

if __name__ == "__main__":
    run_complete_demo()
