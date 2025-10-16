import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import time
from typing import List, Dict
import sys
sys.path.append('.')

from digital_twin_simulator import CANMessage

class ThreatDetectionEngine:
    
    def __init__(self):
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.attack_classifier = RandomForestClassifier(
            n_estimators=200,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def extract_features(self, messages: List[CANMessage]) -> np.ndarray:
        "Convert CAN messages to ML features"
        features = []
        
        # Time-based features
        if len(messages) > 1:
            time_diffs = np.diff([m.timestamp for m in messages])
            avg_time_diff = np.mean(time_diffs)
            std_time_diff = np.std(time_diffs)
        else:
            avg_time_diff = 0
            std_time_diff = 0
        
        # Message frequency by source
        source_counts = {}
        for msg in messages:
            source_counts[msg.source] = source_counts.get(msg.source, 0) + 1
        
        # Message ID entropy (randomness indicator)
        message_ids = [msg.message_id for msg in messages]
        unique_ids = len(set(message_ids))
        id_entropy = unique_ids / len(messages) if messages else 0
        
        # Data payload statistics
        data_bytes = [byte for msg in messages for byte in msg.data]
        avg_byte_value = np.mean(data_bytes) if data_bytes else 0
        std_byte_value = np.std(data_bytes) if data_bytes else 0
        
        features = [
            len(messages),
            avg_time_diff,
            std_time_diff,
            id_entropy,
            avg_byte_value,
            std_byte_value,
            source_counts.get('attacker', 0),
            unique_ids
        ]
        
        return np.array(features).reshape(1, -1)
    
    def train_baseline(self, normal_traffic_samples: List[List[CANMessage]]):
        "Train on normal traffic patterns"
        X_train = []
        
        for traffic_sample in normal_traffic_samples:
            features = self.extract_features(traffic_sample)
            X_train.append(features.flatten())
        
        X_train = np.array(X_train)
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        self.anomaly_detector.fit(X_train_scaled)
        self.is_trained = True
        
        print(f"✓ Model trained on {len(normal_traffic_samples)} normal traffic samples")
    
    def detect_threat(self, messages: List[CANMessage]) -> Dict:
        "Analyze traffic for threats"
        if not self.is_trained:
            return {'error': 'Model not trained'}
        
        features = self.extract_features(messages)
        features_scaled = self.scaler.transform(features)
        
        anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
        is_anomaly = self.anomaly_detector.predict(features_scaled)[0] == -1
        
        threat_level = 'CRITICAL' if anomaly_score < -0.5 else \
                      'HIGH' if anomaly_score < -0.3 else \
                      'MEDIUM' if anomaly_score < -0.1 else \
                      'LOW'
        
        attack_type = self._identify_attack_type(messages, features)
        
        return {
            'is_threat': bool(is_anomaly),
            'threat_level': threat_level,
            'anomaly_score': float(anomaly_score),
            'attack_type': attack_type,
            'confidence': abs(anomaly_score) * 100,
            'timestamp': time.time(),
            'message_count': len(messages)
        }
    
    def _identify_attack_type(self, messages: List[CANMessage], 
                             features: np.ndarray) -> str:
        "Heuristic attack type identification"
        message_count = len(messages)
        source_attacker_count = sum(1 for m in messages if m.source == 'attacker')
        
        if message_count > 500:
            return 'DoS_Attack'
        elif source_attacker_count > 0 and message_count < 200:
            old_timestamps = sum(1 for m in messages if m.timestamp < time.time() - 5)
            if old_timestamps > message_count * 0.5:
                return 'Replay_Attack'
            else:
                return 'Fuzzing_Attack'
        else:
            return 'Unknown'
    
    def save_model(self, filepath: str):
        "Save trained model"
        model_data = {
            'anomaly_detector': self.anomaly_detector,
            'scaler': self.scaler,
            'is_trained': self.is_trained
        }
        joblib.dump(model_data, filepath)
        print(f"✓ Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        "Load pre-trained model"
        model_data = joblib.load(filepath)
        self.anomaly_detector = model_data['anomaly_detector']
        self.scaler = model_data['scaler']
        self.is_trained = model_data['is_trained']
        print(f"✓ Model loaded from {filepath}")
