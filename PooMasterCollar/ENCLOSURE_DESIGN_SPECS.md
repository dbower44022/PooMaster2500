# 3D Enclosure Design Specifications

## 📐 Overall Dimensions

**Outer Dimensions:**
- Length: 50mm
- Width: 30mm  
- Height: 14mm (12mm base + 2mm lid)
- Weight target: <10g (for enclosure alone)

**Wall Thickness:** 1.5-2mm (balance strength vs size)

## 🎯 Design Philosophy

**Goals:**
- Minimize size and weight
- Easy assembly (snap-fit or small screws)
- Accessible charging port
- Clear LED visibility
- Durable for daily wear
- Safe for puppy

## 📦 Component Envelope (Space Requirements)

```
Internal Layout (Top View):
┌──────────────────────────────────┐
│   ┌─────────────┐                │  50mm
│   │  ESP32-C3   │   [Switch]     │  
│   │  22×18mm    │    5×3mm       │
│   └─────────────┘                │
│                                  │
│   ┌──────────────────────┐       │
│   │   Battery 602535     │       │
│   │   25×35×6mm          │       │
│   └──────────────────────┘       │
│                                  │
│  [LED1]              [LED2]      │
│   5mm                 5mm        │
└──────────────────────────────────┘
     30mm
```

**Component Heights:**
- ESP32-C3: 3.2mm
- Battery: 6mm (tallest component)
- LEDs: 8.5mm (if through-hole, standing)
- Switch: 3mm
- **Total internal height needed:** 12mm minimum

**Cable/Wire Space:** Add 2-3mm clearance for wires

## 🔍 Critical Features

### 1. USB-C Port Access
```
Location: Short edge, centered
Size: 10mm wide × 4mm tall
Shape: Rounded rectangle
Depth: Cut through to board (9mm)
Clearance: Extra 1mm around connector for cable
```

**Important:** Port should be easily accessible without removing from collar.

### 2. LED Windows / Light Pipes

**Option A: Clear Windows (Easier)**
```
Location: Top surface, 10mm from each edge
Size: 6mm diameter circular windows
Depth: 0.5mm thick clear material
Method: Print separately in clear PETG/transparent resin
Fit: Press-fit or glue into main housing
```

**Option B: Integrated Light Pipes (Better light)**
```
Location: Same as above
Design: 
  - Inner diameter: 5.5mm (LED fits inside)
  - Outer diameter: 6-7mm
  - Height: Full enclosure height (12mm)
  - Top: Flared to 8-10mm for wide viewing angle
  - Surface: Slightly dome-shaped for diffusion
Material: Clear PETG or transparent resin
Print: Separately, vertical orientation
```

**LED Alignment:** Include internal posts or holders to position LEDs exactly under light pipes.

### 3. Power Switch Access
```
Location: Side edge, 5mm from back
Size: 3mm × 8mm slot
Shape: Rectangular
Purpose: Slide switch access
Include: Labels (ON/OFF) or dots for tactile feedback
```

### 4. Collar Attachment

**Recommended: Slide Clip Design**
```
Location: Back of enclosure
Design:
  - Two parallel rails, 20mm apart
  - Rail height: 3mm
  - Rail depth: 2mm
  - Gap between rails: Collar width + 1mm
    * Small collar: 16mm (15mm collar + 1mm)
    * Medium collar: 21mm (20mm collar + 1mm)
    * Large collar: 26mm (25mm collar + 1mm)
  - Add retention bumps to prevent sliding
```

**Alternative: Strap Loops**
```
Location: Back of enclosure, top and bottom
Design:
  - 2 loops, 5mm wide, 10mm opening
  - Thread velcro strap through
  - Advantage: Universal fit, easy removal
```

**Alternative: Carabiner Loop**
```
Location: Top center back
Design:
  - Single sturdy loop, 8mm diameter hole
  - Wall thickness: 3mm (extra strong)
  - Attach small carabiner to clip to D-ring
  - May dangle depending on collar
```

## 🏗️ Construction Method

### Two-Part Design (Recommended)

**Base (Bottom):**
- Houses all electronics
- Includes mounting features
- Posts for LED alignment
- Wire channels
- Screw posts or snap-fit tabs

**Lid (Top):**
- Covers electronics
- LED windows integrated or separate
- Smooth top surface
- Snap-fit or 2-4 small screws (M2×4mm)
- Optional: Gasket groove for water resistance

### Snap-Fit Details
```
Tab Design:
- Width: 4mm
- Length: 6mm
- Undercut: 0.3mm
- Taper: 30° for easy insertion
- Quantity: 4 tabs (one per corner)
```

### Screw Mount Details
```
Posts:
- Diameter: 4mm outer, 1.6mm inner (M2 tap)
- Height: 10mm
- Location: 4 corners, inset 4mm
- Screws: M2×4mm or M2×6mm (countersunk or button head)
```

## 🎨 Print Settings

**Material Options:**
| Material | Pros | Cons | Best For |
|----------|------|------|----------|
| PETG | Durable, slight flex, weather resistant | Harder to print | Primary choice |
| ABS | Strong, heat resistant | Warping, fumes | High durability |
| PLA | Easy to print, cheap | Brittle, sun degrades | Prototyping only |
| TPU | Flexible, shock absorbing | Hard to print small | Protective bumper |

**Print Settings:**
```
Layer Height: 0.2mm (or 0.15mm for better detail)
Wall Count: 3-4 (for strength)
Infill: 20-30% (balance weight vs strength)
Top/Bottom Layers: 5
Support: Only for overhangs >50°
Orientation: Bottom-down for main housing
Speed: 40-50mm/s (slower for small parts)
```

**Clear Parts (Light Pipes/Windows):**
```
Material: Clear PETG or Transparent resin (SLA)
Layer Height: 0.1mm (smoother = clearer)
Wall Count: 2-3
Infill: 100% (must be solid for clarity)
Speed: 30mm/s (prevent vibrations)
Post-processing: 
  - Sand with 400 → 800 → 1200 grit
  - Polish with plastic polish or heat gun (carefully)
  - Or use clear epoxy resin coating
```

## 🔒 Sealing & Weatherproofing

**Basic Protection (Light Rain):**
- Tight snap-fit with 0.2mm interference
- Silicone sealant around USB port internally
- TPU gasket between base and lid (optional)

**Better Protection (IP54):**
- Add O-ring groove: 1mm wide × 0.8mm deep
- Use thin silicone O-ring (25mm × 1mm)
- Seal USB port with rubber plug when not charging
- Conformal coating on electronics

**Ventilation:**
- Small vent holes (0.5mm) on bottom for pressure equalization
- Covered by Gore-tex-style membrane if waterproofing

## 🎨 Aesthetic Options

**Colors:**
- Classic: Black, white, gray
- Fun: Match collar color, bright colors
- Reflective: Add reflective tape strip
- Glow: Glow-in-dark filament for night visibility

**Surface Finish:**
- Smooth matte: Standard
- Textured: Add light texture for grip
- Logo/Name: Embossed or debossed puppy's name

**Customization Ideas:**
- Paw print design on top
- Bone-shaped enclosure (slightly larger)
- Integrates with existing collar design
- Matching accessories (leash holder, etc.)

## 📏 CAD Design Tips

**Start Points:**
1. Create component envelope (ESP32-C3, battery, LEDs)
2. Add 2mm clearance around each component
3. Design bottom housing with mounting posts
4. Add wire routing channels (2mm wide × 2mm deep)
5. Design lid with LED features
6. Add snap-fit or screw mounting
7. Design collar attachment
8. Fillet all sharp edges (1mm radius minimum)

**Critical Dimensions to Check:**
- USB-C connector clearance (9mm deep minimum)
- LED alignment with light pipes (±0.5mm tolerance)
- Battery fit (snug but not tight - thermal expansion)
- Wire routing path (no sharp bends)
- Switch actuation (test slide range)

## 🧪 Prototyping Strategy

**Print Order:**
1. **Rough prototype** (PLA, fast settings) - verify size/fit
2. **LED test piece** - verify light pipes/windows work
3. **Collar clip test** - verify fits collar properly
4. **Final version** (PETG, good settings) - iterate if needed

**Before Final Print:**
- [ ] All components fit comfortably
- [ ] LEDs visible from multiple angles
- [ ] USB port accessible with cable
- [ ] Switch works smoothly
- [ ] Collar attachment secure
- [ ] No sharp edges
- [ ] Comfortable weight/size

## 📋 Design Checklist

**Functionality:**
- [ ] USB-C port fully accessible
- [ ] LEDs visible from 180° viewing angle
- [ ] Power switch accessible and labeled
- [ ] Battery removable (or permanent with charging access)
- [ ] Secure collar mounting
- [ ] Wire strain relief

**Safety:**
- [ ] No sharp edges (all 1mm+ fillet)
- [ ] No small parts that can detach
- [ ] No choking hazards
- [ ] Smooth exterior (won't catch on things)
- [ ] Breakaway feature (optional - release under extreme force)
- [ ] Non-toxic materials

**Durability:**
- [ ] 2mm+ wall thickness
- [ ] Reinforced stress points
- [ ] Protected electronics
- [ ] Secure lid retention
- [ ] Weather-resistant

**Assembly:**
- [ ] Easy to open for battery/maintenance
- [ ] Clear assembly order
- [ ] No special tools needed (or just small screwdriver)
- [ ] Parts key or snap together obviously

## 📐 Reference Dimensions Summary

```
External Enclosure:
  Length: 50mm
  Width: 30mm
  Height: 14mm
  
Internal Space:
  Length: 46mm (minus walls)
  Width: 26mm (minus walls)
  Height: 12mm (minus lid)
  
USB-C Port:
  Width: 10mm
  Height: 4mm
  Depth: 9mm
  
LED Windows:
  Diameter: 6-8mm
  Spacing: 30mm apart
  
Collar Clip:
  Rail spacing: 15-25mm (adjustable)
  Rail height: 3mm
  Rail depth: 2mm
```

## 🎯 Final Notes

**Design for Printability:**
- Avoid overhangs >45°
- Minimum feature size: 1mm
- Use chamfers instead of fillets where possible
- Orient parts for minimal support

**Design for Assembly:**
- Components install from one direction
- LED positioning aids (posts/slots)
- Clear top/bottom orientation
- Foolproof assembly (can't install wrong)

**Design for Maintenance:**
- Easy access to battery
- Replaceable components
- Spare screw holes for modifications
- Version number embossed on bottom

## 📁 Recommended CAD Software

**Free Options:**
- **Fusion 360** (free for hobbyists) - Best overall
- **FreeCAD** - Open source
- **TinkerCAD** - Beginner-friendly, browser-based
- **OpenSCAD** - Parametric, code-based

**Paid Options:**
- **SolidWorks** - Professional
- **Rhino** - Excellent for organic shapes

## 🎬 Design Process Summary

1. **Import components** (or create simplified models)
2. **Create layout** (arrange for optimal space)
3. **Design base** (bottom housing + mounting)
4. **Design lid** (top cover + LED features)
5. **Add attachment** (collar clip/strap)
6. **Add features** (USB access, switch, etc.)
7. **Fillet edges** (1mm radius minimum)
8. **Prototype** (print and test fit)
9. **Refine** (iterate based on test fit)
10. **Final print** (good settings, good material)

---

**Estimated Design Time:** 4-8 hours (for first design)
**Print Time:** 1-2 hours (per enclosure)
**Material Cost:** $1-2 per enclosure

**Ready to design? Let's make it happen! 🚀**
