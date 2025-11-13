# ESP32 Puppy Tracker - Setup Guide

## 📦 Required Components

### For Each Device:
- **1x ESP32-WROOM-32 Development Board**
- **2x WS2812B NeoPixel LEDs** (individual LEDs, not strip)
- **2x Push Buttons** (momentary, normally open)
- **1x Active Buzzer** (5V)
- **2x 10kΩ Resistors** (for button pull-downs if not using internal pull-ups)
- **1x 470Ω Resistor** (for NeoPixel data line)
- **1x 1000µF Capacitor** (for NeoPixel power stability - optional but recommended)
- **Jumper wires**
- **Breadboard or perfboard**
- **USB cable** (for programming and power)

## 🔌 Wiring Diagram

### NeoPixel LEDs
```
ESP32 Pin 25 (NEOPIXEL_PIN) ---[470Ω]--- NeoPixel #1 DIN
                                           NeoPixel #1 DOUT --- NeoPixel #2 DIN
                                           
ESP32 3.3V ----------------+--------------- NeoPixel #1 VCC
                           |
                           +--------------- NeoPixel #2 VCC
                           |
                          [1000µF Cap]
                           |
ESP32 GND -----------------+--------------- NeoPixel #1 GND
                                        |
                                        +--- NeoPixel #2 GND
```

**Notes:**
- NeoPixels are daisy-chained (DOUT of first connects to DIN of second)
- First LED (index 0) = Pee indicator
- Second LED (index 1) = Poo indicator
- 470Ω resistor protects the data line
- Capacitor helps prevent power spikes when LEDs change

### Buttons
```
ESP32 Pin 32 (PEE_BUTTON) --- Button --- GND
ESP32 Pin 33 (POO_BUTTON) --- Button --- GND
```

**Notes:**
- Buttons connect pin to GND when pressed (active LOW)
- Internal pull-up resistors are enabled in code
- No external resistors needed if using internal pull-ups

### Buzzer
```
ESP32 Pin 26 (BUZZER_PIN) --- Active Buzzer (+) 
ESP32 GND -------------------- Active Buzzer (-)
```

**Notes:**
- Active buzzers have polarity (+ and -)
- They generate their own tone when powered
- No PWM needed for active buzzers

### Power
```
USB Cable --- ESP32 5V/VIN pin
          --- ESP32 GND
```

**Or for battery operation:**
```
3.7V LiPo --- ESP32 3.3V pin (regulated)
          --- ESP32 GND
```

## 🛠️ Arduino IDE Setup

### Step 1: Install Arduino IDE
1. Download from: https://www.arduino.cc/en/software
2. Install version 2.x or higher

### Step 2: Add ESP32 Board Support
1. Open Arduino IDE
2. Go to **File → Preferences**
3. In "Additional Boards Manager URLs" add:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Click **OK**
5. Go to **Tools → Board → Boards Manager**
6. Search for "esp32"
7. Install "esp32 by Espressif Systems" (version 2.0.0 or higher)

### Step 3: Install Required Libraries
Go to **Sketch → Include Library → Manage Libraries** and install:

1. **WiFiManager** by tzapu (version 2.0.16-rc.2 or higher)
   - Search: "WiFiManager"
   - Install: WiFiManager by tzapu

2. **Adafruit NeoPixel** (latest version)
   - Search: "Adafruit NeoPixel"
   - Install: Adafruit NeoPixel by Adafruit

3. **ArduinoJson** (version 6.x)
   - Search: "ArduinoJson"
   - Install: ArduinoJson by Benoit Blanchon

### Step 4: Configure Board Settings
1. Go to **Tools → Board** → Select "ESP32 Dev Module"
2. Set the following:
   - Upload Speed: 115200
   - CPU Frequency: 240MHz
   - Flash Frequency: 80MHz
   - Flash Mode: QIO
   - Flash Size: 4MB
   - Partition Scheme: Default 4MB with spiffs
   - Core Debug Level: None (or "Info" for debugging)
   - Port: Select your ESP32's COM port

## 📝 Upload Instructions

### First Time Upload:

1. **Connect ESP32** to computer via USB
2. **Open** `puppy_tracker_esp32.ino` in Arduino IDE
3. **Verify** the code compiles: Click ✓ (Verify button)
4. **Select** correct COM port: **Tools → Port → [Your ESP32 Port]**
5. **Upload**: Click → (Upload button)
6. **Wait** for "Done uploading" message

### Troubleshooting Upload Issues:

**"Failed to connect to ESP32"**
- Hold the "BOOT" button on ESP32 while clicking upload
- Release after "Connecting..." appears

**"Serial port not found"**
- Install CH340 or CP2102 USB driver (depends on your board)
- Try different USB cable (must be data cable, not charge-only)

## 🔧 Configuration

### First Boot - WiFi Setup:

1. **Power up** the ESP32
2. Look for WiFi network: **"PuppyTracker-Setup"**
3. **Connect** to it with your phone/computer
4. Browser should auto-open config page (or go to 192.168.4.1)
5. **Configure**:
   - Select your WiFi network
   - Enter WiFi password
   - Enter Server IP (your computer's IP where main.py runs)
   - Enter Server Port (default: 8000)
6. Click **Save**
7. Device will restart and connect to your WiFi

### Finding Your Server IP:

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter

**Example:**
- Server IP: 192.168.1.100
- Server Port: 8000

### Reconfiguring WiFi:

If you need to change settings:
1. Power on the device
2. Press and hold BOTH buttons (Pee + Poo) for 10 seconds
3. Device will restart into config mode
4. Connect to "PuppyTracker-Setup" again

*Note: This feature requires a small code modification - let me know if you want this added!*

## 🧪 Testing

### Serial Monitor Testing:

1. **Open** Serial Monitor: **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. You should see:
   ```
   =================================
   Puppy Bathroom Tracker - ESP32
   =================================
   
   ✓ NeoPixels initialized
   ✓ Buttons initialized
   ✓ Buzzer initialized
   Starting WiFiManager...
   ✓ WiFi connected!
   ```

### Hardware Testing:

1. **LEDs**: Should show blue during startup, then update to status colors
2. **Pee Button**: Press - should beep and LED updates
3. **Poo Button**: Press - should beep and LED updates
4. **Buzzer**: If alarm condition, chirps every 3 seconds

### LED Color Meanings:

- 🟢 **Green**: 0-60% of average time (all good)
- 🟡 **Yellow**: 60-75% (getting close)
- 🟠 **Orange**: 75-90% (should take puppy out soon)
- 🔴 **Red**: 90%+ (needs attention now!) + alarm chirps
- ⚪ **Flashing White**: Error condition (check serial monitor)

### Error Troubleshooting:

**Flashing White LEDs:**
- Check Serial Monitor for specific error
- Common causes:
  - Server not running
  - Wrong IP address configured
  - WiFi disconnected
  - Server not reachable

## 🎨 Customization

### Change GPIO Pins:
Edit these lines in the code:
```cpp
#define NEOPIXEL_PIN 25      // NeoPixel data pin
#define PEE_BUTTON_PIN 32    // Pee button
#define POO_BUTTON_PIN 33    // Poo button
#define BUZZER_PIN 26        // Buzzer pin
```

### Change Polling Interval:
```cpp
#define POLL_INTERVAL 60000  // 60 seconds (value in milliseconds)
```

### Change Brightness:
In `setup()` function:
```cpp
pixels.setBrightness(128); // 0-255, default is 128 (50%)
```

### Change Alarm Chirp Frequency:
```cpp
#define ALARM_CHIRP_INTERVAL 3000 // Every 3 seconds (in milliseconds)
```

## 🏗️ Enclosure Design

### Recommended Features:
- Two cutouts for LED visibility (clear/translucent)
- Two button holes labeled "PEE" and "POO"
- Small holes for buzzer sound
- USB port access for power
- Mounting holes or wall-mount bracket

### Dimensions:
- ESP32 board: ~55mm x 28mm
- Account for button height
- Leave space for wire routing

### 3D Printing Tips:
- Use PETG or ABS for durability
- Print LED windows in clear/translucent filament
- Consider printing buttons separately for better feel

## 📊 Expected Behavior

### Normal Operation:
1. Device boots → Blue LEDs briefly
2. Connects to WiFi → Status LEDs show current state
3. Updates every 60 seconds automatically
4. Button press → Beep → Immediate update

### Alarm State:
- LED turns red
- Buzzer chirps every 3 seconds (80ms beep, pause, 80ms beep)
- Continues until event is logged

### After Button Press:
1. Short beep confirms button press
2. Event sent to server
3. 500ms delay for server processing
4. Status fetched and LEDs update
5. If was in alarm, chirping stops

## 🔋 Power Consumption

### Typical Current Draw:
- ESP32 idle: ~80mA
- ESP32 WiFi active: ~120-160mA
- 2x NeoPixels (max brightness): ~120mA
- Buzzer active: ~30mA

### Battery Life Estimation:
With a 2000mAh battery:
- Idle: ~12-16 hours
- With frequent updates: ~10-14 hours
- Consider USB power or larger battery for 24/7 operation

## 🆘 Common Issues

### Issue: LEDs don't light up
**Solutions:**
- Check wiring (especially data line and ground)
- Verify 470Ω resistor on data line
- Check power connections
- Try different GPIO pin

### Issue: Buttons don't work
**Solutions:**
- Verify buttons are connected correctly (to ground)
- Check if button is normally-open type
- Test button with multimeter
- Try different GPIO pins

### Issue: Buzzer doesn't beep
**Solutions:**
- Check polarity (+ to GPIO, - to GND)
- Verify it's an active buzzer (not passive)
- Test with simple digitalWrite HIGH/LOW
- Check if buzzer is 3.3V or 5V compatible

### Issue: Can't connect to WiFi
**Solutions:**
- Reset WiFi settings (hold both buttons - if implemented)
- Check WiFi credentials
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)
- Check WiFi signal strength

### Issue: White flashing (server error)
**Solutions:**
- Verify server is running: `http://[SERVER_IP]:8000/docs`
- Check IP address configuration
- Ping server from another device
- Check firewall settings on server PC

## 📚 Additional Resources

- ESP32 Pinout: https://randomnerdtutorials.com/esp32-pinout-reference-gpios/
- NeoPixel Guide: https://learn.adafruit.com/adafruit-neopixel-uberguide
- WiFiManager Docs: https://github.com/tzapu/WiFiManager
- Arduino ESP32 Docs: https://docs.espressif.com/projects/arduino-esp32/

## ✅ Pre-Flight Checklist

Before deploying your device:

- [ ] All libraries installed
- [ ] Code compiles without errors
- [ ] Uploaded to ESP32 successfully
- [ ] WiFi credentials configured
- [ ] Server IP/port configured correctly
- [ ] Both LEDs working
- [ ] Both buttons working and logging events
- [ ] Buzzer chirping during alarms
- [ ] Serial monitor shows successful status updates
- [ ] No white flashing errors

## 🎯 Next Steps

Once your ESP32 device is working:
1. ✅ Test thoroughly with the web interface
2. ✅ Design and 3D print enclosure
3. ✅ Mount in convenient location
4. ✅ Train family members on button usage
5. ✅ Monitor serial output for a few days
6. ✅ Build additional devices for other rooms

Happy tracking! 🐕
