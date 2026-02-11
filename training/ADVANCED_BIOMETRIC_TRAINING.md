# Advanced Biometric Training: Full Scope

## Tier Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BIOMETRIC TRAINING TIERS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  TIER 1: BASIC                 TIER 2: ENHANCED              TIER 3: ADVANCED│
│  ─────────────                 ────────────────              ────────────────│
│  • Apple Watch ECG             • Research EEG (32ch)         • fNIRS (brain blood)│
│  • Muse EEG (4ch)              • Multi-lead ECG              • Eye tracking    │
│  • ~$300                       • EMG (muscle)                • Facial EMG      │
│                                • Respiration belt            • Full-body motion│
│                                • ~$3,000                     • Pupillometry    │
│                                                              • Voice analysis  │
│                                                              • Thermal imaging │
│                                                              • ~$15,000+       │
│                                                                              │
│  Captures:                     Captures:                     Captures:        │
│  • Basic arousal               • Detailed brain states       • Cognitive load │
│  • Simple breakthrough         • Muscle tension              • Attention focus│
│  • HRV patterns                • Breathing patterns          • Micro-expressions│
│                                • Fine motor signals          • Subvocalization│
│                                                              • Blood oxygenation│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## TIER 2: ENHANCED BIOMETRIC TRAINING

### Hardware Stack

| Device | Signal | Cost | What It Captures |
|--------|--------|------|------------------|
| **OpenBCI Cyton + Daisy** | 16-channel EEG | $1,200 | Full cortical mapping |
| **Polar H10** | Research-grade ECG | $90 | Precise HRV, R-R intervals |
| **Shimmer3 GSR+** | GSR + PPG | $400 | Skin conductance, blood pulse |
| **Respiration Belt** | Breathing rate/depth | $150 | Respiratory patterns |
| **Myo Armband** (or EMG) | Forearm EMG | $200 | Typing tension, grip |
| **Tobii Eye Tracker 5** | Gaze + pupil | $230 | Attention, cognitive load |

**Total: ~$2,300**

### Enhanced Signal Processing

#### 1. High-Density EEG (16+ channels)

```
Channel Placement (10-20 System):
                    
                Fz
           F3   ●   F4
              ╲ │ ╱
        F7 ●───●───● F8
              ╱ │ ╲
           T3  Cz   T4
              ╲ │ ╱
        T5 ●───●───● T6
              ╱ │ ╲
           P3  Pz   P4
                ●
               Oz

Frontal (F): Executive function, decision-making
Central (C): Motor planning, action
Temporal (T): Language, memory
Parietal (P): Spatial processing, attention
Occipital (O): Visual processing
```

**What 16 channels adds over 4:**

| Metric | 4-Channel (Muse) | 16-Channel (OpenBCI) |
|--------|------------------|----------------------|
| Spatial resolution | Low | Medium-high |
| Source localization | No | Approximate |
| Hemispheric asymmetry | Basic | Detailed |
| Coherence analysis | Limited | Full |
| Artifact rejection | Difficult | Better |

#### 2. Coherence Analysis (Brain Region Communication)

```python
class CoherenceAnalyzer:
    """
    Measure how brain regions communicate during different cognitive states.
    
    High coherence = regions working together
    Low coherence = independent processing
    
    YOUR pattern: Which regions sync during YOUR insights?
    """
    
    def compute_coherence_matrix(self, eeg_data: np.ndarray, fs: int = 256):
        """
        Compute coherence between all channel pairs.
        
        Returns: (n_channels x n_channels x n_frequencies) matrix
        """
        n_channels = eeg_data.shape[0]
        n_freqs = 50  # 1-50 Hz
        
        coherence_matrix = np.zeros((n_channels, n_channels, n_freqs))
        
        for i in range(n_channels):
            for j in range(i+1, n_channels):
                # Cross-spectral density
                f, Cxy = signal.coherence(
                    eeg_data[i], eeg_data[j],
                    fs=fs, nperseg=fs*2
                )
                coherence_matrix[i, j, :len(Cxy)] = Cxy
                coherence_matrix[j, i, :len(Cxy)] = Cxy
        
        return coherence_matrix
    
    def extract_coherence_features(self, coherence_matrix: np.ndarray):
        """
        Extract training-relevant coherence features.
        """
        return {
            # Frontal-parietal coherence (executive attention)
            'frontal_parietal_theta': self._region_coherence(
                coherence_matrix, 'frontal', 'parietal', band='theta'
            ),
            
            # Interhemispheric coherence (integration)
            'interhemispheric_alpha': self._interhemispheric(
                coherence_matrix, band='alpha'
            ),
            
            # Global coherence (whole-brain synchrony)
            'global_gamma': np.mean(coherence_matrix[:, :, 30:50]),
            
            # Frontal asymmetry (emotional valence)
            'frontal_asymmetry': self._frontal_asymmetry(coherence_matrix),
        }
    
    def detect_insight_signature(self, coherence_features: dict) -> dict:
        """
        Detect insight from coherence patterns.
        
        Research shows insights characterized by:
        1. Sudden gamma burst in right temporal
        2. Preceding alpha increase (neural "blink")
        3. Increased long-range coherence
        """
        indicators = {
            'alpha_increase': coherence_features.get('global_alpha_change', 0) > 0.2,
            'gamma_burst': coherence_features.get('right_temporal_gamma', 0) > 1.5,
            'long_range_sync': coherence_features.get('frontal_parietal_theta', 0) > 0.6,
        }
        
        insight_score = sum(indicators.values()) / len(indicators)
        
        return {
            'is_insight': insight_score > 0.6,
            'confidence': insight_score,
            'indicators': indicators,
        }
```

#### 3. Respiratory-Cardiac Coherence

```python
class RespiratoryCardiacCoherence:
    """
    Measure coherence between breathing and heart rate.
    
    High coherence = regulated state, optimal for learning
    Low coherence = dysregulated, stressed
    
    Training signal: Examples from coherent states get higher weight
    """
    
    def compute_coherence(
        self,
        respiration: np.ndarray,  # Breathing signal
        rr_intervals: np.ndarray,  # Heart beat intervals
        fs: int = 4  # Samples per second
    ) -> float:
        """
        Compute respiratory-cardiac coherence.
        
        Returns coherence score 0-1.
        """
        # Resample to common rate
        resp_interp = self._resample(respiration, fs)
        hr_interp = self._resample(60000 / rr_intervals, fs)  # Convert to BPM
        
        # Compute coherence at respiratory frequency (0.1-0.4 Hz)
        f, Cxy = signal.coherence(resp_interp, hr_interp, fs=fs)
        
        # Find coherence in respiratory band
        resp_band = (f >= 0.1) & (f <= 0.4)
        coherence = np.max(Cxy[resp_band])
        
        return coherence
    
    def compute_training_weight(self, coherence: float) -> float:
        """
        Higher coherence = more regulated = better training signal.
        """
        if coherence > 0.8:
            return 1.5  # High coherence - premium examples
        elif coherence > 0.5:
            return 1.0  # Normal
        else:
            return 0.7  # Low coherence - might be noisy
```

#### 4. EMG for Cognitive Effort

```python
class CognitiveEffortFromEMG:
    """
    Detect cognitive effort from muscle tension.
    
    When you're thinking hard:
    - Forearm tension increases (even without typing)
    - Facial muscles (corrugator) contract (furrowed brow)
    - Jaw tension (masseter) increases
    
    This correlates with analysis vs synthesis stages.
    """
    
    def compute_effort_index(
        self,
        forearm_emg: np.ndarray,
        facial_emg: Optional[np.ndarray] = None
    ) -> dict:
        """
        Compute cognitive effort from EMG.
        """
        # RMS amplitude of EMG
        forearm_rms = np.sqrt(np.mean(forearm_emg ** 2))
        
        # Normalize to baseline
        effort_index = forearm_rms / self.baseline_forearm_rms
        
        result = {
            'effort_index': effort_index,
            'interpretation': self._interpret_effort(effort_index),
        }
        
        if facial_emg is not None:
            facial_rms = np.sqrt(np.mean(facial_emg ** 2))
            result['facial_tension'] = facial_rms / self.baseline_facial_rms
            result['furrowed_brow'] = result['facial_tension'] > 1.3
        
        return result
    
    def _interpret_effort(self, index: float) -> str:
        if index < 0.8:
            return "relaxed"  # Likely reception or integration
        elif index < 1.2:
            return "normal"
        elif index < 1.8:
            return "effortful"  # Likely analysis
        else:
            return "high_strain"  # Possibly frustrated
```

#### 5. Eye Tracking + Pupillometry

```python
class CognitiveLoadFromEyes:
    """
    Eyes reveal cognitive load and attention.
    
    Pupil dilation: Cognitive effort, arousal, interest
    Blink rate: Mental fatigue, processing depth
    Fixation patterns: Attention, comprehension
    
    This is one of the most reliable cognitive load measures.
    """
    
    def compute_cognitive_load(
        self,
        pupil_diameter: np.ndarray,  # mm, over time
        blink_timestamps: List[float],
        fixation_durations: List[float],
        baseline_pupil: float
    ) -> dict:
        """
        Compute cognitive load from eye metrics.
        """
        # Pupil dilation (Index of Cognitive Activity)
        mean_pupil = np.mean(pupil_diameter)
        pupil_change = (mean_pupil - baseline_pupil) / baseline_pupil
        
        # Blink rate (blinks per minute)
        duration_minutes = len(pupil_diameter) / (60 * 30)  # Assuming 30Hz
        blink_rate = len(blink_timestamps) / duration_minutes
        
        # Mean fixation duration
        mean_fixation = np.mean(fixation_durations) if fixation_durations else 0
        
        # Cognitive load composite
        # High load: dilated pupils, fewer blinks, longer fixations
        load_index = (
            0.4 * min(pupil_change * 5, 1.0) +  # Pupil contribution
            0.3 * max(0, 1 - blink_rate / 20) +  # Blink contribution (inverse)
            0.3 * min(mean_fixation / 500, 1.0)  # Fixation contribution
        )
        
        return {
            'cognitive_load': load_index,
            'pupil_change_percent': pupil_change * 100,
            'blink_rate_per_min': blink_rate,
            'mean_fixation_ms': mean_fixation,
            'interpretation': self._interpret_load(load_index),
        }
    
    def _interpret_load(self, load: float) -> str:
        if load < 0.3:
            return "low_load"  # Easy processing, possibly reception
        elif load < 0.6:
            return "moderate_load"  # Normal engagement
        elif load < 0.8:
            return "high_load"  # Deep analysis
        else:
            return "very_high_load"  # Possibly overwhelmed
    
    def detect_aha_moment(
        self,
        pupil_timeseries: np.ndarray,
        window_ms: int = 2000
    ) -> dict:
        """
        Detect "aha" moments from pupil dynamics.
        
        Research shows: sudden pupil dilation spike during insight.
        """
        # Compute derivative (rate of change)
        pupil_derivative = np.diff(pupil_timeseries)
        
        # Find sudden increases
        threshold = np.std(pupil_derivative) * 2.5
        spikes = np.where(pupil_derivative > threshold)[0]
        
        if len(spikes) > 0:
            return {
                'aha_detected': True,
                'spike_magnitude': float(np.max(pupil_derivative[spikes])),
                'spike_times': spikes.tolist(),
            }
        
        return {'aha_detected': False}
```

### Enhanced Training Integration

```python
@dataclass
class EnhancedBiometricSnapshot:
    """Tier 2: Enhanced biometric snapshot with all signals."""
    
    timestamp: datetime
    
    # Core signals (from Tier 1)
    ecg: ECGMetrics
    eeg: EEGMetrics  # Now 16 channels
    gsr: float
    
    # Enhanced signals
    eeg_coherence: Dict[str, float]  # Inter-region coherence
    respiration: RespirationMetrics
    respiratory_cardiac_coherence: float
    emg_effort: Dict[str, float]
    eye_metrics: Dict[str, float]
    
    def to_training_features(self) -> Dict[str, float]:
        """Extract all features for training."""
        features = {}
        
        # EEG features
        features['theta_power'] = self.eeg.theta_power
        features['alpha_power'] = self.eeg.alpha_power
        features['beta_power'] = self.eeg.beta_power
        features['gamma_power'] = self.eeg.gamma_power
        features['frontal_parietal_coherence'] = self.eeg_coherence.get('frontal_parietal', 0)
        features['interhemispheric_coherence'] = self.eeg_coherence.get('interhemispheric', 0)
        
        # Cardiac features
        features['heart_rate'] = self.ecg.heart_rate
        features['hrv_rmssd'] = self.ecg.rmssd
        features['lf_hf_ratio'] = self.ecg.lf_hf_ratio
        
        # Respiratory-cardiac
        features['resp_cardiac_coherence'] = self.respiratory_cardiac_coherence
        
        # Effort/load
        features['emg_effort'] = self.emg_effort.get('effort_index', 0)
        features['cognitive_load'] = self.eye_metrics.get('cognitive_load', 0)
        features['pupil_change'] = self.eye_metrics.get('pupil_change_percent', 0)
        
        # GSR
        features['gsr'] = self.gsr
        
        return features
```

---

## TIER 3: ADVANCED BIOMETRIC TRAINING

### Hardware Stack

| Device | Signal | Cost | What It Captures |
|--------|--------|------|------------------|
| **fNIRS System** | Brain blood oxygenation | $8,000+ | Prefrontal activity |
| **High-density EEG (64ch)** | Full cortical EEG | $3,000+ | Precise source localization |
| **Facial EMG Array** | Micro-expressions | $1,500 | Subconscious emotions |
| **Voice Analysis Mic** | Acoustic features | $200 | Emotional prosody |
| **Thermal Camera** | Facial temperature | $2,000 | Stress, cognitive effort |
| **Full-body Motion Capture** | Posture, gestures | $500+ | Embodied cognition |
| **High-speed Eye Tracker** | 1000Hz eye tracking | $3,000 | Microsaccades |

**Total: ~$18,000+**

### Advanced Signal Processing

#### 1. fNIRS (Functional Near-Infrared Spectroscopy)

```python
class fNIRSProcessor:
    """
    fNIRS measures blood oxygenation changes in the brain.
    
    Unlike EEG (electrical), fNIRS measures metabolic activity.
    When brain regions work, they need oxygen → blood flow increases.
    
    Prefrontal cortex activity = executive function, decision-making
    
    This directly measures WHICH brain regions activate during your insights.
    """
    
    def __init__(self, n_channels: int = 16):
        self.n_channels = n_channels
        self.baseline_oxy = None
        self.baseline_deoxy = None
    
    def process_raw(
        self,
        raw_data: np.ndarray,  # (n_channels, n_timepoints)
        wavelengths: Tuple[int, int] = (760, 850)  # nm
    ) -> Dict[str, np.ndarray]:
        """
        Convert raw optical density to oxy/deoxy hemoglobin.
        
        Uses Modified Beer-Lambert Law.
        """
        # Separate wavelengths
        od_760 = raw_data[0::2]  # Odd channels
        od_850 = raw_data[1::2]  # Even channels
        
        # Convert to concentration changes (simplified)
        # Real implementation uses extinction coefficients
        delta_oxy = 0.5 * (od_850 - od_760)
        delta_deoxy = 0.5 * (od_760 - od_850)
        
        return {
            'oxy_hb': delta_oxy,      # Oxygenated hemoglobin
            'deoxy_hb': delta_deoxy,  # Deoxygenated hemoglobin
            'total_hb': delta_oxy + delta_deoxy,
        }
    
    def compute_prefrontal_activation(
        self,
        oxy_hb: np.ndarray,
        region: str = 'dlpfc'  # Dorsolateral prefrontal cortex
    ) -> Dict[str, float]:
        """
        Compute prefrontal cortex activation.
        
        DLPFC: Working memory, executive function, planning
        VMPFC: Emotional regulation, value-based decisions
        """
        # Channel mapping (depends on optode placement)
        region_channels = {
            'dlpfc': [0, 1, 2, 3],      # Lateral frontal
            'vmpfc': [4, 5],             # Medial frontal
            'motor': [6, 7, 8, 9],       # Motor cortex
        }
        
        channels = region_channels.get(region, [0, 1])
        region_activation = np.mean(oxy_hb[channels])
        
        return {
            'region': region,
            'activation': float(region_activation),
            'interpretation': self._interpret_activation(region, region_activation),
        }
    
    def detect_cognitive_state_from_fnirs(
        self,
        oxy_hb: np.ndarray,
        deoxy_hb: np.ndarray
    ) -> Dict[str, Any]:
        """
        Detect cognitive state from blood oxygenation patterns.
        """
        dlpfc = self.compute_prefrontal_activation(oxy_hb, 'dlpfc')
        vmpfc = self.compute_prefrontal_activation(oxy_hb, 'vmpfc')
        
        # High DLPFC + low VMPFC = analytical thinking
        # High VMPFC + moderate DLPFC = emotional processing
        # Both high = integration
        
        if dlpfc['activation'] > 0.5 and vmpfc['activation'] < 0.3:
            return {'state': 'analysis', 'confidence': 0.8}
        elif vmpfc['activation'] > 0.5 and dlpfc['activation'] < 0.5:
            return {'state': 'emotional_processing', 'confidence': 0.7}
        elif dlpfc['activation'] > 0.4 and vmpfc['activation'] > 0.4:
            return {'state': 'integration', 'confidence': 0.75}
        else:
            return {'state': 'reception', 'confidence': 0.6}
    
    def _interpret_activation(self, region: str, activation: float) -> str:
        if activation > 0.5:
            return f"{region}_highly_active"
        elif activation > 0.2:
            return f"{region}_moderately_active"
        else:
            return f"{region}_baseline"
```

#### 2. Facial EMG for Micro-Expressions

```python
class FacialEMGProcessor:
    """
    Facial muscles reveal emotions before you're aware of them.
    
    Key muscles:
    - Corrugator supercilii: Frown (confusion, frustration)
    - Zygomaticus major: Smile (genuine pleasure, insight satisfaction)
    - Orbicularis oculi: Eye crinkle (genuine smile vs fake)
    - Frontalis: Raised eyebrows (surprise, interest)
    
    These micro-contractions happen in ~200ms - before conscious awareness.
    """
    
    MUSCLE_EMOTION_MAP = {
        'corrugator': {
            'high': ['frustration', 'confusion', 'concentration'],
            'low': ['ease', 'understanding'],
        },
        'zygomaticus': {
            'high': ['joy', 'insight_satisfaction', 'amusement'],
            'low': ['neutral', 'negative'],
        },
        'orbicularis_oculi': {
            'high': ['genuine_positive', 'authentic_smile'],
            'low': ['social_smile', 'neutral'],
        },
        'frontalis': {
            'high': ['surprise', 'interest', 'attention'],
            'low': ['neutral', 'bored'],
        },
    }
    
    def process_emg(
        self,
        emg_signals: Dict[str, np.ndarray],  # muscle_name: signal
        fs: int = 1000  # EMG typically 1kHz
    ) -> Dict[str, Dict]:
        """
        Process facial EMG signals.
        """
        results = {}
        
        for muscle, signal in emg_signals.items():
            # Rectify and smooth
            rectified = np.abs(signal)
            smoothed = self._moving_average(rectified, window=int(fs * 0.1))
            
            # Compute activation relative to baseline
            activation = np.mean(smoothed) / self.baselines.get(muscle, 1.0)
            
            results[muscle] = {
                'activation': activation,
                'interpretation': self._interpret_muscle(muscle, activation),
            }
        
        return results
    
    def detect_micro_expression(
        self,
        emg_timeseries: Dict[str, np.ndarray],
        fs: int = 1000
    ) -> List[Dict]:
        """
        Detect micro-expressions (< 500ms muscle activations).
        """
        micro_expressions = []
        
        for muscle, signal in emg_timeseries.items():
            rectified = np.abs(signal)
            
            # Find transient activations
            threshold = np.mean(rectified) + 2 * np.std(rectified)
            above_threshold = rectified > threshold
            
            # Find contiguous regions
            regions = self._find_regions(above_threshold)
            
            for start, end in regions:
                duration_ms = (end - start) / fs * 1000
                if 50 < duration_ms < 500:  # Micro-expression range
                    micro_expressions.append({
                        'muscle': muscle,
                        'start_ms': start / fs * 1000,
                        'duration_ms': duration_ms,
                        'intensity': float(np.max(rectified[start:end])),
                        'likely_emotion': self._infer_emotion(muscle),
                    })
        
        return micro_expressions
    
    def compute_emotion_authenticity(
        self,
        stated_emotion: str,
        facial_emg: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Verify if stated emotion matches facial muscle activity.
        
        Key insight: Genuine smile = zygomaticus + orbicularis_oculi
                    Fake smile = zygomaticus only
        """
        if 'positive' in stated_emotion or 'happy' in stated_emotion:
            zygo_active = facial_emg.get('zygomaticus', {}).get('activation', 0) > 1.2
            orbi_active = facial_emg.get('orbicularis_oculi', {}).get('activation', 0) > 1.1
            
            if zygo_active and orbi_active:
                return {'authentic': True, 'type': 'duchenne_smile', 'confidence': 0.9}
            elif zygo_active and not orbi_active:
                return {'authentic': False, 'type': 'social_smile', 'confidence': 0.7}
        
        # Add more emotion-specific checks...
        return {'authentic': True, 'confidence': 0.5}
```

#### 3. Voice Analysis (Acoustic Emotional Features)

```python
class VoiceEmotionAnalyzer:
    """
    Voice carries emotional information independent of words.
    
    Acoustic features that reveal emotional state:
    - Pitch (F0): Higher = aroused/stressed, Lower = calm/sad
    - Pitch variability: More = expressive/engaged, Less = flat/depressed
    - Speaking rate: Faster = excited/anxious, Slower = thoughtful/sad
    - Voice quality: Jitter, shimmer indicate stress
    - Formants: Vowel shapes change with emotion
    
    For text-based training: Could analyze voice memos or thinking-aloud sessions.
    """
    
    def extract_acoustic_features(
        self,
        audio: np.ndarray,
        sr: int = 16000
    ) -> Dict[str, float]:
        """
        Extract emotion-relevant acoustic features.
        """
        import librosa  # Audio processing library
        
        features = {}
        
        # Pitch (F0)
        pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
        pitch_values = pitches[pitches > 0]
        if len(pitch_values) > 0:
            features['pitch_mean'] = float(np.mean(pitch_values))
            features['pitch_std'] = float(np.std(pitch_values))
            features['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))
        
        # Energy/loudness
        rms = librosa.feature.rms(y=audio)[0]
        features['energy_mean'] = float(np.mean(rms))
        features['energy_std'] = float(np.std(rms))
        
        # Speaking rate (via onset detection)
        onsets = librosa.onset.onset_detect(y=audio, sr=sr)
        duration_sec = len(audio) / sr
        features['syllable_rate'] = len(onsets) / duration_sec
        
        # Spectral features (voice quality)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features['spectral_centroid'] = float(np.mean(spectral_centroid))
        
        # MFCCs (general voice characteristics)
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f'mfcc_{i}'] = float(np.mean(mfccs[i]))
        
        return features
    
    def classify_emotional_state(
        self,
        acoustic_features: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Classify emotional state from acoustic features.
        """
        # Arousal (activation level)
        arousal_indicators = [
            acoustic_features.get('pitch_mean', 0) > 150,  # Hz
            acoustic_features.get('pitch_std', 0) > 30,
            acoustic_features.get('syllable_rate', 0) > 4,
            acoustic_features.get('energy_mean', 0) > 0.1,
        ]
        arousal = sum(arousal_indicators) / len(arousal_indicators)
        
        # Valence (positive/negative) - harder from voice alone
        valence_indicators = [
            acoustic_features.get('pitch_range', 0) > 100,  # Expressive
            acoustic_features.get('pitch_mean', 0) > 120,   # Not monotone
        ]
        valence = sum(valence_indicators) / len(valence_indicators)
        
        return {
            'arousal': arousal,  # 0 = calm, 1 = activated
            'valence': valence,  # 0 = negative, 1 = positive
            'engagement': (arousal + valence) / 2,
        }
    
    def detect_insight_moment(
        self,
        audio_segment: np.ndarray,
        sr: int = 16000
    ) -> Dict[str, Any]:
        """
        Detect potential insight from voice pattern.
        
        Insight signature in voice:
        - Sudden pitch rise ("Aha!")
        - Increased energy
        - Pause before (processing) and after (savoring)
        """
        # Segment into frames
        frame_length = int(sr * 0.1)  # 100ms frames
        
        pitches = []
        energies = []
        
        for i in range(0, len(audio_segment) - frame_length, frame_length // 2):
            frame = audio_segment[i:i + frame_length]
            
            # Pitch
            pitches_frame, _ = librosa.piptrack(y=frame, sr=sr)
            pitch_vals = pitches_frame[pitches_frame > 0]
            if len(pitch_vals) > 0:
                pitches.append(np.mean(pitch_vals))
            else:
                pitches.append(0)
            
            # Energy
            energies.append(np.sqrt(np.mean(frame ** 2)))
        
        # Look for sudden increases
        if len(pitches) < 3:
            return {'insight_detected': False}
        
        pitch_derivative = np.diff(pitches)
        energy_derivative = np.diff(energies)
        
        pitch_spike = np.max(pitch_derivative) > 50  # Hz jump
        energy_spike = np.max(energy_derivative) > 0.05
        
        if pitch_spike and energy_spike:
            return {
                'insight_detected': True,
                'confidence': 0.7,
                'signature': 'pitch_energy_spike',
            }
        
        return {'insight_detected': False}
```

#### 4. Thermal Imaging

```python
class ThermalCognitiveAnalyzer:
    """
    Facial temperature changes reveal cognitive and emotional states.
    
    Key thermal signatures:
    - Periorbital (around eyes): Drops with cognitive load
    - Nasal tip: Drops with stress (blood redirected)
    - Forehead: Increases with mental effort
    - Perioral (around mouth): Drops with anxiety
    
    Temperature changes are involuntary and hard to mask.
    """
    
    THERMAL_REGIONS = {
        'forehead': 'cognitive_effort',
        'periorbital': 'cognitive_load',
        'nasal_tip': 'stress',
        'cheeks': 'emotional_arousal',
        'perioral': 'anxiety',
    }
    
    def extract_thermal_features(
        self,
        thermal_image: np.ndarray,  # Temperature values
        face_landmarks: Dict[str, Tuple[int, int, int, int]]  # Region bounding boxes
    ) -> Dict[str, float]:
        """
        Extract temperature from facial regions.
        """
        features = {}
        
        for region, bbox in face_landmarks.items():
            x, y, w, h = bbox
            region_temps = thermal_image[y:y+h, x:x+w]
            
            features[f'{region}_mean'] = float(np.mean(region_temps))
            features[f'{region}_max'] = float(np.max(region_temps))
            features[f'{region}_std'] = float(np.std(region_temps))
        
        return features
    
    def compute_cognitive_thermal_index(
        self,
        current_temps: Dict[str, float],
        baseline_temps: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Compute cognitive state from thermal changes.
        """
        # Forehead increase = mental effort
        forehead_change = (
            current_temps.get('forehead_mean', 0) - 
            baseline_temps.get('forehead_mean', 0)
        )
        
        # Periorbital decrease = cognitive load
        periorbital_change = (
            current_temps.get('periorbital_mean', 0) - 
            baseline_temps.get('periorbital_mean', 0)
        )
        
        # Nasal drop = stress
        nasal_change = (
            current_temps.get('nasal_tip_mean', 0) - 
            baseline_temps.get('nasal_tip_mean', 0)
        )
        
        return {
            'cognitive_effort': max(0, forehead_change * 10),  # Scale to 0-1
            'cognitive_load': max(0, -periorbital_change * 10),
            'stress_index': max(0, -nasal_change * 10),
            'combined_index': (forehead_change - periorbital_change - nasal_change) / 3,
        }
```

#### 5. Full Multi-Modal Fusion

```python
@dataclass
class AdvancedBiometricSnapshot:
    """
    Tier 3: Full multi-modal biometric snapshot.
    
    Combines all available signals for maximum insight into your cognitive state.
    """
    timestamp: datetime
    
    # Neural (electrical + metabolic)
    eeg: HighDensityEEGMetrics        # 64 channels
    eeg_coherence: Dict[str, float]    # Inter-region coherence
    eeg_source_localization: Dict[str, float]  # Estimated source activity
    fnirs: fNIRSMetrics               # Blood oxygenation
    
    # Cardiac-Respiratory
    ecg: ECGMetrics
    respiration: RespirationMetrics
    resp_cardiac_coherence: float
    
    # Peripheral
    gsr: float
    skin_temperature: float
    
    # Muscular
    facial_emg: Dict[str, float]      # Corrugator, zygomaticus, etc.
    postural_emg: Dict[str, float]    # Neck, shoulder tension
    
    # Ocular
    pupil_diameter: float
    blink_rate: float
    gaze_patterns: Dict[str, float]
    microsaccades: int
    
    # Thermal
    facial_thermal: Dict[str, float]
    
    # Voice (if speaking)
    voice_features: Optional[Dict[str, float]] = None


class AdvancedCognitiveStateClassifier:
    """
    Classify cognitive state using all available modalities.
    
    Uses ensemble of modality-specific classifiers + fusion layer.
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
    
    def classify(
        self,
        snapshot: AdvancedBiometricSnapshot
    ) -> Dict[str, Any]:
        """
        Classify cognitive state from all modalities.
        """
        modality_predictions = {}
        
        # EEG-based prediction
        modality_predictions['eeg'] = self._classify_from_eeg(
            snapshot.eeg, snapshot.eeg_coherence
        )
        
        # fNIRS-based prediction
        modality_predictions['fnirs'] = self._classify_from_fnirs(
            snapshot.fnirs
        )
        
        # Eye-based prediction
        modality_predictions['eye'] = self._classify_from_eye(
            snapshot.pupil_diameter,
            snapshot.blink_rate,
            snapshot.gaze_patterns
        )
        
        # Cardiac prediction
        modality_predictions['cardiac'] = self._classify_from_cardiac(
            snapshot.ecg, snapshot.resp_cardiac_coherence
        )
        
        # Facial EMG prediction
        modality_predictions['facial_emg'] = self._classify_from_facial_emg(
            snapshot.facial_emg
        )
        
        # Thermal prediction
        modality_predictions['thermal'] = self._classify_from_thermal(
            snapshot.facial_thermal
        )
        
        # Voice prediction (if available)
        if snapshot.voice_features:
            modality_predictions['voice'] = self._classify_from_voice(
                snapshot.voice_features
            )
        
        # Weighted fusion
        fused_prediction = self._fuse_predictions(modality_predictions)
        
        return {
            'cognitive_stage': fused_prediction['stage'],
            'confidence': fused_prediction['confidence'],
            'is_breakthrough': fused_prediction['is_breakthrough'],
            'emotional_state': fused_prediction['emotion'],
            'modality_breakdown': modality_predictions,
            'agreement_score': self._compute_agreement(modality_predictions),
        }
    
    def _fuse_predictions(
        self,
        predictions: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """
        Fuse predictions from all modalities.
        
        Uses weighted voting with confidence weighting.
        """
        stage_votes = {}
        breakthrough_votes = []
        
        for modality, pred in predictions.items():
            weight = self.modality_weights.get(modality, 0.1)
            confidence = pred.get('confidence', 0.5)
            
            # Stage voting
            stage = pred.get('stage', 'unknown')
            if stage not in stage_votes:
                stage_votes[stage] = 0
            stage_votes[stage] += weight * confidence
            
            # Breakthrough voting
            if pred.get('is_breakthrough', False):
                breakthrough_votes.append(weight * confidence)
        
        # Winner
        best_stage = max(stage_votes, key=stage_votes.get)
        best_confidence = stage_votes[best_stage] / sum(stage_votes.values())
        
        # Breakthrough consensus
        breakthrough = sum(breakthrough_votes) > 0.3
        
        return {
            'stage': best_stage,
            'confidence': best_confidence,
            'is_breakthrough': breakthrough,
            'emotion': self._fuse_emotions(predictions),
        }
    
    def _compute_agreement(
        self,
        predictions: Dict[str, Dict]
    ) -> float:
        """
        Compute agreement across modalities.
        
        High agreement = reliable prediction
        Low agreement = uncertain, investigate
        """
        stages = [p.get('stage') for p in predictions.values() if p.get('stage')]
        
        if not stages:
            return 0.0
        
        # Most common stage
        from collections import Counter
        most_common, count = Counter(stages).most_common(1)[0]
        
        return count / len(stages)
```

---

## Training Weight Impact by Tier

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    TRAINING SIGNAL QUALITY BY TIER                          │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Signal Quality                                                             │
│       ▲                                                                     │
│       │                                              ┌─────────────────┐   │
│   1.0 │                                              │   TIER 3        │   │
│       │                                          ████│ Multi-modal     │   │
│       │                                      ████████│ fNIRS + 64ch EEG│   │
│   0.8 │                                  ████████████│ Voice + Thermal │   │
│       │                     ┌────────────────────────┴─────────────────┘   │
│       │                     │   TIER 2                                     │
│   0.6 │                 ████│ 16ch EEG + EMG                               │
│       │             ████████│ Eye tracking                                 │
│       │         ████████████│ Respiratory                                  │
│   0.4 │  ┌──────────────────┴────────┐                                     │
│       │  │   TIER 1                  │                                     │
│       │  │ Apple Watch + Muse        │                                     │
│   0.2 │██│ Basic HRV + 4ch EEG       │                                     │
│       │██│                           │                                     │
│       │██└───────────────────────────┘                                     │
│   0.0 └──┬──────────────────┬────────────────────┬─────────────────────▶   │
│          │                  │                    │                          │
│       Manual            Tier 1              Tier 2              Tier 3      │
│       Labels            Basic               Enhanced            Advanced    │
│                                                                             │
│  Training Weight Multiplier:                                                │
│    Manual only: 1.0x                                                        │
│    Tier 1 confirmed: 1.3x                                                   │
│    Tier 2 confirmed: 1.7x                                                   │
│    Tier 3 confirmed: 2.5x                                                   │
│    Multi-modal agreement: +0.5x bonus                                       │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Recommended Path

### Start Here (Week 1-2)
```
Tier 1: Apple Watch + Muse 2
Cost: ~$300
Setup time: 1 day
Data quality: Basic but useful
```

### Graduate To (Month 2-3)
```
Tier 2: OpenBCI + Polar H10 + Tobii Eye Tracker
Cost: ~$2,500
Setup time: 1 week
Data quality: Research-grade core signals
```

### Full Vision (Month 6+)
```
Tier 3: Add fNIRS + Facial EMG + Thermal
Cost: ~$15,000+
Setup time: 1 month
Data quality: Publication-grade multi-modal
```

---

## The Ultimate Signal

At Tier 3, you have:

1. **What your neurons are doing** (EEG + fNIRS)
2. **What your autonomic system is doing** (ECG + GSR + respiration)
3. **What your face reveals** (EMG + thermal)
4. **What your eyes reveal** (pupil + gaze + microsaccades)
5. **What your voice reveals** (acoustic features)

**The model learns YOUR complete psychophysiological signature.**

When all modalities agree on "breakthrough" - gamma burst, pupil dilation, HRV spike, facial micro-smile, prefrontal activation, thermal shift - that example gets 2.5x weight.

**You're not training on what you THINK happened. You're training on what ACTUALLY happened in your body and brain.**
