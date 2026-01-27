# Motion & Sound Identity

**Version:** 1.0  
**Created:** January 24, 2026  
**Status:** DIRECTION FOR FUTURE IMPLEMENTATION

---

## Core Principle

Motion and sound extend the brand into time. They should feel:
- **Physical** — Like real electricity, real metal, real impact
- **Warm** — Not cold digital chirps
- **Substantial** — Weight and presence
- **Restrained** — Used sparingly, never gratuitous

---

## Motion Identity

### Philosophy

Motion should feel like **energy contained**, not energy unleashed. The bolt doesn't strike randomly—it delivers power with precision.

### Primary Motion: The Pulse

**Concept:** The logo subtly pulses with contained energy, like a heartbeat or breathing.

**Parameters:**
- Scale: 100% → 102% → 100%
- Duration: 2 seconds per cycle
- Easing: ease-in-out (organic feel)
- Opacity: Subtle glow intensifies at peak

**Use:** Idle states, loading, "system active" indicator

**CSS Example:**
```css
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    filter: drop-shadow(0 0 0px var(--accent));
  }
  50% {
    transform: scale(1.02);
    filter: drop-shadow(0 0 20px var(--accent));
  }
}

.logo-pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

---

### Secondary Motion: The Strike

**Concept:** The bolt descends with purpose—entry animation, confirmation, completion.

**Parameters:**
- Movement: Top to center (or off-screen to position)
- Duration: 400ms
- Easing: cubic-bezier(0.34, 1.56, 0.64, 1) — slight overshoot
- Impact: Subtle screen shake or ripple at landing

**Use:** Page load, successful action, NOT-ME arrival

**CSS Example:**
```css
@keyframes strike {
  0% {
    transform: translateY(-100px);
    opacity: 0;
  }
  70% {
    transform: translateY(5px);
    opacity: 1;
  }
  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.logo-strike {
  animation: strike 400ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

---

### Tertiary Motion: The Spark

**Concept:** Small energy particles emit from the bolt—micro-interactions, hover states.

**Parameters:**
- Particles: 3-5 small dots
- Movement: Radiate outward 20-40px
- Duration: 300ms
- Fade: Opacity 100% → 0%

**Use:** Hover on interactive elements, micro-feedback

---

### Loading States

**Primary loader:** The bolt pulses while a circular progress indicator completes around it.

**Alternative:** The bolt's segments "charge" sequentially from top to bottom.

**Never use:** Generic spinners, bouncing dots, or elements unrelated to the bolt.

---

### Page Transitions

**Enter:** Content fades up from below (rise, like heat)
- Duration: 300ms
- Distance: 20px
- Stagger: 50ms between elements

**Exit:** Content fades down (settle, like cooling)
- Duration: 200ms
- Distance: 10px

---

### Brand-Specific Motion

| Brand | Motion Character |
|-------|-----------------|
| **Truth Engine** | Deliberate, powerful, centered |
| **Primitive Engine** | Heavier, more impact, forge-like |
| **Credential Atlas** | Precise, clean, efficient |
| **Stage 5 Mind** | Warmer, softer, more organic |

---

## Sound Identity

### Philosophy

Sound should feel like **electricity made audible**—the warm hum of power, the clean strike of energy, the resonance of metal.

### Primary Sound: The Strike

**Concept:** A clean electrical impact—not harsh, but present.

**Characteristics:**
- Attack: Fast (< 10ms)
- Body: Electrical crackle
- Decay: Medium (200-400ms)
- Tail: Warm resonance, like struck metal settling

**Use:** Confirmations, completions, arrivals

**Reference:** Think: quality mechanical keyboard + electrical substation at distance

---

### Secondary Sound: The Hum

**Concept:** A low-frequency presence that signals "system active."

**Characteristics:**
- Frequency: 60-80Hz base
- Character: Warm electrical transformer hum
- Volume: Barely perceptible (ambient)
- Variation: Subtle modulation

**Use:** Background presence (optional), meditation/focus modes

---

### Tertiary Sound: The Spark

**Concept:** Quick, bright, micro-feedback.

**Characteristics:**
- Duration: < 100ms
- Character: High-frequency crackle
- Volume: Quiet, non-intrusive

**Use:** UI interactions, hover feedback, typing

---

### Notification Sounds

| Event | Sound Character |
|-------|-----------------|
| Message received | Single clean strike |
| NOT-ME speaks | Softer strike, warmer tone |
| Error | Lower pitch, discordant undertone |
| Success | Strike + resonant settling |
| System alert | Double strike, urgent but not alarming |

---

### Sound Design Guidelines

**Do:**
- Use real-world electrical/metal recordings as base
- Layer organic textures (room tone, natural reverb)
- Keep volumes consistent and non-fatiguing
- Allow users to mute/adjust

**Don't:**
- Use synthetic chirps or beeps
- Use generic "notification" sounds
- Make sounds attention-grabbing or alarming
- Use sounds that feel "digital" or "app-like"

---

## Implementation Priority

### Phase 1 (MVP)
- Logo pulse animation (CSS)
- Page transitions (CSS)
- No sound (can be added later)

### Phase 2 (Enhancement)
- Strike animation for key moments
- Loading states
- Basic notification sound

### Phase 3 (Polish)
- Full motion system
- Complete sound palette
- Ambient options

---

## Technical Specifications

### Motion Formats

| Context | Format |
|---------|--------|
| Web (simple) | CSS animations |
| Web (complex) | Lottie (JSON) |
| Video | After Effects / Motion |
| Native apps | Platform-native animations |

### Sound Formats

| Context | Format |
|---------|--------|
| Web | MP3 (fallback) + OGG (preferred) |
| Native apps | Platform-native (AAC, etc.) |
| Video | WAV (production) → compressed for delivery |

### File Naming

```
motion_pulse_logo_v1.json
motion_strike_logo_v1.json
motion_spark_micro_v1.json
sound_strike_primary_v1.mp3
sound_hum_ambient_v1.mp3
sound_spark_micro_v1.mp3
```

---

## Accessibility

### Motion

- Respect `prefers-reduced-motion` media query
- Provide static alternatives for all animations
- Never use motion as only indicator of state

```css
@media (prefers-reduced-motion: reduce) {
  .logo-pulse,
  .logo-strike {
    animation: none;
  }
}
```

### Sound

- All sounds optional (never required for function)
- Provide visual alternatives for all audio cues
- Allow granular volume control
- Default to sounds off (opt-in)

---

*Motion is presence. Sound is reality. Together they make the brand breathe.*
