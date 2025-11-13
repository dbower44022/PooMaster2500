# Collar Display - Quick Reference Card

## 📱 WiFi & Server Setup

```cpp
// Edit these in collar_display.ino before uploading:

WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourWiFiPassword"  
API_HOST = "192.168.1.XXX"  // Your PC's IP address
```

**Find your PC's IP:** Open Command Prompt, type `ipconfig`, look for IPv4 Address

## 🔌 Wiring (Quick Version)

```
ESP32-C3 Pin → Connection
━━━━━━━━━━━━━━━━━━━━━━━━━━
GPIO8        → NeoPixel DIN (LED 1)
3.3V         → NeoPixel VCC (both LEDs)
GND          → NeoPixel GND (both LEDs)
LED 1 DOUT   → LED 2 DIN (chain LEDs)
```

**Don't forget:** 100µF capacitor between 3.3V and GND!

## 🔋 Battery Life Quick Math

| Battery | Runtime | Charge Time |
|---------|---------|-------------|
| 400mAh  | ~20hrs  | ~45min      |
| 600mAh  | ~30hrs  | ~1hr        |
| 1000mAh | ~50hrs  | ~1.5hrs     |

## 🚨 LED Status Indicators

| LED Pattern | Meaning |
|-------------|---------|
| Blue (solid) | Connecting to WiFi |
| Green (flash) | Successful update |
| Red (flash) | Error / Failed update |
| Orange (flash) | Low battery warning |
| Purple (fill) | OTA update in progress |
| Pee LED green-yellow-red | Normal status display |
| Poo LED green-yellow-red | Normal status display |
| Blinking on/off | Alarm triggered (90%+) |

## ⚙️ Default Settings

```
Update Interval: 60 seconds
Deep Sleep: Enabled (saves battery)
LED Brightness: 50/255 (~20%)
WiFi Timeout: 15 seconds
HTTP Timeout: 10 seconds
Alarm Blink Rate: 500ms (0.5 sec on/off)
OTA Password: puppy123 (CHANGE THIS!)
```

## 🔧 Common Tweaks

**Longer Battery Life:**
```cpp
#define UPDATE_INTERVAL_MS 120000  // 2 minutes
strip.setBrightness(30);           // Dimmer LEDs
```

**More Responsive (shorter battery):**
```cpp
#define UPDATE_INTERVAL_MS 30000   // 30 seconds
strip.setBrightness(100);          // Brighter LEDs
// enterDeepSleep();                 // Comment this out (line 452)
```

**Alarm Blink Speed:**
```cpp
#define ALARM_BLINK_INTERVAL_MS 300  // Faster (300ms)
#define ALARM_BLINK_INTERVAL_MS 1000 // Slower (1 sec)
```

## 📏 Recommended Component Sizes

**ESP32-C3 SuperMini:** 22.5 × 18 × 3.2mm
**Battery (602535):** 25 × 35 × 6mm  
**LEDs (5mm):** 5mm diameter each
**Total Assembly:** ~45 × 28 × 12mm

**Weight:** ~20g total (very light!)

## 🎯 Enclosure Must-Haves

✅ USB-C port hole (charging access)
✅ Two LED windows/light pipes
✅ Power switch hole
✅ Collar attachment (clip/velcro/loop)
✅ Wire strain relief
✅ Ventilation (optional but good)

**Suggested Material:** PETG or ABS
**Print Settings:** 0.2mm layers, 20% infill

## 🐛 Quick Troubleshooting

**No WiFi:**
- Check SSID/password spelling
- Ensure 2.4GHz WiFi (not 5GHz)
- Verify signal strength

**LEDs don't light:**
- Check 3.3V power to LEDs
- Verify GPIO8 connection
- Try different GPIO in code if needed

**Wrong colors:**
- LEDs might be RGB instead of GRB
- Change: `NEO_GRB` to `NEO_RGB` (line 52)

**Battery drains fast:**
- Verify deep sleep is enabled
- Check for shorts
- Lower LED brightness
- Increase update interval

**Device keeps resetting:**
- Add 100µF capacitor
- Check battery voltage (should be 3.3V+)
- Test with USB power only

## 📋 Pre-Flight Checklist

Before sealing enclosure:
- [ ] WiFi credentials correct in code
- [ ] Server IP address correct
- [ ] LEDs light up and show correct colors
- [ ] Battery charges via USB-C
- [ ] Switch controls power
- [ ] No hot components
- [ ] Deep sleep working (Serial Monitor shows message)
- [ ] OTA password changed
- [ ] Web interface matches LED colors

## 🎨 Color Reference

**Status Colors:**
- Green (0, 255, 0) = 0-60% of time elapsed
- Yellow (255, 255, 0) = 60-75% of time elapsed
- Orange (255, 128, 0) = 75-90% of time elapsed
- Red (255, 0, 0) = 90%+ ALARM!

These match the web interface exactly!

## 🔄 OTA Updates

**Update firmware wirelessly:**
1. Device must be on same network
2. In Arduino IDE: Tools → Port → "puppy-collar-display at X.X.X.X"
3. Upload new code (no USB cable needed!)
4. LEDs show purple progress bar

**OTA Credentials (CHANGE THESE!):**
- Hostname: puppy-collar-display
- Password: puppy123

## 📞 Serial Monitor Debugging

**Baud Rate:** 115200

**Normal Operation Messages:**
```
WiFi connected!
IP address: 192.168.1.XXX
Status updated successfully!
Pee: RGB(0,255,0)
Poo: RGB(0,255,0)
Entering deep sleep for 60 seconds...
```

**Error Messages:**
```
WiFi connection timeout!
HTTP request failed, error: -1
JSON parsing failed
Failed to fetch initial status
```

## ⚡ Power Draw Reference

**WiFi Active:** ~150mA
**Both LEDs Full:** ~120mA  
**Deep Sleep:** ~0.01mA
**Charging:** Red LED on board

## 🎁 Fun Customization Ideas

1. **Rainbow mode** - Cycle through colors slowly
2. **Breathing effect** - Pulse brightness up/down
3. **Different blink patterns** - Morse code, heartbeat, etc.
4. **Multi-device sync** - Flash all collars when alarm
5. **Custom colors** - Make your own color scheme
6. **Sound reactive** (add microphone) - Flash with barks

## 📖 File Locations in Project

```
collar_display.ino           ← Main firmware
COLLAR_HARDWARE_GUIDE.md     ← Complete build guide
COLLAR_QUICK_REFERENCE.md    ← This file!
```

## 💡 Pro Tips

1. **Test thoroughly on bench** before mounting on collar
2. **Use hot glue** for strain relief on wires
3. **Label your battery polarity** before soldering
4. **Keep a spare battery charged** for quick swaps
5. **Print extra enclosures** while you have the design loaded
6. **Take photos during build** to help with future repairs
7. **Monitor battery temp** during first few charges
8. **Use WiFi analyzer app** to check signal at collar height

## 🏆 Success Criteria

Your collar display is working perfectly when:
✅ LEDs match the web dashboard colors
✅ Colors transition smoothly (green → yellow → red)
✅ Blinks when alarm triggered (90%+)
✅ Lasts 24+ hours on battery
✅ Charges in ~1-2 hours
✅ Puppy doesn't notice/mind wearing it
✅ Updates every minute without fail
✅ Survives a full day of puppy activities

## 📚 Additional Resources

**ESP32-C3 Info:** docs.espressif.com/projects/esp-idf/en/latest/esp32c3/
**NeoPixel Guide:** learn.adafruit.com/adafruit-neopixel-uberguide
**LiPo Safety:** learn.adafruit.com/li-ion-and-lipoly-batteries

---

**Build Time:** 2-4 hours
**Skill Level:** Intermediate (soldering required)
**Cost:** $10-15 per device

**Have fun tracking your puppy! 🐕**
