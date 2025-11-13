# ESP32 Puppy Tracker - Bill of Materials (BOM)

## 📦 Shopping List - Per Device

### Core Components

| Component | Quantity | Specifications | Est. Price | Notes |
|-----------|----------|----------------|------------|-------|
| ESP32 Development Board | 1 | ESP32-WROOM-32 | $8-12 | Includes USB, voltage regulator |
| WS2812B NeoPixel LEDs | 2 | 5V RGB LED | $1-2 | Individual LEDs or get a strip |
| Push Buttons | 2 | 12mm Momentary NO | $1-2 | Tactile or larger panel mount |
| Active Buzzer | 1 | 5V Active Buzzer | $1-2 | Make sure it's ACTIVE, not passive |

**Subtotal Core: ~$11-18 per device**

### Supporting Components

| Component | Quantity | Value | Purpose | Est. Price |
|-----------|----------|-------|---------|------------|
| Resistor | 1 | 470Ω | NeoPixel data protection | $0.10 |
| Capacitor | 1 | 1000µF, 16V+ | Power smoothing | $0.50 |
| Jumper Wires | 10-15 | Various M-M, M-F | Connections | $2-5 |
| Breadboard | 1 | Half-size | Prototyping | $3-5 |

**Subtotal Supporting: ~$5-11**

### Optional/Final Assembly

| Item | Quantity | Purpose | Est. Price |
|------|----------|---------|------------|
| Perfboard | 1 | Permanent soldering | $2-5 |
| USB Cable | 1 | Power & programming | $3-5 |
| Enclosure | 1 | Protection & aesthetics | $5-15 (or 3D print) |
| M3 Screws/Standoffs | 4 | Mounting ESP32 | $2-5 |
| 3D Printing Filament | 50-100g | Custom enclosure | $2-5 |

**Subtotal Optional: ~$14-35**

### **Total Cost per Device: $30-64**
*(Lower end for bare breadboard, higher end for finished enclosure)*

---

## 🛒 Where to Buy

### Option 1: Amazon (Fast Shipping)

**ESP32 Development Board:**
- Search: "ESP32 WROOM 32 Development Board"
- Examples:
  - HiLetgo ESP-WROOM-32
  - AZ-Delivery ESP32 DevKit
  - DOIT ESP32 DevKit V1
- Price: $8-12
- Link: [Amazon ESP32 Boards](https://www.amazon.com/s?k=esp32+wroom+32+development+board)

**WS2812B NeoPixels:**
- Search: "WS2812B LED Individual"
- Options:
  - 5-pack individual LEDs with wires
  - Cut from a NeoPixel strip (cheaper per LED)
- Price: $1-2 each or $8-15 for strip
- Link: [Amazon WS2812B](https://www.amazon.com/s?k=ws2812b+led)

**Push Buttons:**
- Search: "12mm Momentary Push Button"
- Get tactile/clicky buttons
- Price: $5-10 for 10-pack
- Link: [Amazon Push Buttons](https://www.amazon.com/s?k=12mm+momentary+push+button)

**Active Buzzer:**
- Search: "5V Active Buzzer Arduino"
- IMPORTANT: Must say "ACTIVE" not passive
- Price: $5-8 for 5-pack
- Link: [Amazon Active Buzzer](https://www.amazon.com/s?k=5v+active+buzzer)

**Resistors & Capacitors:**
- Search: "Resistor Kit" and "Electrolytic Capacitor Kit"
- Get assortment kits - good for future projects
- Price: $10-15 for comprehensive kit
- Link: [Amazon Resistor Kit](https://www.amazon.com/s?k=resistor+kit)

**Jumper Wires:**
- Search: "Dupont Jumper Wire Kit"
- Get male-to-male and male-to-female
- Price: $5-10 for 120+ pieces
- Link: [Amazon Jumper Wires](https://www.amazon.com/s?k=dupont+jumper+wire)

**Breadboard:**
- Search: "Half Size Breadboard"
- 400 tie points
- Price: $3-5 each or multi-pack
- Link: [Amazon Breadboard](https://www.amazon.com/s?k=breadboard)

---

### Option 2: Adafruit (Quality Components)

**Website:** https://www.adafruit.com

**ESP32:**
- Product: Adafruit HUZZAH32 – ESP32 Feather Board
- ID: 3405
- Price: $21.95
- URL: https://www.adafruit.com/product/3405

**NeoPixels:**
- Product: NeoPixel Diffused 5mm Through-Hole LED
- ID: 1938
- Price: $0.95 each
- URL: https://www.adafruit.com/product/1938

**Alternative - Strip:**
- Product: NeoPixel Strip (cut to 2 LEDs)
- ID: 1376 (30 LEDs/meter)
- Price: $16.95
- URL: https://www.adafruit.com/product/1376

**Buttons:**
- Product: Colorful Round Tactile Button Switch Assortment
- ID: 1009
- Price: $2.50 (15-pack)
- URL: https://www.adafruit.com/product/1009

**Buzzer:**
- Product: Buzzer - 5V
- ID: 1536
- Price: $1.50
- URL: https://www.adafruit.com/product/1536

---

### Option 3: SparkFun (Arduino Ecosystem)

**Website:** https://www.sparkfun.com

**ESP32:**
- Product: SparkFun Thing Plus - ESP32 WROOM
- ID: DEV-15663
- Price: $21.50
- URL: https://www.sparkfun.com/products/15663

**NeoPixels:**
- Product: LED - RGB Clear Common Cathode
- Various options available
- URL: https://www.sparkfun.com/categories/89

---

### Option 4: AliExpress (Budget Option - Slow Shipping)

**Warning:** 2-4 week shipping times, but cheapest prices

**ESP32 Board:** $3-5 each
- Search: "ESP32 WROOM Development Board"

**WS2812B:** $0.50-1 each
- Search: "WS2812B 5050 LED"

**Buttons:** $0.10-0.20 each
- Search: "12mm Push Button Switch"

**Buzzer:** $0.20-0.50 each
- Search: "5V Active Buzzer TMB12A05"

**Note:** Quality can be inconsistent; order extras

---

## 📝 Complete Kit Recommendations

### Starter Kit Option (Amazon):
Buy a complete ESP32 starter kit that includes many components:

**Search:** "ESP32 Starter Kit"
**Price:** $30-50
**Includes:**
- ESP32 board
- Breadboard
- Jumper wires
- LEDs (may need WS2812B separately)
- Resistors
- Buttons
- Various sensors

**Then add separately:**
- WS2812B NeoPixels
- Active buzzer

---

## 🔧 Tools Needed

### Essential:
- **Computer** with USB port
- **USB Cable** (micro-USB or USB-C depending on board)
- **Arduino IDE** (free download)

### Optional but Helpful:
- **Multimeter** ($15-30) - for troubleshooting
- **Wire Strippers** ($10-15) - if using solid core wire
- **Soldering Iron & Solder** ($20-40) - for permanent assembly
- **Helping Hands** ($10-15) - holds boards while soldering
- **Heat Shrink Tubing** ($10) - wire insulation
- **Label Maker** ($20+) - labeling buttons

---

## 🎨 3D Printing Requirements

If you plan to 3D print an enclosure:

### Filament:
- **Type:** PLA or PETG
- **Amount:** ~50-100g per enclosure
- **Colors:** 
  - White/light color for main body
  - Clear/translucent for LED windows
- **Cost:** $20-25 per 1kg spool (makes 10-20 enclosures)

### Printer Requirements:
- **Build volume:** 100mm x 100mm x 100mm minimum
- **Layer height:** 0.2mm standard
- **Supports:** Minimal if designed well
- **Infill:** 20% adequate

---

## 💰 Budget Breakdown

### Minimal Breadboard Setup (1 device):
| Category | Cost |
|----------|------|
| ESP32 + NeoPixels + Buttons + Buzzer | $12-18 |
| Resistors/capacitors/wires/breadboard | $5-11 |
| USB cable | $3-5 |
| **Total** | **$20-34** |

### Production Quality (1 device):
| Category | Cost |
|----------|------|
| Components | $12-18 |
| Supporting parts | $5-11 |
| Perfboard + soldering | $5-10 |
| 3D printed enclosure | $2-5 (material) |
| USB cable | $3-5 |
| **Total** | **$27-49** |

### Multiple Devices (4 devices):
| Category | Cost |
|----------|------|
| 4x Core components | $48-72 |
| Shared supplies (wires, resistors, tools) | $20-30 |
| 4x Enclosures | $8-20 (3D print) |
| **Total** | **$76-122** |
| **Per device** | **$19-30.50** |

---

## 🎁 Ready-Made Alternatives

If you prefer not to source individual components:

### ESP32 + NeoPixel Projects:
- **M5Stack** (ESP32 with built-in display)
  - ~$30-40
  - Would need external buttons
  - https://m5stack.com

- **ATOM Matrix** (ESP32 with 5x5 LED matrix)
  - ~$15
  - Could repurpose some LEDs
  - https://shop.m5stack.com/products/atom-matrix-esp32-development-kit

### Note:
These require modifying the code to work with different LED configurations.

---

## 📦 Recommended First Order

**If you've never worked with ESP32 before:**

1. **1x ESP32 Dev Board** ($10) - Amazon
2. **1x NeoPixel Strip** (1 meter, 30 LEDs) ($15) - Cut what you need
3. **1x Button Kit** (15-pack) ($3) - Various colors
4. **1x Active Buzzer 5-pack** ($6)
5. **1x Breadboard** ($4)
6. **1x Jumper Wire Kit** ($7)
7. **1x Component Kit** (resistors, caps, LEDs) ($12)

**Total: ~$57** - enough for 2-3 devices with spare parts

---

## ⚠️ Important Purchasing Notes

### ESP32 Board:
- **Ensure it has:** USB port, 3.3V regulator, reset button
- **Pin headers:** Pre-soldered is easier for beginners
- **Avoid:** "Bare" ESP32 modules without dev board

### WS2812B LEDs:
- **Voltage:** 5V (most common)
- **Type:** WS2812B or SK6812 (compatible)
- **Connection:** Need data, power, ground (3 wires minimum)
- **NOT:** WS2811 (different protocol)

### Buzzer:
- **ACTIVE buzzer:** Generates tone when powered (simpler)
- **NOT passive:** Requires PWM signal to generate tone
- **Marking:** Usually labeled "Active" or has component on back
- **Test:** Connect to 5V - should beep immediately

### Buttons:
- **Type:** Momentary (not latching)
- **Contact:** Normally Open (NO)
- **Size:** 6mm-12mm common, larger easier to press
- **Legs:** 2-pin or 4-pin (4-pin has duplicate connections)

---

## 🔄 Substitute Components

If you can't find exact components:

### NeoPixels:
- **WS2812B** = **SK6812** (compatible)
- Can use addressable LED strip instead of individual LEDs
- Can use Flora NeoPixels (sewable, larger)

### Buttons:
- Any momentary push button works
- Tactile switches (smaller)
- Panel mount buttons (bigger, nicer feel)
- Arcade buttons (fun but oversized)

### Buzzer:
- Piezo buzzer (passive) - requires code changes
- Mini speaker with amplifier - louder option
- Could omit buzzer entirely

---

## 🌟 Upgrade Options

Once you have the basic version working:

### Better Buttons:
- **Illuminated push buttons** ($3-5 each)
  - Built-in LED for visual feedback
  - Adds wiring complexity

### Better Enclosure:
- **Laser-cut acrylic** instead of 3D print
- **Injection molded** custom cases (expensive)
- **Hammond project boxes** with custom cutouts

### Battery Operation:
- **LiPo battery** (3.7V, 2000mAh) - $10-15
- **TP4056 charging module** - $1-2
- **Power switch** - $1-2

### Status Display:
- **OLED display** (0.96" 128x64) - $5-10
  - Shows time since last event
  - Shows exact percentages
  - Requires code additions

---

## ✅ Quality Check

When your parts arrive:

**ESP32:**
- [ ] Has USB port
- [ ] Powers on when connected
- [ ] Shows up as COM port on computer

**NeoPixels:**
- [ ] Has 4 pins (VCC, GND, DIN, DOUT)
- [ ] Not damaged/broken solder joints

**Buttons:**
- [ ] Click physically
- [ ] Normally open (multimeter test)

**Buzzer:**
- [ ] Has +/- markings
- [ ] Beeps when connected to 5V
- [ ] Is labeled "active" or has components on back

---

## 🆘 Return/Exchange

**Dead on Arrival (DOA):**
- ESP32 doesn't power on
- NeoPixels don't light up with known-good code
- Buttons don't register presses

**Amazon:** Usually easy returns within 30 days
**AliExpress:** Can be difficult, dispute process
**Adafruit/SparkFun:** Excellent customer service

---

## 📞 Support

If you need help identifying components:
- Post photos in Arduino forums
- Ask in ESP32 Discord/Reddit
- Contact seller with questions

Happy shopping! 🛒
