---
id: BIOMETRIC_TRAINING
title: "Biometric Training: ECG, EEG, and Physiological Ground Truth"
type: specification
status: draft
domain: infrastructure
created: 2026-02-01
updated: 2026-02-01
author: claude
summary: |
  Defines how ECG, EEG, and other physiological signals can serve as
  ground truth for training AI models. Covers hardware options, signal
  interpretation, fusion with manual labels, and the privacy implications
  of neuron-level training data.
answers:
  - "How do biometric signals become training data?"
  - "What does ECG reveal about cognitive state?"
  - "What does EEG reveal about cognitive state?"
  - "How do you detect genuine breakthrough moments?"
  - "What hardware is needed for biometric training?"
  - "How do you fuse manual and physiological labels?"
related:
  - TRUTH_ENGINE_BUSINESS_PLAN
tags:
  - training
  - biometrics
  - ecg
  - eeg
  - ground-truth
---

# Biometric Training: ECG, EEG, and Physiological Ground Truth

## What Your Body Signals Actually Are

### ECG (Electrocardiogram) - Heart Signals

Your heart generates electrical signals that reveal:

```
ECG Waveform
     R
     ↑
    /│\
   / │ \
  /  │  \
 P   │   T
  \  │  /
   \ │ /
    \│/
     Q S
     
P wave: Atrial depolarization (anticipation)
QRS:    Ventricular contraction (action)
T wave: Ventricular recovery (settling)
```

**What ECG reveals about your cognitive state:**

| Metric | What It Measures | Training Signal |
|--------|-----------------|-----------------|
| **Heart Rate (HR)** | Beats per minute | Arousal level |
| **HRV (Heart Rate Variability)** | Beat-to-beat variation | Stress vs relaxation |
| **RMSSD** | Short-term HRV | Parasympathetic activity (calm focus) |
| **LF/HF Ratio** | Low/High frequency power | Sympathetic/parasympathetic balance |
| **Respiratory Sinus Arrhythmia** | HR changes with breathing | Emotional regulation |

### EEG (Electroencephalogram) - Brain Signals

Your neurons generate electrical patterns:

```
Frequency Bands:

Delta (0.5-4 Hz)   ~~~~~~         Deep processing, unconscious
Theta (4-8 Hz)     ∿∿∿∿∿∿         Memory, creativity, "flow"
Alpha (8-13 Hz)    ⌇⌇⌇⌇⌇⌇         Relaxed awareness, reflection
Beta (13-30 Hz)    ⎍⎍⎍⎍⎍⎍⎍⎍       Active thinking, focus
Gamma (30-100 Hz)  ⎪⎪⎪⎪⎪⎪⎪⎪⎪⎪     Insight, "aha" moments, binding
```

**What EEG reveals about your cognitive state:**

| Pattern | What It Indicates | Training Signal |
|---------|------------------|-----------------|
| **Alpha increase** | Relaxed, reflective | Synthesis stage |
| **Beta increase** | Active analysis | Analysis stage |
| **Theta burst** | Memory access, creativity | Exploration stage |
| **Gamma burst** | Insight, integration | Breakthrough moment |
| **Alpha blocking** | Attention shift | Transition detected |
| **Frontal asymmetry** | Emotional valence | Positive/negative emotion |

---

## The Mechanical Integration

### How Biometric Signals Become Training Data

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CURRENT TRAINING                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Your Conversation  →  Your Manual Label  →  Training Signal         │
│                                                                      │
│  "I finally see      "cognitive_stage:     Loss computed            │
│   the pattern"        synthesis"            against YOUR label       │
│                                                                      │
│  Problem: Label is RETROSPECTIVE, possibly rationalized              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                   BIOMETRIC TRAINING                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Your Conversation  →  Your Body's Signal  →  Training Signal        │
│        +                                                             │
│  Your Physiology                                                     │
│                                                                      │
│  "I finally see       ECG: HRV spike        Multi-modal ground      │
│   the pattern"        EEG: Gamma burst       truth                   │
│                       GSR: Conductance ↑                             │
│                                                                      │
│  Advantage: Signal is REAL-TIME, INVOLUNTARY, UNFAKEABLE            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### The Weight Update With Biometrics

```
                    YOUR TEXT                YOUR BODY
                        │                        │
                        ↓                        ↓
              ┌─────────────────┐      ┌─────────────────┐
              │  "I realized    │      │  ECG: HRV +23%  │
              │   something     │      │  EEG: Gamma 40Hz│
              │   profound"     │      │  GSR: +0.3 µS   │
              └─────────────────┘      └─────────────────┘
                        │                        │
                        └──────────┬─────────────┘
                                   ↓
                    ┌──────────────────────────────┐
                    │     BIOMETRIC DECODER        │
                    │                              │
                    │  Gamma + HRV spike =         │
                    │  GENUINE breakthrough        │
                    │                              │
                    │  (vs just saying the word    │
                    │   "breakthrough")            │
                    └──────────────────────────────┘
                                   │
                                   ↓
                    ┌──────────────────────────────┐
                    │     FUSED GROUND TRUTH       │
                    │                              │
                    │  cognitive_stage: synthesis  │
                    │  emotion: breakthrough       │
                    │  confidence: 0.95 (body)     │
                    │  physiological_verified: ✓   │
                    └──────────────────────────────┘
                                   │
                                   ↓
                         Loss & Weight Update
                         
              Weights learn: What REAL breakthrough looks like
              (not just the word, the actual neural signature)
```

---

## What Each Signal Contributes

### ECG → Emotional Authenticity

```python
class ECGEncoder:
    """
    ECG signals validate emotional labels.
    
    Your heart doesn't lie. When you label something as
    "breakthrough" but your HRV is flat, the model learns
    to weight that label lower.
    """
    
    def compute_emotional_authenticity(self, ecg_window, stated_emotion):
        # Extract HRV metrics
        hrv = self.compute_hrv(ecg_window)
        
        # Emotional arousal from HRV
        if stated_emotion in ['breakthrough', 'excited', 'frustrated']:
            # High arousal emotions should show HRV changes
            expected_hrv_change = True
            actual_hrv_change = abs(hrv.rmssd_delta) > 10  # ms
            
            authenticity = 1.0 if actual_hrv_change else 0.5
        
        elif stated_emotion in ['calm', 'reflective', 'neutral']:
            # Low arousal emotions should show stable HRV
            expected_stability = True
            actual_stability = hrv.rmssd_delta < 5
            
            authenticity = 1.0 if actual_stability else 0.7
        
        return authenticity
```

**Training effect**: Model learns to distinguish GENUINE emotional states from stated ones.

### EEG → Cognitive State Verification

```python
class EEGEncoder:
    """
    EEG signals verify cognitive stage labels.
    
    Different cognitive stages have distinct neural signatures.
    Your brain shows what stage you're ACTUALLY in.
    """
    
    COGNITIVE_SIGNATURES = {
        'exploration': {
            'theta': 'elevated',      # Memory search, curiosity
            'alpha': 'moderate',      # Open awareness
            'beta': 'low-moderate',   # Not intense focus yet
        },
        'analysis': {
            'theta': 'moderate',
            'alpha': 'suppressed',    # Alpha blocking = attention
            'beta': 'elevated',       # Active processing
        },
        'synthesis': {
            'theta': 'elevated',      # Integration
            'alpha': 'elevated',      # Relaxed insight
            'gamma': 'bursts',        # Binding, "aha"
        },
        'integration': {
            'alpha': 'high',          # Settled understanding
            'beta': 'low',            # Not effortful
            'coherence': 'high',      # Cross-region synchrony
        },
    }
    
    def verify_cognitive_stage(self, eeg_window, stated_stage):
        # Extract band powers
        bands = self.compute_band_powers(eeg_window)
        
        # Compare to expected signature
        expected = self.COGNITIVE_SIGNATURES[stated_stage]
        match_score = self.compare_signature(bands, expected)
        
        return match_score  # 0.0 to 1.0
```

**Training effect**: Model learns what cognitive stages ACTUALLY look like neurologically.

### Combined → Breakthrough Detection

```python
class BreakthroughDetector:
    """
    Detect GENUINE breakthrough moments from physiology.
    
    A real breakthrough has a distinct signature:
    - Gamma burst (insight binding)
    - HRV spike (emotional arousal)
    - GSR increase (sympathetic activation)
    - Followed by alpha increase (settling)
    
    This is involuntary. You can't fake it.
    """
    
    def detect_breakthrough(self, eeg, ecg, gsr, window_ms=2000):
        # Check for gamma burst
        gamma_power = self.compute_gamma(eeg)
        gamma_burst = gamma_power > self.gamma_threshold
        
        # Check for HRV spike
        hrv_delta = self.compute_hrv_change(ecg)
        hrv_spike = abs(hrv_delta) > 15  # ms
        
        # Check for GSR increase
        gsr_delta = self.compute_gsr_change(gsr)
        gsr_increase = gsr_delta > 0.2  # µS
        
        # All three = genuine breakthrough
        if gamma_burst and hrv_spike and gsr_increase:
            return {
                'is_breakthrough': True,
                'confidence': 0.95,
                'signature': 'full_physiological',
            }
        
        # Partial signature
        elif gamma_burst or (hrv_spike and gsr_increase):
            return {
                'is_breakthrough': True,
                'confidence': 0.70,
                'signature': 'partial_physiological',
            }
        
        return {'is_breakthrough': False, 'confidence': 0.3}
```

---

## The Training Pipeline With Biometrics

### Data Collection Setup

```
┌─────────────────────────────────────────────────────────────────────┐
│                     YOUR TRAINING SESSION                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │  Apple      │  │  EEG        │  │  Optional   │                 │
│  │  Watch      │  │  Headband   │  │  GSR Ring   │                 │
│  │             │  │             │  │             │                 │
│  │  ECG/HRV    │  │  Muse/      │  │  Oura/      │                 │
│  │  sampling   │  │  OpenBCI    │  │  custom     │                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                         │
│         └────────────────┼────────────────┘                         │
│                          ↓                                          │
│               ┌────────────────────┐                                │
│               │  Sync Server       │                                │
│               │                    │                                │
│               │  Timestamps all    │                                │
│               │  signals to ms     │                                │
│               │  precision         │                                │
│               └─────────┬──────────┘                                │
│                         │                                           │
│                         ↓                                           │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     CONVERSATION                             │   │
│  │                                                              │   │
│  │  You chat with Claude/GPT while wearing sensors             │   │
│  │  Every message timestamped                                   │   │
│  │  Physiology recorded continuously                            │   │
│  │                                                              │   │
│  │  Text: "I think I finally understand..."                     │   │
│  │  Time: 2026-02-01T14:32:15.234Z                             │   │
│  │  ECG:  [HRV window at that moment]                          │   │
│  │  EEG:  [Band powers at that moment]                         │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Fused Training Example

```python
@dataclass
class BiometricTrainingExample:
    """
    A training example with physiological ground truth.
    """
    # Text
    text: str
    timestamp: datetime
    
    # Manual labels (your conscious annotation)
    manual_cognitive_stage: str
    manual_emotion: str
    manual_is_breakthrough: bool
    
    # Physiological signals (your body's annotation)
    ecg_window: np.ndarray      # 10 seconds around message
    eeg_window: np.ndarray      # 10 seconds around message
    gsr_value: float            # At message time
    
    # Computed physiological labels
    physio_cognitive_stage: str  # From EEG signature
    physio_emotion_arousal: float  # From HRV
    physio_is_breakthrough: bool  # From combined signature
    
    # Fusion weights
    manual_confidence: float     # How certain were you?
    physio_confidence: float     # How clear was the signal?
    
    def get_fused_label(self):
        """
        Fuse manual and physiological labels.
        
        When they agree: High confidence
        When they disagree: Investigate or weight by physio
        """
        if self.manual_is_breakthrough == self.physio_is_breakthrough:
            # Agreement - high confidence
            return {
                'is_breakthrough': self.manual_is_breakthrough,
                'confidence': 0.95,
                'source': 'fused_agreement',
            }
        
        elif self.physio_is_breakthrough and not self.manual_is_breakthrough:
            # Body says breakthrough, you didn't notice
            # Trust the body - subconscious breakthrough
            return {
                'is_breakthrough': True,
                'confidence': 0.80,
                'source': 'physio_override',
                'note': 'Subconscious breakthrough detected',
            }
        
        else:
            # You said breakthrough, body doesn't show it
            # Maybe verbal pattern, not genuine
            return {
                'is_breakthrough': self.manual_is_breakthrough,
                'confidence': 0.50,
                'source': 'manual_only',
                'note': 'No physiological confirmation',
            }
```

### The Loss Function With Biometrics

```python
def compute_biometric_loss(
    predictions: Dict,
    manual_labels: Dict,
    physio_labels: Dict,
    physio_confidence: float
):
    """
    Loss function that incorporates physiological ground truth.
    
    Key insight: Physiology provides CONFIDENCE WEIGHTING.
    
    - High physio confidence → trust the label more
    - Manual-physio agreement → maximum weight
    - Manual-physio disagreement → investigate or reduce weight
    """
    
    # Base loss on manual labels
    manual_loss = compute_standard_loss(predictions, manual_labels)
    
    # Physio loss (if signal is clean)
    if physio_confidence > 0.7:
        physio_loss = compute_standard_loss(predictions, physio_labels)
    else:
        physio_loss = 0.0
    
    # Agreement bonus
    if labels_agree(manual_labels, physio_labels):
        agreement_weight = 1.5  # Boost confident examples
    else:
        agreement_weight = 0.7  # Reduce uncertain examples
    
    # Fused loss
    total_loss = (
        0.4 * manual_loss +           # Your conscious labels
        0.4 * physio_loss +           # Your body's labels
        0.2 * consistency_loss        # Encourage agreement
    ) * agreement_weight
    
    return total_loss
```

---

## What This Changes About Training

### 1. Unfakeable Ground Truth

```
Manual labeling:
  You: "This is a breakthrough moment"
  Reality: Maybe, maybe not. You might be wrong about yourself.

Biometric labeling:
  Your body: [Gamma burst + HRV spike + GSR increase]
  Reality: This IS a breakthrough. Neurologically confirmed.
```

**Training effect**: Model learns what breakthrough ACTUALLY is, not what you THINK it is.

### 2. Subconscious Pattern Detection

```
You might not notice:
- Subtle stress during certain topics (HRV reveals)
- Micro-insights before conscious awareness (Gamma reveals)
- Emotional reactions you rationalize away (GSR reveals)

Biometrics capture what you miss.
```

**Training effect**: Model learns patterns you weren't even aware of.

### 3. Confidence Calibration

```
Example 1:
  Text: "I think this is synthesis stage"
  Manual confidence: 0.6 (you're unsure)
  Physio: Alpha elevated, gamma present
  Fused confidence: 0.9 (body confirms)

Example 2:
  Text: "This is definitely a breakthrough"
  Manual confidence: 0.95 (you're certain)
  Physio: No gamma, flat HRV
  Fused confidence: 0.5 (body disagrees)
```

**Training effect**: Model learns when to trust labels and when to be skeptical.

### 4. Temporal Precision

```
Manual labeling:
  After the conversation: "That message around 2:30 was important"
  Precision: ±minutes

Biometric labeling:
  During the conversation: [Gamma burst at 14:32:15.234]
  Precision: ±milliseconds
```

**Training effect**: Model learns EXACTLY when insights occur, not approximately.

---

## Hardware Options

### Consumer Grade (Available Now)

| Device | Signals | Pros | Cons |
|--------|---------|------|------|
| **Apple Watch** | ECG, HRV, movement | Already own it, seamless | Limited to heart |
| **Oura Ring** | HRV, temperature, movement | 24/7 wear, sleep data | No real-time stream |
| **Muse 2** | EEG (4 channels) | Affordable ($250), app | Limited channels |
| **Polar H10** | ECG, HRV | Research-grade HRV | Chest strap |

### Research Grade (Better Signal)

| Device | Signals | Pros | Cons |
|--------|---------|------|------|
| **OpenBCI** | EEG (8-16 channels) | Open source, flexible | DIY, messy |
| **Emotiv Insight** | EEG (5 channels) | Wireless, comfortable | Expensive ($500) |
| **Neurosity Crown** | EEG (8 channels) | Developer-focused | Limited availability |

### Recommended Setup for You

```
Minimum Viable Biometric Training:
  - Apple Watch (you probably have) → ECG/HRV
  - Muse 2 headband ($250) → EEG basics
  
Enhanced Setup:
  - Polar H10 chest strap → Better HRV
  - OpenBCI Cyton ($1000) → Research-grade EEG
  - Custom sync software → Timestamp alignment
```

---

## The Deeper Implication

### You're Not Just Training a Model

```
Standard ML:
  Data → Model → Predictions
  
  Model learns statistical patterns.

Biometric Genesis:
  Your neurons → Your labels → Model weights
  
  Model learns YOUR neural patterns.
  
  The weights literally encode your brain's signature.
```

### What "Neuron Signals to Train" Actually Means

When you wear an EEG and your gamma oscillations spike during an insight:

1. Those gamma waves are literal neuron synchronization
2. Millions of your neurons firing together at 40Hz
3. That pattern becomes a training signal
4. Model weights shift to recognize that signature
5. The model learns what YOUR neurons look like when they "get it"

**The model isn't learning your thoughts. It's learning your thought PATTERNS.**

```
Your neurons: ⎪⎪⎪⎪⎪⎪⎪⎪⎪⎪ (gamma burst)
              ↓
Model weights: [shift toward recognizing this pattern]
              ↓
Future input: "Something feels like it's clicking..."
              ↓
Model output: "This has the signature of genuine insight"
              (because it learned YOUR insight signature)
```

---

## Privacy & Sovereignty Note

This data is extraordinarily intimate:

- Your neural patterns
- Your emotional signatures
- Your physiological responses

**This must remain YOURS:**
- Local processing only
- No cloud upload of biometrics
- You control the data
- Model trained on YOUR hardware (THE EMPIRE)

The point is training a model that sees like YOU - not giving your brain patterns to anyone else.

---

## Next Steps If You Want This

1. **Acquire hardware**: Start with Apple Watch ECG + Muse 2
2. **Build sync infrastructure**: Timestamp alignment across devices
3. **Collect pilot data**: 10 hours of conversations with biometrics
4. **Validate signatures**: Confirm gamma/HRV patterns match expected
5. **Integrate into pipeline**: Add biometric channels to training

Would you like me to spec out the data collection infrastructure?
