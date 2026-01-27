# Texture Standards

**Version:** 1.0  
**Created:** January 24, 2026  
**Philosophy:** Tactile rebellion — physical, crafted, permanent

---

## Core Principle

The grunge/distress texture is a core brand element. It signals:
- **Physical** — This could be stamped into metal
- **Crafted** — Made by human hands with intention
- **Permanent** — Built to last, weathered by time
- **Real** — Not AI-generated smoothness

---

## Texture Modes

Three standardized texture levels for consistent application:

### Light Wear (15% Distress)

**Use for:**
- Credential Atlas (precision brand)
- Clean, authoritative contexts
- Small applications (favicons, app icons)
- Digital-first applications

**Characteristics:**
- Subtle concrete spatter
- Minimal edge erosion
- Clean silhouette preserved
- Professional, precise feel

**Application:** Logo at full resolution with light noise overlay

---

### Medium Wear (30% Distress)

**Use for:**
- Truth Engine (primary brand)
- Standard brand applications
- Website, print, marketing
- Most common use case

**Characteristics:**
- Visible concrete texture
- Some edge softening
- Industrial stamped feel
- Balanced wear and clarity

**Application:** Logo with moderate grunge treatment, visible but not dominant

---

### Heavy Wear (60% Distress)

**Use for:**
- Primitive Engine (forge brand)
- Workshop/industrial contexts
- Hero images, large applications
- Physical products, merchandise

**Characteristics:**
- Significant surface wear
- Cracks, scratches visible
- Edge erosion present
- Aged, battle-worn feel

**Application:** Logo with full grunge treatment, texture is prominent

---

## Texture by Brand

| Brand | Default Texture | Reasoning |
|-------|-----------------|-----------|
| **Truth Engine** | Medium (30%) | Source, authoritative but real |
| **Primitive Engine** | Heavy (60%) | Forge, workshop, creation |
| **Credential Atlas** | Light (15%) | Precision, clarity, trust |
| **Stage 5 Mind** | Light-Medium (20%) | Human, warm, approachable |

---

## Texture Elements

### Concrete Spatter
- Small particle noise
- Irregular distribution
- Density varies by texture level

### Surface Cracks
- Fine hairline cracks (Medium)
- Visible crack networks (Heavy)
- Radiate from stress points

### Edge Erosion
- Slight edge softening (Light)
- Visible edge wear (Medium)
- Significant edge breakdown (Heavy)

### Scratches
- None (Light)
- Subtle linear marks (Medium)
- Visible scratch patterns (Heavy)

---

## Technical Specifications

### For Vector (Ivan's Deliverables)

Request from Ivan:
1. **Clean vector** — No texture, pure geometric shape
2. **Light texture overlay** — Separate layer, 15% distress
3. **Medium texture overlay** — Separate layer, 30% distress
4. **Heavy texture overlay** — Separate layer, 60% distress

File format: `.ai` (Adobe Illustrator) with layers, plus `.svg` exports

### For Raster Applications

When applying texture to clean vectors:

```
Base layer: Clean logo (vector or high-res raster)
Texture layer: Concrete/grunge texture image
Blend mode: Multiply or Overlay
Opacity: Varies by texture level (15/30/60%)
```

### Texture Source Files

Create or source:
- `texture_concrete_01.png` — Fine concrete grain
- `texture_grunge_01.png` — General distress
- `texture_cracks_01.png` — Crack patterns
- `texture_scratches_01.png` — Linear wear marks

Resolution: Minimum 4000×4000px, seamless tileable

---

## Application Guidelines

### Digital (Screens)

| Context | Texture Level |
|---------|---------------|
| Favicon | Light or None |
| App icon | Light |
| Website header | Medium |
| Hero section | Medium or Heavy |
| Social avatar | Light |
| Email signature | Light |

### Print

| Context | Texture Level |
|---------|---------------|
| Business card | Medium |
| Letterhead | Light |
| Large format poster | Heavy |
| Product packaging | Heavy |
| Documentation | Light |

### Physical/Product

| Context | Texture Level |
|---------|---------------|
| Hardware badge | Heavy (engraved feel) |
| Merchandise | Heavy |
| Signage | Medium to Heavy |
| Embossing | Clean (texture from material) |

---

## Background Treatments

The texture extends beyond logos to backgrounds:

### Dark Textured Background
```css
background-color: #0D0D0D;
background-image: url('texture_concrete_dark.png');
background-blend-mode: overlay;
background-size: cover;
```

### Light Textured Background
```css
background-color: #F5F0E6;
background-image: url('texture_concrete_light.png');
background-blend-mode: multiply;
opacity: 0.3;
```

---

## Forbidden Patterns

- Never apply texture to body text (readability)
- Never use color in texture overlays (grayscale only)
- Never apply heavy texture to small sizes (loses detail)
- Never mix texture styles in single composition
- Never use photographic textures (abstract only)
- Never apply texture at inconsistent levels within same brand context

---

## Quality Checklist

Before using textured logo:

- [ ] Texture level matches brand and context
- [ ] Logo silhouette remains recognizable
- [ ] Works at intended reproduction size
- [ ] Contrast sufficient for readability
- [ ] Consistent with other materials in same context
- [ ] Not competing with other visual elements

---

*Texture is truth. These marks have lived. They are not pristine because nothing real is pristine.*
