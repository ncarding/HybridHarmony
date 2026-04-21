# Hybrid Harmony

**G2 harmonization filter for Glyphs.app with minimal shape change**

Hybrid Harmony is a Glyphs.app filter that combines the approaches of [Green Harmony](https://github.com/slobzheninov/GreenHarmony) and [Grey Harmony](https://github.com/mekkablue/GreyHarmony) to achieve G2 continuity (curvature continuity) at smooth curve connections while minimizing visible shape distortion.

## What It Does

When two Bézier curve segments meet at a smooth node (green on-curve point), the curvature on both sides should ideally match for the smoothest visual transition. This is called **G2 continuity**.

**Traditional approaches:**
- **Green Harmony**: Moves the on-curve node to achieve G2, keeping handles fixed
- **Grey Harmony**: Moves the off-curve handles (BCPs) to achieve G2, keeping the on-curve node fixed

**Hybrid Harmony**: Moves *both* the on-curve node and adjacent handles proportionally, allowing you to balance shape preservation with harmonization quality.

## Usage

### Basic Usage

1. Select one or more green smooth nodes between curve segments
2. Run **Filter > Hybrid Harmony** (or press `Ctrl-Shift-H`)
3. The selected nodes will be harmonized with a default 50/50 blend

If no nodes are selected, all smooth curve nodes in the layer will be processed.

### Modifier Keys (in Edit View)

- **Shift**: Green-only mode (moves only on-curve nodes)
- **Option/Alt**: Grey-only mode (moves only handles)
- **Option/Alt + run**: Apply to all compatible layers (for interpolation consistency)

### Custom Parameters

Add a custom parameter at export time (File > Font Info > Instances):

**Parameter name:** `Filter`  
**Value:** `HybridHarmony; alpha:0.7`

**Supported parameters:**
- `alpha`: Blend factor between 0.0 and 1.0
  - `0.0` = Grey Harmony (handles only)
  - `0.65` = Recommended blend (default)
  - `1.0` = Green Harmony (on-curve only)
- `allLayers`: `True` to apply to all compatible layers

**Example:**
```
HybridHarmony; alpha:0.3; allLayers:True
```

## Blend Factor Guide

The `alpha` parameter controls how movement is distributed:

- **`alpha = 0.0`** (Grey): Best for preserving extremum point positions and metric alignment
- **`alpha = 0.3-0.4`**: Good balance for most cases, slight preference for preserving node positions
- **`alpha = 0.65`** (default): Optimal balance of node and handle movement
- **`alpha = 0.8-1.0`**: Slight preference for moving nodes, preserves handle relationships
- **`alpha = 1.0`** (Green): Best when handle positions are more important than node positions

## Installation

### Option 1: Manual Installation

1. Download or clone this repository
2. Double-click `HybridHarmony.glyphsFilter` to install
3. Restart Glyphs.app

### Option 2: Direct Copy

Copy `HybridHarmony.glyphsFilter` to:
```
~/Library/Application Support/Glyphs 3/Plugins/
```

## Validation

Use [Speed Punk](https://glyphsapp.com/tools/speedpunk) to visualize curvature:
- After harmonization, the curvature comb (colored bars) should have matching amplitude on both sides of the harmonized node
- This indicates approximate G2 continuity

## Warnings

⚠️ **Shape alteration**: This filter will change your outlines. Always test on copies or use background layers for comparison.

⚠️ **Interpolation**: When working with multiple masters, apply the filter consistently across all masters to avoid interpolation kinks.

⚠️ **Not a silver bullet**: For complex curvature requirements or when maximum shape preservation is critical, consider [Remix Tools](https://remix-tools.com/) by Tim Ahrens.

## Technical Details

### Algorithm

Based on [Simon Cozens' G2 harmonization algorithm](https://gist.github.com/simoncozens/3c5d304ae2c14894393c6284df91be5b):

1. Find the intersection point of rays formed by adjacent Bézier control points
2. Calculate distance ratios to determine the harmonized position
3. Compute parameter `t = ratio / (ratio + 1)` for the target position
4. Apply blended movement:
   - On-curve moves by `alpha × displacement`
   - Handles move by `(1 - alpha) × displacement`

### Edge Cases Handled

- Parallel or near-parallel handle rays (skipped)
- Zero-length handles (skipped)
- Invalid geometry or missing adjacent nodes (skipped)
- Division by near-zero denominators (protected)

## Attribution & License

Copyright 2026 - Derivative work under **Apache License 2.0**

This plugin combines and extends:
- **Green Harmony** by Alex Slobzheninov ([@slobzheninov](https://github.com/slobzheninov))  
  https://github.com/slobzheninov/GreenHarmony
- **Grey Harmony** by Rainer Erich Scheichelbauer ([@mekkablue](https://github.com/mekkablue))  
  https://github.com/mekkablue/GreyHarmony

Both based on the G2 harmonization algorithm by **Simon Cozens** ([@simoncozens](https://github.com/simoncozens))  
https://gist.github.com/simoncozens/3c5d304ae2c14894393c6284df91be5b

Template code by Georg Seifert ([@schriftgestalt](https://github.com/schriftgestalt)) and Jan Gerner ([@yanone](https://github.com/yanone))

See [LICENSE](LICENSE) for full Apache 2.0 license text.

## Development

### Requirements
- Glyphs.app 3.x
- Python 2.7+ (included with Glyphs)

### Testing Checklist
- [ ] Visual G2 validation with Speed Punk
- [ ] Shape preservation metrics (before/after comparison)
- [ ] Edge case stability (parallel handles, zero handles)
- [ ] Interpolation compatibility across masters
- [ ] Export validation (CFF/TrueType)
- [ ] Undo/redo functionality

## Feedback & Contributions

Issues and pull requests welcome. When reporting issues, please include:
- Glyphs.app version
- Sample glyph file or screenshot
- Parameter values used
- Expected vs. actual behavior

---

**Related Resources:**
- [Drawing Good Paths](https://glyphsapp.com/learn/drawing-good-paths) - Glyphs tutorial
- [Harmonization](https://glyphsapp.com/learn/harmonization) - Glyphs tutorial on G0/G1/G2 continuity
- [Speed Punk](https://glyphsapp.com/tools/speedpunk) - Curvature visualization plugin
