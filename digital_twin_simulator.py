import random
import time
from dataclasses import dataclass
from typing import Dict, List
import json

@dataclass
class CANMessage:
    "Represents a CAN bus message from vehicle systems"
    message_id: str
    timestamp: float
    data: bytes
    source: str  # ECU source (engine, brake, steering, etc.)

class VehicleDigitalTwin:
    "Virtual replica of a Daimler truck's network"
    
    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id
        self.ecu_systems = ['engine', 'brake', 'transmission', 'steering', 'gateway']
        self.baseline_behavior = self._establish_baseline()
        
    def _establish_baseline(self) -> Dict:
        """Normal operating parameters for each ECU"""
        return {
            'engine': {'rpm_range': (600, 2500), 'temp_range': (80, 105), 'msg_frequency': 10},
            'brake': {'pressure_range': (0, 120), 'msg_frequency': 20},
            'transmission': {'gear_range': (1, 16), 'msg_frequency': 5},
            'steering': {'angle_range': (-540, 540), 'msg_frequency': 50},
            'gateway': {'msg_frequency': 100}
        }
    
    def generate_normal_traffic(self) -> List[CANMessage]:
        "Simulate normal CAN bus traffic"
        messages = []
        current_time = time.time()
        
        for ecu, params in self.baseline_behavior.items():
            # Generate messages based on frequency
            for _ in range(params['msg_frequency']):
                msg = CANMessage(
                    message_id=f"0x{random.randint(100, 999):03x}",
                    timestamp=current_time,
                    data=self._generate_normal_data(ecu, params),
                    source=ecu
                )
                messages.append(msg)
        
        return messages
    
    def _generate_normal_data(self, ecu: str, params: Dict) -> bytes:
        "Generate realistic data for each ECU"
        if ecu == 'engine':
            rpm = random.randint(*params['rpm_range'])
            temp = random.randint(*params['temp_range'])
            return rpm.to_bytes(2, 'big') + temp.to_bytes(1, 'big')
        elif ecu == 'brake':
            pressure = random.randint(*params['pressure_range'])
            return pressure.to_bytes(1, 'big')
        elif ecu == 'transmission':
            gear = random.randint(*params['gear_range'])
            return gear.to_bytes(1, 'big')
        elif ecu == 'steering':
            angle = random.randint(*params['angle_range'])
            return angle.to_bytes(2, 'big', signed=True)
        else:
            return random.randbytes(8)
    
    def inject_attack(self, attack_type: str) -> List[CANMessage]:
        "Simulate various attack patterns for testing"
        current_time = time.time()
        malicious_messages = []
        
        if attack_type == 'replay_attack':
            # Replay old brake messages (common attack)
            for _ in range(100):
                msg = CANMessage(
                    message_id="0x244", 
                    timestamp=current_time - 10, 
                    data=bytes([0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00]),
                    source='attacker'
                )
                malicious_messages.append(msg)
                
        elif attack_type == 'fuzzing_attack':
            # Send random malformed messages
            for _ in range(50):
                msg = CANMessage(
                    message_id=f"0x{random.randint(0, 0x7FF):03x}",
                    timestamp=current_time,
                    data=random.randbytes(8),
                    source='attacker'
                )
                malicious_messages.append(msg)
                
        elif attack_type == 'dos_attack':
            # Flood the bus with high-priority messages
            for _ in range(1000):
                msg = CANMessage(
                    message_id="0x000",  # Highest priority
                    timestamp=current_time,
                    data=bytes([0x00] * 8),
                    source='attacker'
                )
                malicious_messages.append(msg)
        
        return malicious_messages

    def get_current_state(self) -> Dict:
        """Return current digital twin state for visualization"""
        return {
            'vehicle_id': self.vehicle_id,
            'timestamp': time.time(),
            'ecu_status': {ecu: 'operational' for ecu in self.ecu_systems},
            'security_state': 'monitoring'
        }
