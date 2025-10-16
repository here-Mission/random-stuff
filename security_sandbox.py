# security_sandbox.py
from enum import Enum
from typing import Optional, Dict, List
import uuid
import time

from digital_twin_simulator import VehicleDigitalTwin
from ml_threat_detector import ThreatDetectionEngine

class SandboxStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    THREAT_DETECTED = "threat_detected"

class SecuritySandbox:
    """Isolated environment for safe threat testing"""
    
    def __init__(self, sandbox_id: Optional[str] = None):
        self.sandbox_id = sandbox_id or str(uuid.uuid4())
        self.status = SandboxStatus.IDLE
        self.digital_twin = None
        self.threat_detector = ThreatDetectionEngine()
        self.test_results = []
        
    def initialize_sandbox(self, vehicle_id: str):
        """Create digital twin in sandbox"""
        print(f"\n🔧 Initializing sandbox {self.sandbox_id[:8]}...")
        self.digital_twin = VehicleDigitalTwin(vehicle_id)
        self.status = SandboxStatus.IDLE
        print(f"✓ Digital twin created for vehicle {vehicle_id}")
        
    def train_threat_model(self, training_cycles: int = 100):
        """Train ML model on normal behavior"""
        print(f"\n🧠 Training threat detection model...")
        
        normal_samples = []
        for i in range(training_cycles):
            traffic = self.digital_twin.generate_normal_traffic()
            normal_samples.append(traffic)
            if (i + 1) % 20 == 0:
                print(f"   Training progress: {i+1}/{training_cycles}")
        
        self.threat_detector.train_baseline(normal_samples)
        
    def run_attack_simulation(self, attack_type: str) -> Dict:
        """Execute attack in sandbox and analyze"""
        print(f"\n🎯 Running {attack_type} simulation...")
        self.status = SandboxStatus.RUNNING
        
        normal_traffic = self.digital_twin.generate_normal_traffic()
        attack_traffic = self.digital_twin.inject_attack(attack_type)
        combined_traffic = normal_traffic + attack_traffic
        
        self.status = SandboxStatus.ANALYZING
        threat_result = self.threat_detector.detect_threat(combined_traffic)
        
        if threat_result['is_threat']:
            self.status = SandboxStatus.THREAT_DETECTED
        else:
            self.status = SandboxStatus.COMPLETE
        
        result = {
            'sandbox_id': self.sandbox_id,
            'attack_type': attack_type,
            'threat_detected': threat_result['is_threat'],
            'analysis': threat_result,
            'status': self.status.value,
            'vehicle_state': self.digital_twin.get_current_state()
        }
        
        self.test_results.append(result)
        self._print_results(result)
        
        return result
    
    def _print_results(self, result: Dict):
        """Pretty print test results"""
        print(f"\n{'='*60}")
        print(f"  SANDBOX ANALYSIS RESULTS")
        print(f"{'='*60}")
        print(f"  Attack Type: {result['attack_type']}")
        print(f"  Threat Detected: {'🚨 YES' if result['threat_detected'] else '✓ NO'}")
        print(f"  Threat Level: {result['analysis']['threat_level']}")
        print(f"  Confidence: {result['analysis']['confidence']:.2f}%")
        print(f"  Identified As: {result['analysis']['attack_type']}")
        print(f"  Anomaly Score: {result['analysis']['anomaly_score']:.4f}")
        print(f"{'='*60}\n")
    
    def get_sandbox_status(self) -> Dict:
        """Return current sandbox state"""
        return {
            'sandbox_id': self.sandbox_id,
            'status': self.status.value,
            'total_tests': len(self.test_results),
            'threats_detected': sum(1 for r in self.test_results if r['threat_detected'])
        }
