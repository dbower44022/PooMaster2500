/*
 * Puppy Bathroom Tracker - Collar Display Device
 * ESP32-C3 with 2 NeoPixels (WS2812B)
 * 
 * Features:
 * - Polls API server every 60 seconds
 * - Updates 2 LEDs (pee/poo status)
 * - Deep sleep for battery optimization
 * - OTA update support
 * - Battery monitoring
 * 
 * Hardware:
 * - ESP32-C3 (SuperMini or similar small board)
 * - 2x WS2812B NeoPixels
 * - LiPo battery (500-1000mAh)
 * - TP4056 charging module (built into many C3 boards)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <esp_sleep.h>
#include <ArduinoOTA.h>

// ===== CONFIGURATION - CHANGE THESE =====

// WiFi Settings
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Server Settings
const char* API_HOST = "192.168.1.100";  // Your server's IP address
const int API_PORT = 8000;
const char* API_ENDPOINT = "/api/v1/status";

// Hardware Pins
#define NEOPIXEL_PIN 8        // GPIO pin for NeoPixels (change if needed)
#define NEOPIXEL_COUNT 2      // 2 LEDs total
#define PEE_LED_INDEX 0       // First LED for pee status
#define POO_LED_INDEX 1       // Second LED for poo status
#define BATTERY_PIN 0         // ADC pin for battery monitoring (GPIO0/ADC1_CH0)

// Timing Settings
#define UPDATE_INTERVAL_MS 60000      // Poll server every 60 seconds
#define WIFI_TIMEOUT_MS 15000         // WiFi connection timeout
#define HTTP_TIMEOUT_MS 10000         // HTTP request timeout
#define ALARM_BLINK_INTERVAL_MS 500   // Blink speed when alarm triggered
#define SLEEP_DURATION_US 60000000    // Deep sleep for 60 seconds (60s * 1,000,000 µs/s)

// Battery Settings
#define BATTERY_FULL_VOLTAGE 4.2      // Fully charged LiPo
#define BATTERY_EMPTY_VOLTAGE 3.3     // Empty LiPo (with protection)
#define LOW_BATTERY_THRESHOLD 3.4     // Show low battery warning

// ===== GLOBAL OBJECTS =====
Adafruit_NeoPixel strip(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
HTTPClient http;
WiFiClient client;

// ===== STATUS STRUCTURE =====
struct Status {
  struct Color {
    uint8_t r;
    uint8_t g;
    uint8_t b;
  };
  
  Color pee;
  Color poo;
  bool pee_alarm;
  bool poo_alarm;
  float pee_time_since;
  float poo_time_since;
  float pee_percentage;
  float poo_percentage;
};

Status currentStatus;
unsigned long lastUpdate = 0;
bool otaInProgress = false;

// ===== BATTERY MONITORING =====
float getBatteryVoltage() {
  // Read battery voltage through voltage divider
  // Adjust multiplier based on your voltage divider resistors
  // Standard ESP32-C3 boards often have built-in divider
  int rawValue = analogRead(BATTERY_PIN);
  float voltage = (rawValue / 4095.0) * 3.3 * 2;  // Assuming 1:1 voltage divider
  return voltage;
}

int getBatteryPercentage() {
  float voltage = getBatteryVoltage();
  
  if (voltage >= BATTERY_FULL_VOLTAGE) return 100;
  if (voltage <= BATTERY_EMPTY_VOLTAGE) return 0;
  
  float percentage = ((voltage - BATTERY_EMPTY_VOLTAGE) / 
                      (BATTERY_FULL_VOLTAGE - BATTERY_EMPTY_VOLTAGE)) * 100;
  return constrain((int)percentage, 0, 100);
}

bool isLowBattery() {
  return getBatteryVoltage() < LOW_BATTERY_THRESHOLD;
}

// ===== WIFI FUNCTIONS =====
bool connectWiFi() {
  Serial.println("Connecting to WiFi...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  unsigned long startAttempt = millis();
  while (WiFi.status() != WL_CONNECTED) {
    if (millis() - startAttempt >= WIFI_TIMEOUT_MS) {
      Serial.println("WiFi connection timeout!");
      return false;
    }
    delay(100);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal strength: ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
  
  return true;
}

// ===== API FUNCTIONS =====
bool fetchStatus() {
  String url = String("http://") + API_HOST + ":" + API_PORT + API_ENDPOINT;
  
  Serial.print("Fetching status from: ");
  Serial.println(url);
  
  http.begin(client, url);
  http.setTimeout(HTTP_TIMEOUT_MS);
  
  int httpCode = http.GET();
  
  if (httpCode != HTTP_CODE_OK) {
    Serial.print("HTTP request failed, error: ");
    Serial.println(httpCode);
    http.end();
    return false;
  }
  
  String payload = http.getString();
  http.end();
  
  // Parse JSON response
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload);
  
  if (error) {
    Serial.print("JSON parsing failed: ");
    Serial.println(error.c_str());
    return false;
  }
  
  // Extract data
  currentStatus.pee.r = doc["pee"]["r"];
  currentStatus.pee.g = doc["pee"]["g"];
  currentStatus.pee.b = doc["pee"]["b"];
  
  currentStatus.poo.r = doc["poo"]["r"];
  currentStatus.poo.g = doc["poo"]["g"];
  currentStatus.poo.b = doc["poo"]["b"];
  
  currentStatus.pee_alarm = doc["pee_alarm"];
  currentStatus.poo_alarm = doc["poo_alarm"];
  
  currentStatus.pee_time_since = doc["pee_time_since"];
  currentStatus.poo_time_since = doc["poo_time_since"];
  
  currentStatus.pee_percentage = doc["pee_percentage"];
  currentStatus.poo_percentage = doc["poo_percentage"];
  
  Serial.println("Status updated successfully!");
  Serial.printf("Pee: RGB(%d,%d,%d) %s\n", 
                currentStatus.pee.r, currentStatus.pee.g, currentStatus.pee.b,
                currentStatus.pee_alarm ? "[ALARM]" : "");
  Serial.printf("Poo: RGB(%d,%d,%d) %s\n", 
                currentStatus.poo.r, currentStatus.poo.g, currentStatus.poo.b,
                currentStatus.poo_alarm ? "[ALARM]" : "");
  
  return true;
}

// ===== LED FUNCTIONS =====
void updateLEDs(bool blinkState = false) {
  // If alarm is active and blink state is off, turn LED off
  if (currentStatus.pee_alarm && !blinkState) {
    strip.setPixelColor(PEE_LED_INDEX, 0, 0, 0);
  } else {
    strip.setPixelColor(PEE_LED_INDEX, 
                       currentStatus.pee.r, 
                       currentStatus.pee.g, 
                       currentStatus.pee.b);
  }
  
  if (currentStatus.poo_alarm && !blinkState) {
    strip.setPixelColor(POO_LED_INDEX, 0, 0, 0);
  } else {
    strip.setPixelColor(POO_LED_INDEX, 
                       currentStatus.poo.r, 
                       currentStatus.poo.g, 
                       currentStatus.poo.b);
  }
  
  strip.show();
}

void showLowBattery() {
  // Flash both LEDs orange to indicate low battery
  for (int i = 0; i < 5; i++) {
    strip.setPixelColor(PEE_LED_INDEX, 255, 128, 0);
    strip.setPixelColor(POO_LED_INDEX, 255, 128, 0);
    strip.show();
    delay(200);
    
    strip.setPixelColor(PEE_LED_INDEX, 0, 0, 0);
    strip.setPixelColor(POO_LED_INDEX, 0, 0, 0);
    strip.show();
    delay(200);
  }
}

void showWiFiConnecting() {
  // Pulse blue while connecting to WiFi
  strip.setPixelColor(PEE_LED_INDEX, 0, 0, 255);
  strip.setPixelColor(POO_LED_INDEX, 0, 0, 255);
  strip.show();
}

void showError() {
  // Flash both LEDs red to indicate error
  for (int i = 0; i < 3; i++) {
    strip.setPixelColor(PEE_LED_INDEX, 255, 0, 0);
    strip.setPixelColor(POO_LED_INDEX, 255, 0, 0);
    strip.show();
    delay(200);
    
    strip.setPixelColor(PEE_LED_INDEX, 0, 0, 0);
    strip.setPixelColor(POO_LED_INDEX, 0, 0, 0);
    strip.show();
    delay(200);
  }
}

void showSuccess() {
  // Quick green flash to indicate successful update
  strip.setPixelColor(PEE_LED_INDEX, 0, 255, 0);
  strip.setPixelColor(POO_LED_INDEX, 0, 255, 0);
  strip.show();
  delay(100);
}

void ledsOff() {
  strip.setPixelColor(PEE_LED_INDEX, 0, 0, 0);
  strip.setPixelColor(POO_LED_INDEX, 0, 0, 0);
  strip.show();
}

// ===== OTA UPDATE FUNCTIONS =====
void setupOTA() {
  ArduinoOTA.setHostname("puppy-collar-display");
  ArduinoOTA.setPassword("puppy123");  // Change this!
  
  ArduinoOTA.onStart([]() {
    otaInProgress = true;
    Serial.println("OTA Update Starting...");
    ledsOff();
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("\nOTA Update Complete!");
    showSuccess();
    otaInProgress = false;
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    int percentage = (progress / (total / 100));
    Serial.printf("Progress: %u%%\r", percentage);
    
    // Show progress on LEDs (0-50% = pee LED, 51-100% = poo LED)
    if (percentage <= 50) {
      int brightness = map(percentage, 0, 50, 0, 255);
      strip.setPixelColor(PEE_LED_INDEX, brightness, 0, brightness);
      strip.setPixelColor(POO_LED_INDEX, 0, 0, 0);
    } else {
      strip.setPixelColor(PEE_LED_INDEX, 255, 0, 255);
      int brightness = map(percentage, 51, 100, 0, 255);
      strip.setPixelColor(POO_LED_INDEX, brightness, 0, brightness);
    }
    strip.show();
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("Auth Failed");
    else if (error == OTA_BEGIN_ERROR) Serial.println("Begin Failed");
    else if (error == OTA_CONNECT_ERROR) Serial.println("Connect Failed");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("Receive Failed");
    else if (error == OTA_END_ERROR) Serial.println("End Failed");
    showError();
    otaInProgress = false;
  });
  
  ArduinoOTA.begin();
  Serial.println("OTA Ready");
}

// ===== DEEP SLEEP FUNCTIONS =====
void enterDeepSleep() {
  Serial.println("Entering deep sleep for 60 seconds...");
  
  // Turn off LEDs
  ledsOff();
  
  // Disconnect WiFi to save power
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  
  // Configure deep sleep
  esp_sleep_enable_timer_wakeup(SLEEP_DURATION_US);
  
  // Enter deep sleep
  esp_deep_sleep_start();
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n=================================");
  Serial.println("Puppy Collar Display Starting...");
  Serial.println("=================================");
  
  // Initialize NeoPixels
  strip.begin();
  strip.setBrightness(50);  // 50/255 brightness for battery life
  strip.show();
  
  // Check battery
  float voltage = getBatteryVoltage();
  int batteryPct = getBatteryPercentage();
  Serial.printf("Battery: %.2fV (%d%%)\n", voltage, batteryPct);
  
  if (isLowBattery()) {
    Serial.println("WARNING: Low battery!");
    showLowBattery();
  }
  
  // Connect to WiFi
  showWiFiConnecting();
  if (!connectWiFi()) {
    Serial.println("Failed to connect to WiFi");
    showError();
    delay(2000);
    enterDeepSleep();
    return;
  }
  
  // Setup OTA
  setupOTA();
  
  // Fetch initial status
  if (!fetchStatus()) {
    Serial.println("Failed to fetch initial status");
    showError();
    delay(2000);
    enterDeepSleep();
    return;
  }
  
  showSuccess();
  delay(500);
  updateLEDs();
  
  lastUpdate = millis();
  Serial.println("Setup complete!");
}

// ===== MAIN LOOP =====
void loop() {
  // Handle OTA updates
  ArduinoOTA.handle();
  
  // If OTA is in progress, don't do anything else
  if (otaInProgress) {
    delay(10);
    return;
  }
  
  // Handle alarm blinking
  static unsigned long lastBlink = 0;
  static bool blinkState = false;
  
  if (currentStatus.pee_alarm || currentStatus.poo_alarm) {
    if (millis() - lastBlink >= ALARM_BLINK_INTERVAL_MS) {
      blinkState = !blinkState;
      updateLEDs(blinkState);
      lastBlink = millis();
    }
  }
  
  // Check if it's time to update
  if (millis() - lastUpdate >= UPDATE_INTERVAL_MS) {
    Serial.println("\n--- Update Cycle ---");
    
    // Reconnect WiFi if needed
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi disconnected, reconnecting...");
      if (!connectWiFi()) {
        showError();
        delay(2000);
        enterDeepSleep();
        return;
      }
    }
    
    // Fetch new status
    if (fetchStatus()) {
      showSuccess();
      delay(100);
      updateLEDs();
    } else {
      showError();
    }
    
    lastUpdate = millis();
    
    // Enter deep sleep to save battery
    // Comment out the next line if you want continuous operation
    enterDeepSleep();
  }
  
  delay(10);  // Small delay to prevent watchdog issues
}
