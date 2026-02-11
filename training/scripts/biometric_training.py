#!/usr/bin/env python3
"""
Biometric Training Integration
==============================

Integrates physiological signals (ECG, EEG, GSR) into Genesis training.

Your body provides ground truth that's:
- Real-time (not retrospective)
- Involuntary (can't be faked)
- Subconscious (captures what you miss)

The model learns what YOUR neurons look like when they "get it".
"""

import json
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# SIGNAL DEFINITIONS
# =============================================================================

class EEGBand(Enum):
    """EEG frequency bands and their cognitive correlates."""
    DELTA = ("delta", 0.5, 4.0, "deep_processing")
    THETA = ("theta", 4.0, 8.0, "memory_creativity")
    ALPHA = ("alpha", 8.0, 13.0, "relaxed_awareness")
    BETA = ("beta", 13.0, 30.0, "active_thinking")
    GAMMA = ("gamma", 30.0, 100.0, "insight_binding")


@dataclass
class ECGMetrics:
    """Heart rate variability metrics from ECG."""
    heart_rate: float           # BPM
    rmssd: float                # Root mean square of successive differences (ms)
    sdnn: float                 # Standard deviation of NN intervals (ms)
    lf_power: float             # Low frequency power (0.04-0.15 Hz)
    hf_power: float             # High frequency power (0.15-0.4 Hz)
    lf_hf_ratio: float          # Sympathetic/parasympathetic balance
    
    @property
    def stress_index(self) -> float:
        """Higher = more stress. Based on LF/HF ratio."""
        return min(self.lf_hf_ratio / 2.0, 1.0)
    
    @property
    def relaxation_index(self) -> float:
        """Higher = more relaxed. Based on HF power and RMSSD."""
        return min(self.hf_power * self.rmssd / 1000, 1.0)


@dataclass
class EEGMetrics:
    """Frequency band powers and derived metrics from EEG."""
    delta_power: float
    theta_power: float
    alpha_power: float
    beta_power: float
    gamma_power: float
    
    # Derived
    alpha_theta_ratio: float = 0.0
    beta_alpha_ratio: float = 0.0
    frontal_asymmetry: float = 0.0  # Left-right difference (emotional valence)
    
    def __post_init__(self):
        if self.theta_power > 0:
            self.alpha_theta_ratio = self.alpha_power / self.theta_power
        if self.alpha_power > 0:
            self.beta_alpha_ratio = self.beta_power / self.alpha_power


@dataclass
class BiometricSnapshot:
    """A moment in time with all physiological signals."""
    timestamp: datetime
    ecg: ECGMetrics
    eeg: EEGMetrics
    gsr: float  # Galvanic skin response (µS)
    
    # Raw signals for detailed analysis
    ecg_raw: Optional[np.ndarray] = None  # 10s window
    eeg_raw: Optional[np.ndarray] = None  # 10s window, channels x samples


# =============================================================================
# COGNITIVE STATE DETECTION
# =============================================================================

@dataclass
class CognitiveSignature:
    """Expected physiological signature for a cognitive state."""
    theta: str  # "low", "moderate", "elevated"
    alpha: str
    beta: str
    gamma: str
    hrv_pattern: str  # "stable", "variable", "spike"


COGNITIVE_SIGNATURES: Dict[str, CognitiveSignature] = {
    "reception": CognitiveSignature(
        theta="low",
        alpha="high",  # Open, receptive
        beta="low",
        gamma="low",
        hrv_pattern="stable"
    ),
    "exploration": CognitiveSignature(
        theta="elevated",  # Memory search, curiosity
        alpha="moderate",
        beta="moderate",
        gamma="low",
        hrv_pattern="variable"
    ),
    "analysis": CognitiveSignature(
        theta="moderate",
        alpha="suppressed",  # Alpha blocking = focused attention
        beta="elevated",     # Active processing
        gamma="moderate",
        hrv_pattern="stable"
    ),
    "synthesis": CognitiveSignature(
        theta="elevated",
        alpha="elevated",    # Relaxed insight
        beta="moderate",
        gamma="bursts",      # Insight binding
        hrv_pattern="spike"  # Emotional arousal at insight
    ),
    "integration": CognitiveSignature(
        theta="moderate",
        alpha="high",        # Settled understanding
        beta="low",
        gamma="low",
        hrv_pattern="stable"
    ),
}


class CognitiveStateDetector:
    """
    Detect cognitive state from physiological signals.
    
    This is what makes biometric training powerful:
    your BODY tells us what cognitive state you're in,
    not just your verbal report.
    """
    
    def __init__(self, calibration_data: Optional[Dict] = None):
        """
        Calibration data = your personal baselines.
        Everyone's signals are different.
        """
        self.baselines = calibration_data or {}
    
    def calibrate(self, resting_data: List[BiometricSnapshot]):
        """
        Calibrate to YOUR personal baselines.
        
        Run this during relaxed, neutral state.
        """
        ecg_baselines = []
        eeg_baselines = []
        
        for snapshot in resting_data:
            ecg_baselines.append({
                'hr': snapshot.ecg.heart_rate,
                'rmssd': snapshot.ecg.rmssd,
                'lf_hf': snapshot.ecg.lf_hf_ratio,
            })
            eeg_baselines.append({
                'theta': snapshot.eeg.theta_power,
                'alpha': snapshot.eeg.alpha_power,
                'beta': snapshot.eeg.beta_power,
                'gamma': snapshot.eeg.gamma_power,
            })
        
        self.baselines = {
            'ecg': {k: np.mean([b[k] for b in ecg_baselines]) for k in ecg_baselines[0]},
            'eeg': {k: np.mean([b[k] for b in eeg_baselines]) for k in eeg_baselines[0]},
        }
        
        logger.info(f"Calibrated baselines: {self.baselines}")
    
    def detect_cognitive_stage(self, snapshot: BiometricSnapshot) -> Tuple[str, float]:
        """
        Detect cognitive stage from physiological signals.
        
        Returns: (stage_name, confidence)
        """
        if not self.baselines:
            logger.warning("Not calibrated - using default thresholds")
        
        # Compute relative changes from baseline
        eeg_relative = self._compute_eeg_relative(snapshot.eeg)
        hrv_pattern = self._detect_hrv_pattern(snapshot.ecg)
        
        # Score each cognitive state
        scores = {}
        for stage_name, signature in COGNITIVE_SIGNATURES.items():
            score = self._score_signature_match(eeg_relative, hrv_pattern, signature)
            scores[stage_name] = score
        
        # Return best match
        best_stage = max(scores, key=scores.get)
        confidence = scores[best_stage]
        
        return best_stage, confidence
    
    def _compute_eeg_relative(self, eeg: EEGMetrics) -> Dict[str, str]:
        """Compute relative EEG levels compared to baseline."""
        if 'eeg' not in self.baselines:
            return {'theta': 'moderate', 'alpha': 'moderate', 
                    'beta': 'moderate', 'gamma': 'low'}
        
        baseline = self.baselines['eeg']
        
        def level(current, base):
            ratio = current / (base + 1e-6)
            if ratio < 0.7:
                return "low"
            elif ratio < 1.3:
                return "moderate"
            else:
                return "elevated"
        
        return {
            'theta': level(eeg.theta_power, baseline['theta']),
            'alpha': level(eeg.alpha_power, baseline['alpha']),
            'beta': level(eeg.beta_power, baseline['beta']),
            'gamma': "bursts" if eeg.gamma_power > baseline['gamma'] * 2 else level(eeg.gamma_power, baseline['gamma']),
        }
    
    def _detect_hrv_pattern(self, ecg: ECGMetrics) -> str:
        """Detect HRV pattern from ECG."""
        if 'ecg' not in self.baselines:
            return "stable"
        
        baseline_rmssd = self.baselines['ecg']['rmssd']
        
        if ecg.rmssd > baseline_rmssd * 1.5:
            return "spike"
        elif ecg.rmssd > baseline_rmssd * 1.2 or ecg.rmssd < baseline_rmssd * 0.8:
            return "variable"
        else:
            return "stable"
    
    def _score_signature_match(
        self,
        eeg_relative: Dict[str, str],
        hrv_pattern: str,
        signature: CognitiveSignature
    ) -> float:
        """Score how well current state matches expected signature."""
        score = 0.0
        max_score = 5.0
        
        # EEG band matches
        if eeg_relative['theta'] == signature.theta:
            score += 1.0
        if eeg_relative['alpha'] == signature.alpha:
            score += 1.0
        if eeg_relative['beta'] == signature.beta:
            score += 1.0
        if eeg_relative['gamma'] == signature.gamma:
            score += 1.0
        
        # HRV pattern match
        if hrv_pattern == signature.hrv_pattern:
            score += 1.0
        
        return score / max_score


# =============================================================================
# BREAKTHROUGH DETECTION
# =============================================================================

class BreakthroughDetector:
    """
    Detect genuine breakthrough moments from physiology.
    
    A REAL breakthrough has a distinct, involuntary signature:
    - Gamma burst (40Hz+ oscillations, insight binding)
    - HRV spike (emotional arousal, autonomic response)
    - GSR increase (sympathetic activation, "electricity")
    - Followed by alpha increase (settling into understanding)
    
    This can't be faked. Your neurons either synchronize or they don't.
    """
    
    def __init__(
        self,
        gamma_threshold: float = 2.0,   # Multiple of baseline
        hrv_threshold: float = 15.0,     # ms change
        gsr_threshold: float = 0.2,      # µS change
    ):
        self.gamma_threshold = gamma_threshold
        self.hrv_threshold = hrv_threshold
        self.gsr_threshold = gsr_threshold
        self.baseline_gamma = None
        self.baseline_gsr = None
    
    def calibrate(self, resting_data: List[BiometricSnapshot]):
        """Set baseline from resting state."""
        self.baseline_gamma = np.mean([s.eeg.gamma_power for s in resting_data])
        self.baseline_gsr = np.mean([s.gsr for s in resting_data])
    
    def detect(
        self,
        current: BiometricSnapshot,
        previous: BiometricSnapshot
    ) -> Dict[str, Any]:
        """
        Detect if current moment is a genuine breakthrough.
        
        Returns detailed breakdown of physiological evidence.
        """
        # Gamma burst detection
        gamma_ratio = current.eeg.gamma_power / (self.baseline_gamma or 1.0)
        gamma_burst = gamma_ratio > self.gamma_threshold
        
        # HRV change detection
        hrv_delta = abs(current.ecg.rmssd - previous.ecg.rmssd)
        hrv_spike = hrv_delta > self.hrv_threshold
        
        # GSR change detection
        gsr_delta = current.gsr - (self.baseline_gsr or current.gsr)
        gsr_increase = gsr_delta > self.gsr_threshold
        
        # Combined scoring
        evidence_count = sum([gamma_burst, hrv_spike, gsr_increase])
        
        if evidence_count >= 3:
            # Full physiological confirmation
            return {
                'is_breakthrough': True,
                'confidence': 0.95,
                'evidence': 'full_signature',
                'details': {
                    'gamma_burst': gamma_burst,
                    'gamma_ratio': gamma_ratio,
                    'hrv_spike': hrv_spike,
                    'hrv_delta_ms': hrv_delta,
                    'gsr_increase': gsr_increase,
                    'gsr_delta_uS': gsr_delta,
                },
                'note': 'Genuine insight - neurologically confirmed'
            }
        
        elif evidence_count >= 2:
            return {
                'is_breakthrough': True,
                'confidence': 0.75,
                'evidence': 'partial_signature',
                'details': {
                    'gamma_burst': gamma_burst,
                    'hrv_spike': hrv_spike,
                    'gsr_increase': gsr_increase,
                },
                'note': 'Likely insight - partial physiological confirmation'
            }
        
        elif gamma_burst:
            # Gamma alone is significant
            return {
                'is_breakthrough': True,
                'confidence': 0.60,
                'evidence': 'gamma_only',
                'note': 'Possible insight - gamma activity detected'
            }
        
        return {
            'is_breakthrough': False,
            'confidence': 0.2,
            'evidence': 'none',
            'note': 'No physiological breakthrough signature'
        }


# =============================================================================
# EMOTION VERIFICATION
# =============================================================================

class EmotionVerifier:
    """
    Verify stated emotions against physiological signals.
    
    Your heart doesn't lie. When you say "I feel calm" but your
    HRV shows stress, the model should weight that label lower.
    """
    
    AROUSAL_EMOTIONS = {
        'excited', 'frustrated', 'anxious', 'breakthrough', 
        'angry', 'joyful', 'surprised'
    }
    
    CALM_EMOTIONS = {
        'calm', 'peaceful', 'reflective', 'neutral',
        'content', 'settled'
    }
    
    def verify(
        self,
        stated_emotion: str,
        ecg: ECGMetrics,
        baseline_ecg: ECGMetrics
    ) -> Dict[str, Any]:
        """
        Verify stated emotion against physiological signals.
        
        Returns authenticity score and details.
        """
        # Compute arousal from HRV
        hrv_change = abs(ecg.rmssd - baseline_ecg.rmssd) / baseline_ecg.rmssd
        stress_change = ecg.stress_index - 0.5  # Deviation from neutral
        
        physiological_arousal = hrv_change + abs(stress_change)
        
        stated_lower = stated_emotion.lower()
        
        if stated_lower in self.AROUSAL_EMOTIONS:
            # High arousal emotion - body should show it
            if physiological_arousal > 0.2:
                return {
                    'authentic': True,
                    'confidence': 0.9,
                    'match': 'congruent',
                    'note': 'Body confirms high arousal emotion'
                }
            else:
                return {
                    'authentic': False,
                    'confidence': 0.4,
                    'match': 'incongruent',
                    'note': 'Stated high arousal, body shows calm'
                }
        
        elif stated_lower in self.CALM_EMOTIONS:
            # Low arousal emotion - body should be stable
            if physiological_arousal < 0.15:
                return {
                    'authentic': True,
                    'confidence': 0.9,
                    'match': 'congruent',
                    'note': 'Body confirms calm state'
                }
            else:
                return {
                    'authentic': False,
                    'confidence': 0.5,
                    'match': 'incongruent',
                    'note': 'Stated calm, body shows arousal'
                }
        
        # Unknown emotion - neutral confidence
        return {
            'authentic': True,
            'confidence': 0.6,
            'match': 'unknown',
            'note': 'Emotion not in calibration set'
        }


# =============================================================================
# BIOMETRIC TRAINING EXAMPLE
# =============================================================================

@dataclass
class BiometricTrainingExample:
    """
    A training example with both manual and physiological ground truth.
    
    This is the key data structure for biometric training:
    your words + your body's signals = fused ground truth.
    """
    # Core data
    text: str
    timestamp: datetime
    
    # Manual labels (your conscious annotation)
    manual_cognitive_stage: str
    manual_emotion: str
    manual_is_breakthrough: bool
    manual_confidence: float
    
    # Physiological snapshot
    biometrics: BiometricSnapshot
    
    # Computed physiological labels
    physio_cognitive_stage: Optional[str] = None
    physio_cognitive_confidence: float = 0.0
    physio_is_breakthrough: bool = False
    physio_breakthrough_confidence: float = 0.0
    physio_emotion_authentic: bool = True
    
    # Fusion results
    fused_cognitive_stage: Optional[str] = None
    fused_is_breakthrough: Optional[bool] = None
    fused_confidence: float = 0.0
    
    def compute_fused_labels(
        self,
        cognitive_detector: CognitiveStateDetector,
        breakthrough_detector: BreakthroughDetector,
        emotion_verifier: EmotionVerifier,
        previous_biometrics: Optional[BiometricSnapshot] = None,
        baseline_ecg: Optional[ECGMetrics] = None
    ):
        """
        Compute physiological labels and fuse with manual labels.
        """
        # Detect cognitive stage from physiology
        self.physio_cognitive_stage, self.physio_cognitive_confidence = \
            cognitive_detector.detect_cognitive_stage(self.biometrics)
        
        # Detect breakthrough
        if previous_biometrics:
            breakthrough_result = breakthrough_detector.detect(
                self.biometrics, previous_biometrics
            )
            self.physio_is_breakthrough = breakthrough_result['is_breakthrough']
            self.physio_breakthrough_confidence = breakthrough_result['confidence']
        
        # Verify emotion
        if baseline_ecg:
            emotion_result = emotion_verifier.verify(
                self.manual_emotion,
                self.biometrics.ecg,
                baseline_ecg
            )
            self.physio_emotion_authentic = emotion_result['authentic']
        
        # Fuse labels
        self._fuse_labels()
    
    def _fuse_labels(self):
        """Fuse manual and physiological labels."""
        
        # Cognitive stage fusion
        if self.manual_cognitive_stage == self.physio_cognitive_stage:
            # Agreement - high confidence
            self.fused_cognitive_stage = self.manual_cognitive_stage
            self.fused_confidence = max(
                self.manual_confidence,
                self.physio_cognitive_confidence
            )
        elif self.physio_cognitive_confidence > 0.8:
            # Strong physio signal - trust body
            self.fused_cognitive_stage = self.physio_cognitive_stage
            self.fused_confidence = self.physio_cognitive_confidence * 0.9
        else:
            # Disagreement, neither strong - use manual with lower confidence
            self.fused_cognitive_stage = self.manual_cognitive_stage
            self.fused_confidence = self.manual_confidence * 0.7
        
        # Breakthrough fusion
        if self.manual_is_breakthrough == self.physio_is_breakthrough:
            self.fused_is_breakthrough = self.manual_is_breakthrough
        elif self.physio_is_breakthrough and self.physio_breakthrough_confidence > 0.7:
            # Body says breakthrough - trust it (can't fake gamma burst)
            self.fused_is_breakthrough = True
        else:
            self.fused_is_breakthrough = self.manual_is_breakthrough
    
    def to_training_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for training pipeline."""
        return {
            'text': self.text,
            'timestamp': self.timestamp.isoformat(),
            
            # Labels
            'cognitive_stage': self.fused_cognitive_stage or self.manual_cognitive_stage,
            'emotion': self.manual_emotion,
            'is_breakthrough': self.fused_is_breakthrough or self.manual_is_breakthrough,
            
            # Confidence weighting
            'confidence': self.fused_confidence,
            'emotion_authentic': self.physio_emotion_authentic,
            
            # Training weights
            'sample_weight': self._compute_sample_weight(),
            
            # Provenance
            'label_source': 'biometric_fused',
            'manual_physio_agreement': (
                self.manual_cognitive_stage == self.physio_cognitive_stage
            ),
        }
    
    def _compute_sample_weight(self) -> float:
        """
        Compute training weight for this example.
        
        High weight when:
        - Manual and physio agree
        - High confidence from both sources
        - Emotion verified as authentic
        """
        base_weight = 1.0
        
        # Agreement bonus
        if self.manual_cognitive_stage == self.physio_cognitive_stage:
            base_weight *= 1.5
        
        # Confidence multiplier
        base_weight *= (0.5 + self.fused_confidence)
        
        # Emotion authenticity
        if not self.physio_emotion_authentic:
            base_weight *= 0.7
        
        return min(base_weight, 3.0)  # Cap at 3x


# =============================================================================
# BIOMETRIC DATA COLLECTOR
# =============================================================================

class BiometricCollector:
    """
    Collect and sync biometric data during conversation.
    
    Integrates with:
    - Apple Watch (ECG, HRV)
    - Muse headband (EEG)
    - Oura ring (HRV, optional)
    - Custom GSR sensor (optional)
    """
    
    def __init__(self, output_dir: str = "data/biometric_sessions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session = None
        self.snapshots: List[BiometricSnapshot] = []
        self.messages: List[Dict] = []
    
    def start_session(self, session_name: Optional[str] = None):
        """Start a new biometric collection session."""
        self.current_session = session_name or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.snapshots = []
        self.messages = []
        logger.info(f"Started biometric session: {self.current_session}")
    
    def record_snapshot(
        self,
        ecg_metrics: ECGMetrics,
        eeg_metrics: EEGMetrics,
        gsr: float,
        ecg_raw: Optional[np.ndarray] = None,
        eeg_raw: Optional[np.ndarray] = None
    ):
        """Record a biometric snapshot (call ~1Hz during session)."""
        snapshot = BiometricSnapshot(
            timestamp=datetime.now(),
            ecg=ecg_metrics,
            eeg=eeg_metrics,
            gsr=gsr,
            ecg_raw=ecg_raw,
            eeg_raw=eeg_raw,
        )
        self.snapshots.append(snapshot)
    
    def record_message(
        self,
        text: str,
        role: str,
        manual_labels: Optional[Dict] = None
    ):
        """Record a conversation message with timestamp."""
        self.messages.append({
            'timestamp': datetime.now(),
            'text': text,
            'role': role,
            'manual_labels': manual_labels or {},
        })
    
    def get_snapshot_at_time(self, timestamp: datetime) -> Optional[BiometricSnapshot]:
        """Get the biometric snapshot closest to a timestamp."""
        if not self.snapshots:
            return None
        
        # Find closest snapshot
        closest = min(
            self.snapshots,
            key=lambda s: abs((s.timestamp - timestamp).total_seconds())
        )
        
        # Check it's within 5 seconds
        if abs((closest.timestamp - timestamp).total_seconds()) < 5:
            return closest
        
        return None
    
    def end_session(self) -> str:
        """End session and save data."""
        if not self.current_session:
            raise ValueError("No active session")
        
        session_path = self.output_dir / f"{self.current_session}.json"
        
        # Serialize (excluding raw arrays for JSON)
        session_data = {
            'session_id': self.current_session,
            'start_time': self.snapshots[0].timestamp.isoformat() if self.snapshots else None,
            'end_time': self.snapshots[-1].timestamp.isoformat() if self.snapshots else None,
            'num_snapshots': len(self.snapshots),
            'num_messages': len(self.messages),
            'messages': [
                {
                    'timestamp': m['timestamp'].isoformat(),
                    'text': m['text'],
                    'role': m['role'],
                    'manual_labels': m['manual_labels'],
                }
                for m in self.messages
            ],
            'snapshots': [
                {
                    'timestamp': s.timestamp.isoformat(),
                    'ecg': {
                        'heart_rate': s.ecg.heart_rate,
                        'rmssd': s.ecg.rmssd,
                        'sdnn': s.ecg.sdnn,
                        'lf_hf_ratio': s.ecg.lf_hf_ratio,
                    },
                    'eeg': {
                        'theta': s.eeg.theta_power,
                        'alpha': s.eeg.alpha_power,
                        'beta': s.eeg.beta_power,
                        'gamma': s.eeg.gamma_power,
                    },
                    'gsr': s.gsr,
                }
                for s in self.snapshots
            ],
        }
        
        with open(session_path, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Saved session to {session_path}")
        self.current_session = None
        
        return str(session_path)


# =============================================================================
# INTEGRATION WITH TRAINING PIPELINE
# =============================================================================

class BiometricTrainingPipeline:
    """
    Full pipeline for biometric-enhanced training.
    
    1. Collect conversations with biometric sensors
    2. Align messages with physiological snapshots
    3. Compute physiological labels
    4. Fuse with manual labels
    5. Generate training examples with confidence weights
    """
    
    def __init__(self):
        self.cognitive_detector = CognitiveStateDetector()
        self.breakthrough_detector = BreakthroughDetector()
        self.emotion_verifier = EmotionVerifier()
        
        self.calibrated = False
    
    def calibrate(self, resting_session_path: str):
        """Calibrate detectors from a resting baseline session."""
        with open(resting_session_path) as f:
            session_data = json.load(f)
        
        # Reconstruct snapshots
        snapshots = []
        for s in session_data['snapshots']:
            ecg = ECGMetrics(
                heart_rate=s['ecg']['heart_rate'],
                rmssd=s['ecg']['rmssd'],
                sdnn=s['ecg']['sdnn'],
                lf_power=0.0,
                hf_power=0.0,
                lf_hf_ratio=s['ecg']['lf_hf_ratio'],
            )
            eeg = EEGMetrics(
                delta_power=0.0,
                theta_power=s['eeg']['theta'],
                alpha_power=s['eeg']['alpha'],
                beta_power=s['eeg']['beta'],
                gamma_power=s['eeg']['gamma'],
            )
            snapshots.append(BiometricSnapshot(
                timestamp=datetime.fromisoformat(s['timestamp']),
                ecg=ecg,
                eeg=eeg,
                gsr=s['gsr'],
            ))
        
        # Calibrate all detectors
        self.cognitive_detector.calibrate(snapshots)
        self.breakthrough_detector.calibrate(snapshots)
        
        # Store baseline ECG for emotion verification
        self.baseline_ecg = ECGMetrics(
            heart_rate=np.mean([s.ecg.heart_rate for s in snapshots]),
            rmssd=np.mean([s.ecg.rmssd for s in snapshots]),
            sdnn=np.mean([s.ecg.sdnn for s in snapshots]),
            lf_power=0.0,
            hf_power=0.0,
            lf_hf_ratio=np.mean([s.ecg.lf_hf_ratio for s in snapshots]),
        )
        
        self.calibrated = True
        logger.info("Biometric pipeline calibrated")
    
    def process_session(self, session_path: str) -> List[BiometricTrainingExample]:
        """
        Process a biometric session into training examples.
        """
        if not self.calibrated:
            logger.warning("Pipeline not calibrated - using defaults")
        
        with open(session_path) as f:
            session_data = json.load(f)
        
        # Reconstruct data
        snapshots = self._reconstruct_snapshots(session_data['snapshots'])
        
        examples = []
        previous_snapshot = None
        
        for msg in session_data['messages']:
            if msg['role'] != 'user':
                continue  # Only train on your messages
            
            timestamp = datetime.fromisoformat(msg['timestamp'])
            
            # Find corresponding biometric snapshot
            snapshot = self._find_closest_snapshot(snapshots, timestamp)
            if not snapshot:
                continue
            
            # Create training example
            example = BiometricTrainingExample(
                text=msg['text'],
                timestamp=timestamp,
                manual_cognitive_stage=msg['manual_labels'].get('cognitive_stage', 'exploration'),
                manual_emotion=msg['manual_labels'].get('emotion', 'neutral'),
                manual_is_breakthrough=msg['manual_labels'].get('is_breakthrough', False),
                manual_confidence=msg['manual_labels'].get('confidence', 0.5),
                biometrics=snapshot,
            )
            
            # Compute physiological labels and fuse
            example.compute_fused_labels(
                cognitive_detector=self.cognitive_detector,
                breakthrough_detector=self.breakthrough_detector,
                emotion_verifier=self.emotion_verifier,
                previous_biometrics=previous_snapshot,
                baseline_ecg=self.baseline_ecg if self.calibrated else None,
            )
            
            examples.append(example)
            previous_snapshot = snapshot
        
        logger.info(f"Processed {len(examples)} biometric training examples")
        return examples
    
    def _reconstruct_snapshots(self, snapshot_data: List[Dict]) -> List[BiometricSnapshot]:
        """Reconstruct BiometricSnapshot objects from JSON."""
        snapshots = []
        for s in snapshot_data:
            ecg = ECGMetrics(
                heart_rate=s['ecg']['heart_rate'],
                rmssd=s['ecg']['rmssd'],
                sdnn=s['ecg']['sdnn'],
                lf_power=0.0,
                hf_power=0.0,
                lf_hf_ratio=s['ecg']['lf_hf_ratio'],
            )
            eeg = EEGMetrics(
                delta_power=0.0,
                theta_power=s['eeg']['theta'],
                alpha_power=s['eeg']['alpha'],
                beta_power=s['eeg']['beta'],
                gamma_power=s['eeg']['gamma'],
            )
            snapshots.append(BiometricSnapshot(
                timestamp=datetime.fromisoformat(s['timestamp']),
                ecg=ecg,
                eeg=eeg,
                gsr=s['gsr'],
            ))
        return snapshots
    
    def _find_closest_snapshot(
        self,
        snapshots: List[BiometricSnapshot],
        timestamp: datetime,
        max_delta_seconds: float = 5.0
    ) -> Optional[BiometricSnapshot]:
        """Find snapshot closest to timestamp."""
        if not snapshots:
            return None
        
        closest = min(
            snapshots,
            key=lambda s: abs((s.timestamp - timestamp).total_seconds())
        )
        
        if abs((closest.timestamp - timestamp).total_seconds()) <= max_delta_seconds:
            return closest
        
        return None
    
    def export_training_data(
        self,
        examples: List[BiometricTrainingExample],
        output_path: str
    ):
        """Export processed examples for training."""
        with open(output_path, 'w') as f:
            for example in examples:
                f.write(json.dumps(example.to_training_dict()) + '\n')
        
        logger.info(f"Exported {len(examples)} examples to {output_path}")


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Biometric Training Pipeline")
    parser.add_argument("command", choices=['calibrate', 'process', 'export'])
    parser.add_argument("--session", help="Session file path")
    parser.add_argument("--output", help="Output path")
    
    args = parser.parse_args()
    
    pipeline = BiometricTrainingPipeline()
    
    if args.command == 'calibrate':
        pipeline.calibrate(args.session)
    
    elif args.command == 'process':
        examples = pipeline.process_session(args.session)
        if args.output:
            pipeline.export_training_data(examples, args.output)


if __name__ == "__main__":
    main()
