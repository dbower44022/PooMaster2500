# ESP32 Puppy Tracker - Quick Start

## 🎯 What You Need to Do

### 1️⃣ Order Parts (~$20-35 per device)
See `ESP32_BOM.md` for complete shopping list.

**Minimum to get started:**
- ESP32-WROOM-32 dev board
- 2x WS2812B NeoPixel LEDs  
- 2x Push buttons
- 1x Active buzzer (5V)
- Jumper wires & breadboard
- 470Ω resistor for NeoPixels

### 2️⃣ Setup Arduino IDE
1. Install Arduino IDE 2.x
2. Add ESP32 board support
3. Install libraries:
   - WiFiManager (by tzapu)
   - Adafruit NeoPixel
   - ArduinoJson

See `ESP32_SETUP_GUIDE.md` for detailed instructions.

### 3️⃣ Wire It Up
```
GPIO 25 --[470Ω]-- NeoPixel #1 DIN -- NeoPixel #2 DIN
GPIO 32 ---------- Pee Button ------ GND
GPIO 33 ---------- Poo Button ------ GND  
GPIO 26 ---------- Buzzer (+) ------ Buzzer (-) to GND

Power:
3.3V ---- Both NeoPixels VCC
GND ----- All grounds together
```

### 4️⃣ Upload Code
1. Open `puppy_tracker_esp32.ino` in Arduino IDE
2. Select Board: "ESP32 Dev Module"
3. Select correct COM port
4. Click Upload
5. Watch Serial Monitor (115200 baud)

### 5️⃣ Configure WiFi
1. Connect to "PuppyTracker-Setup" WiFi network
2. Browser opens to config page (or go to 192.168.4.1)
3. Enter:
   - Your WiFi network & password
   - Server IP (from `ipconfig` on your PC)
   - Server Port (8000)
4. Save and device restarts

### 6️⃣ Test!
- Press Pee button → Short beep, LED updates
- Press Poo button → Short beep, LED updates
- Check Serial Monitor for status updates every 60 seconds
- If alarm condition → Buzzer chirps every 3 seconds

---

## 🎨 LED Colors

- 🟢 **Green** (0-60%): All good
- 🟡 **Yellow** (60-75%): Getting close  
- 🟠 **Orange** (75-90%): Take puppy out soon
- 🔴 **Red** (90%+): NEEDS ATTENTION NOW! + Chirping
- ⚪ **Flashing White**: Error (check Serial Monitor)

---

## 🔧 Common Issues

**LEDs don't work:**
- Check 470Ω resistor on data line
- Verify power/ground connections
- Make sure using WS2812B (not WS2811)

**Buttons don't work:**
- Ensure buttons connect pin to GND when pressed
- Check for good connections
- Try pressing harder (some buttons need force)

**Buzzer doesn't beep:**
- Verify it's an ACTIVE buzzer (not passive)
- Check polarity (+ to GPIO, - to GND)
- Test by connecting directly to 3.3V

**Can't upload code:**
- Hold BOOT button while clicking Upload
- Check USB cable (needs data pins)
- Install CH340/CP2102 driver if needed

**WiFi won't connect:**
- ESP32 only supports 2.4GHz (not 5GHz)
- Check WiFi password carefully
- Restart device and try config again

**White flashing (server error):**
- Verify server is running on your PC
- Check server IP is correct
- Make sure PC firewall allows port 8000
- Test server: open `http://[SERVER_IP]:8000/docs` in browser

---

## 📐 Wiring Diagram (Text)

```
                    ESP32-WROOM-32
                   ┌──────────────┐
                   │              │
    [Pee Button]───┤ GPIO 32      │
                   │              │
    [Poo Button]───┤ GPIO 33      │
                   │              │
    [470Ω]─LED1────┤ GPIO 25      │
            │      │              │
           LED2    │              │
                   │              │
    [Buzzer +]─────┤ GPIO 26      │
                   │              │
                   │ 3.3V ────────┼──── NeoPixels VCC
                   │              │
                   │ GND ─────────┼──── All grounds
                   │              │
                   └──────────────┘
                         │
                       [USB]
```

---

## 📝 Configuration Examples

### Home Network:
- **WiFi SSID:** "MyHomeWiFi"
- **WiFi Password:** "MyPassword123"
- **Server IP:** "192.168.1.100" ← Use `ipconfig` to find this
- **Server Port:** "8000"

### What the device does:
1. Polls server every 60 seconds: `GET http://192.168.1.100:8000/api/v1/status`
2. Gets RGB values for each LED
3. Updates NeoPixels with colors
4. Chirps buzzer if alarm flag is true

### When button pressed:
1. Beeps once (100ms)
2. Sends: `POST http://192.168.1.100:8000/api/v1/events`
   ```json
   {"event_type": "pee"}  // or "poo"
   ```
3. Waits 500ms
4. Fetches new status
5. Updates LEDs

---

## 🎓 Next Steps After Basic Testing

### Immediate:
- [x] Verify both LEDs work
- [x] Test both buttons log events
- [x] Confirm buzzer chirps during alarm
- [x] Check Serial Monitor shows status updates

### Short Term:
- [ ] Build permanent version on perfboard/PCB
- [ ] Design and 3D print enclosure  
- [ ] Label buttons clearly ("PEE" / "POO")
- [ ] Mount in convenient location
- [ ] Add power switch (optional)

### Long Term:
- [ ] Build multiple devices for different rooms
- [ ] Add battery power with charging
- [ ] Consider adding OLED display for status
- [ ] Integrate with Home Assistant
- [ ] Create custom PCB design

---

## 🐛 Debug Mode

To see more detailed output, change this line in code:
```cpp
// In setup(), before Serial.begin():
#define DEBUG_MODE  // Uncomment for verbose output
```

Or in Arduino IDE:
- Tools → Core Debug Level → "Debug"

This shows:
- Detailed HTTP responses
- WiFi connection steps
- JSON parsing details
- Timing information

---

## 📱 Remote Access

To access from your phone/tablet:
1. Make sure phone is on same WiFi network
2. Open web browser
3. Go to: `http://[SERVER_IP]:8000/index.html`
4. Can also log events from web interface

ESP32 and web interface work together, all data synced!

---

## 🔋 Power Options

### USB Power (Recommended for testing):
- Connect ESP32 to USB charger or computer
- 5V, 500mA minimum
- Always powered

### Battery Power:
- 3.7V LiPo battery (2000mAh+)
- Connect to 3.3V pin (NOT VIN)
- Add TP4056 charging module
- Lasts 10-14 hours typical

### Wall Power:
- USB wall adapter (5V, 1A)
- Long micro-USB cable
- Reliable 24/7 power

---

## 📞 Getting Help

**Serial Monitor shows errors?**
- Copy/paste the error output
- Note what you were doing when it happened
- Check if it's consistent or random

**Hardware not working?**
- Take clear photos of wiring
- Test each component individually
- Use multimeter to verify connections

**Code won't compile?**
- Check library versions installed
- Verify all libraries present
- Update ESP32 board package

**Need more help?**
- Arduino forums: https://forum.arduino.cc
- ESP32 Reddit: r/esp32
- Or just ask me! I'm here to help.

---

## ✨ Success Checklist

You know it's working when:
- ✅ Serial Monitor shows "✓ Setup complete!"
- ✅ LEDs show green (or current status color)
- ✅ Pressing button beeps and LED updates immediately  
- ✅ Status updates appear every 60 seconds in Serial Monitor
- ✅ Buzzer chirps when puppy needs to go out (90%+)
- ✅ Web interface shows matching status
- ✅ No white flashing errors

---

## 🎉 You're Ready!

Once everything works:
1. Mark this as done in your project tracker
2. Show it off to family/friends
3. Train everyone on how to press buttons
4. Start collecting data on your puppy's schedule
5. Plan your next device for another room!

The hardest part is over. Enjoy your automated puppy tracking! 🐕

---

**Files in this package:**
- `puppy_tracker_esp32.ino` - Main Arduino code
- `ESP32_SETUP_GUIDE.md` - Detailed setup instructions
- `ESP32_BOM.md` - Complete parts list with links
- `ESP32_QUICK_START.md` - This file

**Questions?** Just ask! 🚀
