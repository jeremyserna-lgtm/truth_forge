#!/usr/bin/env python3
"""
Advanced Multi-Modal Biometric Training
========================================

Tier 2 & 3 biometric processing for Genesis training.

Combines:
- High-density EEG (16-64 channels) with coherence analysis
- fNIRS (brain blood oxygenation)
- Eye tracking + pupillometry
- Facial EMG (micro-expressions)
- Voice acoustic analysis
- Thermal imaging
- Respiratory-cardiac coherence

The more modalities that agree, the higher the training weight.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# TIER 2: ENHANCED SIGNALS
# =============================================================================

@dataclass
class HighDensityEEGMetrics:
    """16-64 channel EEG metrics with spatial information."""
    
    # Channel count
    n_channels: int
    
    # Band powers (averaged across regions)
    delta_power: float
    theta_power: float
    alpha_power: float
    beta_power: float
    gamma_power: float
    
    # Regional powers
    frontal_alpha: float
    parietal_alpha: float
    temporal_gamma: float
    occipital_alpha: float
    
    # Asymmetry (left - right)
    frontal_alpha_asymmetry: float  # Positive = more left (approach)
    parietal_alpha_asymmetry: float
    
    # Coherence metrics
    frontal_parietal_coherence: float
    interhemispheric_coherence: float
    global_coherence: float


@dataclass
class fNIRSMetrics:
    """Functional near-infrared spectroscopy metrics."""
    
    # Oxygenated hemoglobin changes by region
    dlpfc_oxy: float        # Dorsolateral prefrontal (executive)
    vmpfc_oxy: float        # Ventromedial prefrontal (emotion/value)
    motor_oxy: float        # Motor cortex
    parietal_oxy: float     # Parietal (spatial/attention)
    
    # Deoxygenated hemoglobin
    dlpfc_deoxy: float
    vmpfc_deoxy: float
    
    # Derived
    @property
    def prefrontal_laterality(self) -> float:
        """Left-right prefrontal difference."""
        return self.dlpfc_oxy  # Simplified
    
    @property
    def executive_engagement(self) -> float:
        """DLPFC activation level."""
        return max(0, self.dlpfc_oxy)
    
    @property
    def emotional_processing(self) -> float:
        """VMPFC activation level."""
        return max(0, self.vmpfc_oxy)


@dataclass
class EyeTrackingMetrics:
    """Eye tracking and pupillometry metrics."""
    
    # Pupil
    pupil_diameter_mm: float
    pupil_diameter_baseline: float
    pupil_dilation_percent: float
    
    # Blink
    blink_rate_per_min: float
    blink_duration_avg_ms: float
    
    # Gaze
    fixation_duration_avg_ms: float
    saccade_rate_per_sec: float
    gaze_entropy: float  # How scattered is attention
    
    # Microsaccades (tiny involuntary eye movements)
    microsaccade_rate: float
    
    @property
    def cognitive_load(self) -> float:
        """Composite cognitive load index."""
        # High load: dilated pupils, fewer blinks, longer fixations
        pupil_component = min(self.pupil_dilation_percent / 20, 1.0)
        blink_component = max(0, 1 - self.blink_rate_per_min / 20)
        fixation_component = min(self.fixation_duration_avg_ms / 500, 1.0)
        
        return (pupil_component + blink_component + fixation_component) / 3


@dataclass
class FacialEMGMetrics:
    """Facial electromyography metrics."""
    
    # Muscle activations (relative to baseline)
    corrugator: float       # Frown muscle (confusion, frustration)
    zygomaticus: float      # Smile muscle
    orbicularis_oculi: float  # Eye crinkle (genuine smile)
    frontalis: float        # Forehead (surprise, interest)
    masseter: float         # Jaw (tension)
    
    @property
    def genuine_positive(self) -> bool:
        """Duchenne smile = zygomaticus + orbicularis."""
        return self.zygomaticus > 1.2 and self.orbicularis_oculi > 1.1
    
    @property
    def frustration_signal(self) -> float:
        """Corrugator activation without positive signals."""
        if self.corrugator > 1.3 and self.zygomaticus < 1.0:
            return self.corrugator
        return 0.0
    
    @property
    def concentration_signal(self) -> float:
        """Moderate corrugator + frontalis."""
        if 1.1 < self.corrugator < 1.5 and self.frontalis > 1.1:
            return (self.corrugator + self.frontalis) / 2
        return 0.0


@dataclass
class VoiceAcousticMetrics:
    """Voice acoustic features for emotion detection."""
    
    # Pitch
    pitch_mean_hz: float
    pitch_std_hz: float
    pitch_range_hz: float
    
    # Energy
    energy_mean: float
    energy_std: float
    
    # Timing
    speaking_rate: float  # Syllables per second
    pause_ratio: float    # Proportion of silence
    
    # Voice quality
    jitter: float         # Pitch perturbation (stress indicator)
    shimmer: float        # Amplitude perturbation (stress indicator)
    
    # Spectral
    spectral_centroid: float
    
    @property
    def arousal(self) -> float:
        """Vocal arousal indicator."""
        pitch_component = min(self.pitch_mean_hz / 200, 1.0)
        energy_component = min(self.energy_mean * 10, 1.0)
        rate_component = min(self.speaking_rate / 5, 1.0)
        
        return (pitch_component + energy_component + rate_component) / 3
    
    @property
    def stress_index(self) -> float:
        """Jitter + shimmer indicate stress."""
        return min((self.jitter * 100 + self.shimmer * 10) / 2, 1.0)


@dataclass
class ThermalMetrics:
    """Facial thermal imaging metrics."""
    
    # Region temperatures (Celsius, change from baseline)
    forehead_delta: float       # Increases with mental effort
    periorbital_delta: float    # Decreases with cognitive load
    nasal_tip_delta: float      # Decreases with stress
    cheek_delta: float          # Varies with emotional arousal
    
    @property
    def cognitive_effort(self) -> float:
        """Forehead warming indicates effort."""
        return max(0, self.forehead_delta * 5)  # Scale 0.2°C change to 1.0
    
    @property
    def stress_index(self) -> float:
        """Nasal cooling indicates stress."""
        return max(0, -self.nasal_tip_delta * 5)
    
    @property
    def cognitive_load(self) -> float:
        """Periorbital cooling indicates load."""
        return max(0, -self.periorbital_delta * 5)


@dataclass
class RespirationMetrics:
    """Respiration metrics."""
    
    breath_rate: float           # Breaths per minute
    breath_depth: float          # Relative depth
    breath_regularity: float     # Coefficient of variation (lower = more regular)
    inspiration_expiration_ratio: float
    
    @property
    def relaxation_index(self) -> float:
        """Slow, deep, regular breathing = relaxed."""
        rate_component = max(0, 1 - (self.breath_rate - 6) / 12)  # Optimal ~6-12
        depth_component = min(self.breath_depth, 1.0)
        regularity_component = max(0, 1 - self.breath_regularity)
        
        return (rate_component + depth_component + regularity_component) / 3


# =============================================================================
# ADVANCED COGNITIVE STATE DETECTION
# =============================================================================

class AdvancedCognitiveDetector:
    """
    Detect cognitive state from multiple biometric modalities.
    
    Each modality provides evidence. When they agree, confidence is high.
    When they disagree, we note the uncertainty.
    """
    
    def __init__(self):
        self.modality_weights = {
            'eeg': 0.25,
            'fnirs': 0.20,
            'eye': 0.15,
            'cardiac': 0.15,
            'facial_emg': 0.10,
            'thermal': 0.10,
            'voice': 0.05,
        }
    
    def detect_from_eeg(self, eeg: HighDensityEEGMetrics) -> Dict[str, Any]:
        """Detect cognitive state from high-density EEG."""
        
        # Insight signature: gamma burst + alpha increase + high coherence
        insight_score = 0.0
        if eeg.temporal_gamma > 1.5:  # Right temporal gamma (insight)
            insight_score += 0.4
        if eeg.frontal_alpha > 1.2:  # Alpha relaxation before insight
            insight_score += 0.3
        if eeg.global_coherence > 0.6:  # Brain regions synchronizing
            insight_score += 0.3
        
        # Determine stage from band patterns
        if eeg.beta_power > 1.3 and eeg.alpha_power < 0.8:
            stage = 'analysis'
            confidence = 0.7
        elif eeg.theta_power > 1.2 and eeg.alpha_power > 1.0:
            stage = 'exploration'
            confidence = 0.65
        elif eeg.alpha_power > 1.3 and eeg.beta_power < 1.0:
            stage = 'synthesis' if insight_score > 0.5 else 'integration'
            confidence = 0.7
        else:
            stage = 'reception'
            confidence = 0.5
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': insight_score > 0.7,
            'insight_score': insight_score,
            'frontal_asymmetry': eeg.frontal_alpha_asymmetry,
        }
    
    def detect_from_fnirs(self, fnirs: fNIRSMetrics) -> Dict[str, Any]:
        """Detect cognitive state from fNIRS."""
        
        # High DLPFC = executive function active (analysis)
        # High VMPFC = emotional/value processing
        # Both high = integration
        
        dlpfc_active = fnirs.executive_engagement > 0.3
        vmpfc_active = fnirs.emotional_processing > 0.3
        
        if dlpfc_active and not vmpfc_active:
            stage = 'analysis'
            confidence = 0.75
        elif vmpfc_active and not dlpfc_active:
            stage = 'exploration'  # Emotional/intuitive
            confidence = 0.65
        elif dlpfc_active and vmpfc_active:
            stage = 'synthesis'
            confidence = 0.8
        else:
            stage = 'reception'
            confidence = 0.5
        
        # Insight: sudden increase in both regions
        is_breakthrough = (
            fnirs.executive_engagement > 0.5 and 
            fnirs.emotional_processing > 0.4
        )
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': is_breakthrough,
            'executive_engagement': fnirs.executive_engagement,
            'emotional_processing': fnirs.emotional_processing,
        }
    
    def detect_from_eyes(self, eye: EyeTrackingMetrics) -> Dict[str, Any]:
        """Detect cognitive state from eye metrics."""
        
        load = eye.cognitive_load
        
        # High load = deep processing
        if load > 0.7:
            stage = 'analysis'
            confidence = 0.6
        elif load > 0.4:
            stage = 'exploration'
            confidence = 0.55
        else:
            stage = 'reception'
            confidence = 0.5
        
        # Pupil dilation spike = potential insight
        is_breakthrough = eye.pupil_dilation_percent > 15
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': is_breakthrough,
            'cognitive_load': load,
            'pupil_dilation': eye.pupil_dilation_percent,
        }
    
    def detect_from_facial_emg(self, emg: FacialEMGMetrics) -> Dict[str, Any]:
        """Detect cognitive/emotional state from facial EMG."""
        
        # Frustration = high corrugator, low zygomaticus
        frustration = emg.frustration_signal
        
        # Concentration = moderate corrugator + frontalis
        concentration = emg.concentration_signal
        
        # Genuine positive = Duchenne smile
        positive = emg.genuine_positive
        
        if frustration > 0.5:
            stage = 'analysis'  # Stuck in analysis
            confidence = 0.6
            is_breakthrough = False
        elif positive:
            stage = 'synthesis'  # Insight satisfaction
            confidence = 0.7
            is_breakthrough = True
        elif concentration > 0.5:
            stage = 'analysis'
            confidence = 0.6
            is_breakthrough = False
        else:
            stage = 'reception'
            confidence = 0.4
            is_breakthrough = False
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': is_breakthrough,
            'frustration': frustration,
            'genuine_positive': positive,
        }
    
    def detect_from_thermal(self, thermal: ThermalMetrics) -> Dict[str, Any]:
        """Detect cognitive state from thermal imaging."""
        
        effort = thermal.cognitive_effort
        load = thermal.cognitive_load
        stress = thermal.stress_index
        
        if effort > 0.6 or load > 0.6:
            stage = 'analysis'
            confidence = 0.55
        elif stress > 0.5:
            stage = 'exploration'  # Stressed exploration
            confidence = 0.5
        else:
            stage = 'reception'
            confidence = 0.45
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': False,  # Thermal alone can't detect this
            'cognitive_effort': effort,
            'stress': stress,
        }
    
    def detect_from_voice(self, voice: VoiceAcousticMetrics) -> Dict[str, Any]:
        """Detect cognitive/emotional state from voice."""
        
        arousal = voice.arousal
        stress = voice.stress_index
        
        # High arousal might indicate breakthrough or frustration
        # Need other signals to disambiguate
        
        if arousal > 0.7:
            # Could be breakthrough or frustration
            stage = 'synthesis'  # Tentative
            confidence = 0.5
            is_breakthrough = stress < 0.3  # High arousal + low stress = insight
        elif arousal < 0.3:
            stage = 'reception'
            confidence = 0.5
            is_breakthrough = False
        else:
            stage = 'exploration'
            confidence = 0.45
            is_breakthrough = False
        
        return {
            'stage': stage,
            'confidence': confidence,
            'is_breakthrough': is_breakthrough,
            'arousal': arousal,
            'stress': stress,
        }
    
    def fuse_all_modalities(
        self,
        eeg_result: Optional[Dict] = None,
        fnirs_result: Optional[Dict] = None,
        eye_result: Optional[Dict] = None,
        cardiac_result: Optional[Dict] = None,
        facial_emg_result: Optional[Dict] = None,
        thermal_result: Optional[Dict] = None,
        voice_result: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Fuse predictions from all available modalities.
        
        Returns consensus prediction with confidence based on agreement.
        """
        results = {
            'eeg': eeg_result,
            'fnirs': fnirs_result,
            'eye': eye_result,
            'cardiac': cardiac_result,
            'facial_emg': facial_emg_result,
            'thermal': thermal_result,
            'voice': voice_result,
        }
        
        # Filter to available modalities
        available = {k: v for k, v in results.items() if v is not None}
        
        if not available:
            return {
                'stage': 'unknown',
                'confidence': 0.0,
                'is_breakthrough': False,
                'agreement': 0.0,
            }
        
        # Weighted voting for stage
        stage_votes = {}
        breakthrough_evidence = []
        
        for modality, result in available.items():
            weight = self.modality_weights.get(modality, 0.1)
            confidence = result.get('confidence', 0.5)
            
            stage = result.get('stage', 'unknown')
            if stage not in stage_votes:
                stage_votes[stage] = 0
            stage_votes[stage] += weight * confidence
            
            if result.get('is_breakthrough', False):
                breakthrough_evidence.append(weight * confidence)
        
        # Determine winning stage
        best_stage = max(stage_votes, key=stage_votes.get)
        total_weight = sum(stage_votes.values())
        stage_confidence = stage_votes[best_stage] / total_weight if total_weight > 0 else 0
        
        # Breakthrough consensus
        breakthrough_score = sum(breakthrough_evidence)
        is_breakthrough = breakthrough_score > 0.25
        
        # Agreement metric
        stages_predicted = [r.get('stage') for r in available.values()]
        agreement = stages_predicted.count(best_stage) / len(stages_predicted)
        
        # Compute training weight multiplier
        training_weight = self._compute_training_weight(
            stage_confidence, agreement, is_breakthrough, len(available)
        )
        
        return {
            'stage': best_stage,
            'confidence': stage_confidence,
            'is_breakthrough': is_breakthrough,
            'breakthrough_score': breakthrough_score,
            'agreement': agreement,
            'n_modalities': len(available),
            'training_weight': training_weight,
            'modality_predictions': available,
        }
    
    def _compute_training_weight(
        self,
        confidence: float,
        agreement: float,
        is_breakthrough: bool,
        n_modalities: int
    ) -> float:
        """
        Compute training weight multiplier based on signal quality.
        
        High agreement across many modalities = premium training signal.
        """
        base_weight = 1.0
        
        # Confidence bonus
        base_weight *= (0.5 + confidence)
        
        # Agreement bonus
        base_weight *= (0.7 + agreement * 0.6)
        
        # Multi-modal bonus
        modality_bonus = min(n_modalities / 5, 1.0)  # Up to 5 modalities
        base_weight *= (0.8 + modality_bonus * 0.4)
        
        # Breakthrough bonus (these are rare and valuable)
        if is_breakthrough and agreement > 0.6:
            base_weight *= 1.5
        
        return min(base_weight, 3.0)  # Cap at 3x


# =============================================================================
# ADVANCED BREAKTHROUGH DETECTION
# =============================================================================

class MultiModalBreakthroughDetector:
    """
    Detect genuine breakthrough moments using multiple modalities.
    
    A TRUE breakthrough shows convergent evidence across modalities:
    - EEG: Gamma burst, especially right temporal
    - fNIRS: Sudden DLPFC + VMPFC activation
    - Pupil: Rapid dilation
    - Facial EMG: Duchenne smile (zygomaticus + orbicularis)
    - HRV: Spike in variability
    - Voice: Pitch/energy increase
    
    Single-modality detection: confidence ~0.5
    Multi-modality convergence: confidence ~0.95
    """
    
    def __init__(self):
        self.modality_thresholds = {
            'eeg_gamma': 1.5,           # Multiple of baseline
            'fnirs_activation': 0.4,     # Normalized activation
            'pupil_dilation': 12,        # Percent change
            'hrv_spike': 15,             # ms change in RMSSD
            'facial_positive': True,     # Duchenne smile
            'voice_arousal': 0.6,        # Arousal index
        }
    
    def detect(
        self,
        eeg: Optional[HighDensityEEGMetrics] = None,
        fnirs: Optional[fNIRSMetrics] = None,
        eye: Optional[EyeTrackingMetrics] = None,
        hrv_delta: Optional[float] = None,
        facial_emg: Optional[FacialEMGMetrics] = None,
        voice: Optional[VoiceAcousticMetrics] = None,
    ) -> Dict[str, Any]:
        """
        Detect breakthrough with multi-modal evidence.
        """
        evidence = {}
        
        # EEG evidence
        if eeg is not None:
            eeg_gamma_high = eeg.temporal_gamma > self.modality_thresholds['eeg_gamma']
            eeg_coherence_high = eeg.global_coherence > 0.6
            evidence['eeg'] = {
                'triggered': eeg_gamma_high and eeg_coherence_high,
                'gamma_ratio': eeg.temporal_gamma,
                'coherence': eeg.global_coherence,
            }
        
        # fNIRS evidence
        if fnirs is not None:
            fnirs_active = (
                fnirs.executive_engagement > self.modality_thresholds['fnirs_activation'] and
                fnirs.emotional_processing > self.modality_thresholds['fnirs_activation'] * 0.8
            )
            evidence['fnirs'] = {
                'triggered': fnirs_active,
                'dlpfc': fnirs.executive_engagement,
                'vmpfc': fnirs.emotional_processing,
            }
        
        # Eye evidence
        if eye is not None:
            pupil_spike = eye.pupil_dilation_percent > self.modality_thresholds['pupil_dilation']
            evidence['eye'] = {
                'triggered': pupil_spike,
                'pupil_dilation': eye.pupil_dilation_percent,
            }
        
        # HRV evidence
        if hrv_delta is not None:
            hrv_spike = abs(hrv_delta) > self.modality_thresholds['hrv_spike']
            evidence['hrv'] = {
                'triggered': hrv_spike,
                'delta_ms': hrv_delta,
            }
        
        # Facial EMG evidence
        if facial_emg is not None:
            genuine_smile = facial_emg.genuine_positive
            evidence['facial'] = {
                'triggered': genuine_smile,
                'zygomaticus': facial_emg.zygomaticus,
                'orbicularis': facial_emg.orbicularis_oculi,
            }
        
        # Voice evidence
        if voice is not None:
            voice_aroused = voice.arousal > self.modality_thresholds['voice_arousal']
            voice_not_stressed = voice.stress_index < 0.4
            evidence['voice'] = {
                'triggered': voice_aroused and voice_not_stressed,
                'arousal': voice.arousal,
                'stress': voice.stress_index,
            }
        
        # Count evidence
        triggered_count = sum(1 for e in evidence.values() if e.get('triggered', False))
        total_modalities = len(evidence)
        
        # Compute confidence
        if total_modalities == 0:
            confidence = 0.0
            is_breakthrough = False
        else:
            evidence_ratio = triggered_count / total_modalities
            
            # Confidence scales with evidence ratio and number of modalities
            confidence = evidence_ratio * (0.5 + 0.1 * min(total_modalities, 5))
            is_breakthrough = confidence > 0.5
        
        # Determine signature type
        if triggered_count >= 4:
            signature = 'full_convergence'
        elif triggered_count >= 2:
            signature = 'partial_convergence'
        elif triggered_count == 1:
            signature = 'single_modality'
        else:
            signature = 'none'
        
        return {
            'is_breakthrough': is_breakthrough,
            'confidence': confidence,
            'signature': signature,
            'triggered_modalities': triggered_count,
            'total_modalities': total_modalities,
            'evidence': evidence,
            'training_weight': self._compute_breakthrough_weight(
                is_breakthrough, confidence, triggered_count
            ),
        }
    
    def _compute_breakthrough_weight(
        self,
        is_breakthrough: bool,
        confidence: float,
        triggered_count: int
    ) -> float:
        """Compute training weight for breakthrough examples."""
        if not is_breakthrough:
            return 1.0
        
        # Breakthroughs are valuable, multi-modal even more so
        base = 1.5
        
        # Confidence bonus
        base *= (1 + confidence)
        
        # Multi-modal bonus
        base *= (1 + triggered_count * 0.2)
        
        return min(base, 4.0)  # Cap at 4x for confirmed breakthroughs


# =============================================================================
# TRAINING EXAMPLE WITH ADVANCED BIOMETRICS
# =============================================================================

@dataclass
class AdvancedBiometricTrainingExample:
    """
    Training example with Tier 2/3 biometric data.
    """
    # Core
    text: str
    timestamp: datetime
    
    # Manual labels
    manual_cognitive_stage: str
    manual_emotion: str
    manual_is_breakthrough: bool
    manual_confidence: float
    
    # Tier 2 biometrics
    eeg: Optional[HighDensityEEGMetrics] = None
    eye: Optional[EyeTrackingMetrics] = None
    facial_emg: Optional[FacialEMGMetrics] = None
    respiration: Optional[RespirationMetrics] = None
    
    # Tier 3 biometrics
    fnirs: Optional[fNIRSMetrics] = None
    voice: Optional[VoiceAcousticMetrics] = None
    thermal: Optional[ThermalMetrics] = None
    
    # Cardiac (from any tier)
    ecg: Optional[Any] = None  # ECGMetrics from basic module
    hrv_delta: Optional[float] = None
    
    # Computed
    fused_result: Optional[Dict] = None
    breakthrough_result: Optional[Dict] = None
    
    def compute_advanced_labels(
        self,
        detector: AdvancedCognitiveDetector,
        breakthrough_detector: MultiModalBreakthroughDetector
    ):
        """Compute labels from all available biometrics."""
        
        # Modality-specific detections
        eeg_result = detector.detect_from_eeg(self.eeg) if self.eeg else None
        fnirs_result = detector.detect_from_fnirs(self.fnirs) if self.fnirs else None
        eye_result = detector.detect_from_eyes(self.eye) if self.eye else None
        facial_emg_result = detector.detect_from_facial_emg(self.facial_emg) if self.facial_emg else None
        thermal_result = detector.detect_from_thermal(self.thermal) if self.thermal else None
        voice_result = detector.detect_from_voice(self.voice) if self.voice else None
        
        # Fused prediction
        self.fused_result = detector.fuse_all_modalities(
            eeg_result=eeg_result,
            fnirs_result=fnirs_result,
            eye_result=eye_result,
            facial_emg_result=facial_emg_result,
            thermal_result=thermal_result,
            voice_result=voice_result,
        )
        
        # Breakthrough detection
        self.breakthrough_result = breakthrough_detector.detect(
            eeg=self.eeg,
            fnirs=self.fnirs,
            eye=self.eye,
            hrv_delta=self.hrv_delta,
            facial_emg=self.facial_emg,
            voice=self.voice,
        )
    
    def get_training_weight(self) -> float:
        """Get final training weight based on biometric confidence."""
        base_weight = 1.0
        
        # Fused result weight
        if self.fused_result:
            base_weight = self.fused_result.get('training_weight', 1.0)
        
        # Breakthrough bonus
        if self.breakthrough_result and self.breakthrough_result.get('is_breakthrough'):
            base_weight = max(
                base_weight,
                self.breakthrough_result.get('training_weight', 1.0)
            )
        
        return base_weight
    
    def to_training_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for training pipeline."""
        
        # Determine final labels (fused if available, else manual)
        if self.fused_result:
            cognitive_stage = self.fused_result.get('stage', self.manual_cognitive_stage)
            is_breakthrough = (
                self.breakthrough_result.get('is_breakthrough', False) 
                if self.breakthrough_result else self.manual_is_breakthrough
            )
            confidence = self.fused_result.get('confidence', self.manual_confidence)
        else:
            cognitive_stage = self.manual_cognitive_stage
            is_breakthrough = self.manual_is_breakthrough
            confidence = self.manual_confidence
        
        return {
            'text': self.text,
            'timestamp': self.timestamp.isoformat(),
            
            # Labels
            'cognitive_stage': cognitive_stage,
            'emotion': self.manual_emotion,
            'is_breakthrough': is_breakthrough,
            
            # Confidence and weight
            'confidence': confidence,
            'sample_weight': self.get_training_weight(),
            
            # Agreement metrics
            'biometric_agreement': self.fused_result.get('agreement', 0) if self.fused_result else 0,
            'n_modalities': self.fused_result.get('n_modalities', 0) if self.fused_result else 0,
            
            # Breakthrough details
            'breakthrough_signature': (
                self.breakthrough_result.get('signature', 'none')
                if self.breakthrough_result else 'none'
            ),
            'breakthrough_confidence': (
                self.breakthrough_result.get('confidence', 0)
                if self.breakthrough_result else 0
            ),
            
            # Provenance
            'label_source': 'advanced_biometric_fused',
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    """Demo of advanced biometric processing."""
    
    # Create sample metrics
    eeg = HighDensityEEGMetrics(
        n_channels=16,
        delta_power=1.0,
        theta_power=1.2,
        alpha_power=1.1,
        beta_power=0.9,
        gamma_power=1.8,  # Gamma burst!
        frontal_alpha=1.2,
        parietal_alpha=1.0,
        temporal_gamma=1.9,
        occipital_alpha=1.0,
        frontal_alpha_asymmetry=0.1,
        parietal_alpha_asymmetry=0.0,
        frontal_parietal_coherence=0.7,
        interhemispheric_coherence=0.6,
        global_coherence=0.65,
    )
    
    fnirs = fNIRSMetrics(
        dlpfc_oxy=0.5,
        vmpfc_oxy=0.4,
        motor_oxy=0.1,
        parietal_oxy=0.2,
        dlpfc_deoxy=-0.1,
        vmpfc_deoxy=-0.05,
    )
    
    eye = EyeTrackingMetrics(
        pupil_diameter_mm=4.5,
        pupil_diameter_baseline=3.8,
        pupil_dilation_percent=18.4,  # Significant dilation!
        blink_rate_per_min=12,
        blink_duration_avg_ms=150,
        fixation_duration_avg_ms=400,
        saccade_rate_per_sec=2.5,
        gaze_entropy=0.4,
        microsaccade_rate=1.2,
    )
    
    facial_emg = FacialEMGMetrics(
        corrugator=0.9,
        zygomaticus=1.4,       # Smiling!
        orbicularis_oculi=1.3,  # Genuine smile!
        frontalis=1.1,
        masseter=1.0,
    )
    
    # Run detection
    detector = AdvancedCognitiveDetector()
    breakthrough_detector = MultiModalBreakthroughDetector()
    
    # Create example
    example = AdvancedBiometricTrainingExample(
        text="I think I finally see how all the pieces connect...",
        timestamp=datetime.now(),
        manual_cognitive_stage="synthesis",
        manual_emotion="breakthrough",
        manual_is_breakthrough=True,
        manual_confidence=0.8,
        eeg=eeg,
        fnirs=fnirs,
        eye=eye,
        facial_emg=facial_emg,
        hrv_delta=22.0,  # HRV spike
    )
    
    example.compute_advanced_labels(detector, breakthrough_detector)
    
    # Output
    training_dict = example.to_training_dict()
    
    print("\n" + "="*60)
    print("ADVANCED BIOMETRIC TRAINING EXAMPLE")
    print("="*60)
    print(f"\nText: {training_dict['text']}")
    print(f"\nFused Stage: {training_dict['cognitive_stage']}")
    print(f"Is Breakthrough: {training_dict['is_breakthrough']}")
    print(f"Confidence: {training_dict['confidence']:.2f}")
    print(f"Training Weight: {training_dict['sample_weight']:.2f}x")
    print(f"\nBreakthrough Signature: {training_dict['breakthrough_signature']}")
    print(f"Breakthrough Confidence: {training_dict['breakthrough_confidence']:.2f}")
    print(f"Biometric Agreement: {training_dict['biometric_agreement']:.2f}")
    print(f"Modalities Used: {training_dict['n_modalities']}")
    
    if example.breakthrough_result:
        print("\nEvidence breakdown:")
        for mod, ev in example.breakthrough_result.get('evidence', {}).items():
            triggered = "✓" if ev.get('triggered') else "✗"
            print(f"  {mod}: {triggered}")


if __name__ == "__main__":
    main()
