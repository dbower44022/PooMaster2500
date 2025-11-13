# Puppy Collar Display - Hardware Guide

## 🛒 Shopping List

### Essential Components

| Component | Specs | Quantity | Approx. Cost | Notes |
|-----------|-------|----------|--------------|-------|
| ESP32-C3 SuperMini | USB-C, built-in charging | 1 | $3-5 | Smallest ESP32-C3 board |
| WS2812B LEDs | 5mm through-hole or SMD | 2 | $0.50 | Individual LEDs or cut from strip |
| LiPo Battery | 3.7V, 500-1000mAh, JST connector | 1 | $5-8 | Higher mAh = longer runtime |
| Slide Switch | SPDT, miniature | 1 | $0.50 | Power on/off |
| Capacitor | 100µF, 6.3V+ | 1 | $0.10 | NeoPixel stability |
| Wire | 28-30 AWG, silicone | 1ft | $1 | Flexible for small space |

**Total Cost: ~$10-15 per device**

### Recommended Specific Products

**ESP32-C3 SuperMini:**
- Search: "ESP32-C3 SuperMini" on AliExpress/Amazon
- Features: Built-in USB-C, TP4056 charging, very small (22.52×18mm)
- Alternative: Seeed XIAO ESP32-C3 (slightly more expensive but excellent)

**NeoPixels:**
- Through-hole: WS2812B 5mm diffused LEDs
- SMD option: WS2812-2020 (ultra-compact 2x2mm)
- Strip alternative: Cut 2 LEDs from WS2812B strip

**Battery:**
- Recommended: 602535 LiPo (600mAh, 25×35×6mm)
- Smaller option: 401030 LiPo (40mAh, 10×30×4mm) - 4-8 hour runtime
- Larger option: 802540 LiPo (1000mAh) - longer runtime but bigger

## 📐 Physical Specifications

### ESP32-C3 SuperMini Board
- Dimensions: 22.52mm × 18mm × 3.2mm
- Weight: ~2g
- Has built-in USB-C charging circuit
- JST 1.25mm battery connector

### Complete Assembly Size Estimate
- Length: ~40-50mm
- Width: ~25-30mm  
- Thickness: ~10-15mm (including battery)
- Total Weight: ~15-25g (depending on battery)

**Note:** This is very light! Most collars can handle this easily.

## 🔧 Wiring Diagram

```
ESP32-C3 SuperMini Pinout:
┌─────────────────────┐
│     USB-C Port      │
├─────────────────────┤
│  5V  GND  3V3       │  ← Power
│  0   1   2   3      │  ← GPIO (use GPIO8 for NeoPixels)
│  4   5   6   7      │
│  8   9   10  20 21  │
│  RST EN  GND BAT    │  ← BAT for battery monitoring
└─────────────────────┘

Connection Diagram:
                    
ESP32-C3                WS2812B LEDs
  GPIO8  ────────────→  DIN (LED 1) ──→ DOUT ──→ DIN (LED 2)
  3.3V   ────────────→  VCC (both LEDs in parallel)
  GND    ────────────→  GND (both LEDs in parallel)
  
  BAT+   ───┬───────→  LiPo +
            │
         [Switch]
            │
  BAT-   ───┴───────→  LiPo -

Add 100µF capacitor between VCC and GND near LEDs for stability
```

## ⚡ Power Consumption & Battery Life

### Current Draw Estimates

**Active Mode (WiFi + LEDs):**
- ESP32-C3 WiFi active: ~100-160mA
- Both LEDs full brightness: ~120mA (60mA each)
- **Total: ~220-280mA**

**Deep Sleep Mode:**
- ESP32-C3 deep sleep: ~5-10µA
- LEDs off: 0mA
- **Total: ~0.01mA**

### Battery Life Calculation

**With 60-second deep sleep cycle:**
- Active time: ~3-5 seconds per minute (WiFi + update)
- Sleep time: ~55-57 seconds per minute
- Average current: ~15-25mA

**Expected Battery Life:**
| Battery Size | Capacity | Runtime |
|--------------|----------|---------|
| 400mAh | 400mAh | ~16-24 hours |
| 600mAh | 600mAh | ~24-36 hours |
| 1000mAh | 1000mAh | ~40-60 hours |

**Note:** Actual runtime varies with WiFi signal strength and alarm frequency.

## 🏗️ Assembly Instructions

### Step 1: Prepare Components
1. If using LED strip, carefully cut 2 LEDs with ~10mm wire leads
2. Tin all wire ends and component leads
3. Test ESP32-C3 board by uploading blink sketch

### Step 2: Solder NeoPixels
1. Connect first LED:
   - DIN → GPIO8 on ESP32-C3
   - VCC → 3.3V
   - GND → GND

2. Chain second LED:
   - DOUT from LED 1 → DIN of LED 2
   - VCC → 3.3V (parallel with LED 1)
   - GND → GND (parallel with LED 1)

3. Add 100µF capacitor across VCC/GND near LEDs

### Step 3: Battery Connection
1. Solder switch inline with battery negative wire
2. Connect battery JST connector to board
3. **Important:** Keep switch OFF during programming

### Step 4: Test Before Enclosing
1. Upload the firmware with your WiFi credentials
2. Power on and verify:
   - Blue LEDs during WiFi connection
   - Green flash on successful API fetch
   - LEDs show current pee/poo status
   - Red flash if error occurs

### Step 5: Enclosure
See 3D printing section below for enclosure design.

## 🔋 Charging Instructions

1. **Power off** the device using the switch (important!)
2. Connect USB-C cable to ESP32-C3 board
3. Red LED on board = charging
4. Blue/Green LED on board = fully charged
5. Typical charge time: 1-2 hours (depending on battery size)
6. Do not charge unattended initially

## 💻 Firmware Upload Instructions

### Required Arduino Libraries
Install via Arduino Library Manager:
- ESP32 board support (by Espressif)
- Adafruit NeoPixel
- ArduinoJson (v6.x)

### Upload Steps
1. Open `collar_display.ino` in Arduino IDE
2. **Configure your settings** (lines 29-37):
   ```cpp
   const char* WIFI_SSID = "YOUR_WIFI_SSID";
   const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
   const char* API_HOST = "192.168.1.100";  // Your server IP
   ```
3. Select board: **ESP32C3 Dev Module**
4. Select port (COM port for your device)
5. Click Upload
6. Open Serial Monitor (115200 baud) to verify operation

### Finding Your Server IP Address
On Windows (where server runs):
```cmd
ipconfig
```
Look for "IPv4 Address" under your WiFi adapter (e.g., 192.168.1.100)

## 📦 3D Printed Enclosure Design

### Design Requirements
- **Dimensions:** ~45×28×12mm (adjust for your components)
- **Features needed:**
  - USB-C port access for charging
  - Two light pipes or clear windows for LEDs
  - Power switch access
  - Mounting clips for collar attachment
  - Wire strain relief

### Recommended Enclosure Style
```
Top View:
┌─────────────────────────┐
│  [LED1]        [LED2]   │  ← Light pipes/windows
│                         │
│    ┌───────────┐        │
│    │  ESP32-C3 │        │
│    └───────────┘        │
│      [Battery]          │
│                  [SW]   │  ← Power switch
└─────────────────────────┘

Side View:
    ┌─────────┐
    │  ○   ○  │  ← LEDs visible
    ├─────────┤
    │▓▓▓▓▓▓▓▓▓│  ← Electronics
    │░░░░░░░░░│  ← Battery
    └─────────┘
     [Clip]      ← Collar attachment
```

### Collar Attachment Options

**Option 1: Slide Clip**
- Print a clip that slides onto collar webbing
- Typical collar width: 15-25mm
- Allows easy removal for charging

**Option 2: Velcro Strap**
- Small velcro loop that wraps around collar
- Most flexible option
- Easy removal

**Option 3: Carabiner Mount**
- Print a loop to attach small carabiner
- Clips to collar D-ring
- May dangle depending on design

### Printing Tips
- Material: PETG or ABS (more durable than PLA)
- Layer height: 0.2mm
- Infill: 20-30%
- Print light pipes or LED windows separately in clear/translucent filament
- Consider printing in fun colors!

### Light Pipe Design
For best LED visibility:
- 3-5mm diameter clear channel from LED to surface
- Flared or diffused end for wide viewing angle
- Consider printing separate clear inserts

## 🧪 Testing & Calibration

### Initial Testing Checklist
- [ ] LEDs light up correctly
- [ ] WiFi connects successfully  
- [ ] API data fetches properly
- [ ] Battery charges via USB-C
- [ ] Switch controls power
- [ ] No shorts or hot components
- [ ] LEDs match web interface colors
- [ ] Deep sleep works (current drops)
- [ ] Alarm blink functions
- [ ] OTA update works (optional)

### Troubleshooting

**LEDs don't light up:**
- Check power (3.3V at LED VCC pins)
- Verify GPIO8 is correct pin
- Check data line continuity
- Try reducing strip.setBrightness() value

**WiFi won't connect:**
- Double-check SSID and password
- Verify 2.4GHz WiFi (ESP32-C3 doesn't support 5GHz)
- Check WiFi signal strength where collar will be
- Try a different WiFi channel

**Wrong colors:**
- Verify LED wiring (DIN direction)
- Check if LEDs are RGB vs GRB (code uses GRB)
- Test with known good colors

**Battery drains too fast:**
- Verify deep sleep is working (Serial Monitor should show sleep message)
- Check for shorts or excessive current draw
- Reduce LED brightness in code
- Increase UPDATE_INTERVAL_MS

**Device keeps resetting:**
- Add/verify 100µF capacitor near LEDs
- Check battery voltage
- Verify adequate power supply
- Check for loose connections

## 🎨 Customization Options

### Adjust LED Brightness
In the code (line 286):
```cpp
strip.setBrightness(50);  // 0-255, default is 50
```
Lower = longer battery life
Higher = better visibility

### Change Update Interval
In the code (line 42):
```cpp
#define UPDATE_INTERVAL_MS 60000  // milliseconds
```
- 30000 = 30 seconds (more updates, shorter battery)
- 60000 = 60 seconds (default, balanced)
- 120000 = 2 minutes (longer battery)

### Disable Deep Sleep
Comment out line 452:
```cpp
// enterDeepSleep();
```
Device will stay awake constantly. Reduces battery life significantly but updates more smoothly.

### LED Effects
Modify `updateLEDs()` function to add:
- Breathing effects
- Rainbow cycling
- Different blink patterns
- Brightness ramping

## 📏 Size Comparison
- **This collar device:** ~45×28×12mm, ~20g
- **AirTag:** 31.9×31.9×8mm, 11g (for reference)
- **Fitbit tracker:** ~35×20×12mm, ~15-20g

Your collar device will be comparable in size/weight to common wearables!

## 🔒 Safety Considerations

1. **Weatherproofing:** 
   - Use conformal coating on electronics
   - Consider IP65-rated enclosure
   - Keep USB port covered when not charging

2. **Chew Protection:**
   - Use durable enclosure material
   - Place on back of collar (not front where puppy can reach)
   - Monitor initially to ensure puppy doesn't chew

3. **Collar Placement:**
   - Don't obstruct ID tags
   - Keep away from buckle/adjustment areas
   - Ensure doesn't interfere with leash attachment

4. **Battery Safety:**
   - Never puncture LiPo battery
   - Don't charge unattended initially
   - Replace if battery swells or damages
   - Dispose of properly if damaged

## 🚀 Ready to Build!

You now have everything needed to build the collar display:
- ✅ Complete parts list
- ✅ Wiring diagram  
- ✅ Firmware code
- ✅ Assembly instructions
- ✅ Enclosure design specs

**Next steps:**
1. Order components (1-2 weeks for shipping)
2. While waiting, design/print enclosure
3. Test firmware on ESP32-C3 board
4. Assemble and test
5. Mount on collar and enjoy!

**Estimated build time:** 2-4 hours (not including component shipping)
