/*
 * Puppy Bathroom Tracker - ESP32 Firmware
 * 
 * Hardware:
 * - ESP32-WROOM-32
 * - 2x WS2812B NeoPixel LEDs (Pee and Poo indicators)
 * - 2x Push buttons (Pee and Poo event logging)
 * - 1x Active buzzer (Alarm notification)
 * 
 * Features:
 * - WiFiManager for easy WiFi and server configuration
 * - Polls server every 60 seconds for status updates
 * - Button press triggers immediate status update with beep feedback
 * - Alarm chirps buzzer every 3 seconds
 * - Error states shown with white LED flash patterns
 * 
 * Libraries Required:
 * - WiFiManager by tzapu (https://github.com/tzapu/WiFiManager)
 * - Adafruit NeoPixel
 * - ArduinoJson (for parsing API responses)
 * - HTTPClient (built-in)
 * 
 * GPIO Pin Assignments (customize as needed):
 * - GPIO 25: NeoPixel Data (both LEDs on same data line)
 * - GPIO 32: Pee Button (pull-up with internal resistor)
 * - GPIO 33: Poo Button (pull-up with internal resistor)
 * - GPIO 26: Buzzer
 */

#include <WiFi.h>
#include <WiFiManager.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_NeoPixel.h>
#include <Preferences.h>

// ===== CONFIGURATION =====
// GPIO Pin Definitions
#define NEOPIXEL_PIN 25      // Data pin for NeoPixels
#define PEE_BUTTON_PIN 32    // Pee button (active LOW)
#define POO_BUTTON_PIN 33    // Poo button (active LOW)
#define BUZZER_PIN 26        // Active buzzer

// NeoPixel Configuration
#define NUM_PIXELS 2         // Number of NeoPixels (0=Pee, 1=Poo)
#define PEE_LED_INDEX 0      // Index of pee LED
#define POO_LED_INDEX 1      // Index of poo LED

// Timing Configuration
#define POLL_INTERVAL 60000      // Poll server every 60 seconds
#define BUTTON_DEBOUNCE 200      // Button debounce time (ms)
#define BUZZER_BEEP_DURATION 100 // Short beep duration (ms)
#define ALARM_CHIRP_INTERVAL 3000 // Chirp every 3 seconds during alarm

// WiFiManager Configuration
#define CONFIG_PORTAL_TIMEOUT 180 // 3 minutes

// ===== GLOBAL OBJECTS =====
Adafruit_NeoPixel pixels(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
WiFiManager wifiManager;
Preferences preferences;
HTTPClient http;

// ===== GLOBAL VARIABLES =====
// Server Configuration
String serverIP = "192.168.1.100";  // Default, will be configurable
int serverPort = 8000;              // Default port

// LED Status
struct LEDStatus {
  uint8_t r, g, b;
  bool alarm;
};
LEDStatus peeStatus = {0, 255, 0, false};  // Start green
LEDStatus pooStatus = {0, 255, 0, false};  // Start green

// Button State
unsigned long lastPeePress = 0;
unsigned long lastPooPress = 0;
bool peeButtonPressed = false;
bool pooButtonPressed = false;

// Timing
unsigned long lastPollTime = 0;
unsigned long lastAlarmChirp = 0;

// Error State
enum ErrorState {
  NO_ERROR,
  WIFI_ERROR,
  SERVER_ERROR,
  JSON_ERROR
};
ErrorState currentError = NO_ERROR;
unsigned long errorFlashTimer = 0;
bool errorFlashState = false;

// ===== FUNCTION DECLARATIONS =====
void setupWiFiManager();
void saveConfigCallback();
void checkButtons();
void logEvent(const char* eventType);
void updateStatus();
void handleAlarms();
void handleErrors();
void setLED(int index, uint8_t r, uint8_t g, uint8_t b);
void beep(int duration);
void chirp();
String getServerURL(const char* endpoint);

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=================================");
  Serial.println("Puppy Bathroom Tracker - ESP32");
  Serial.println("=================================\n");

  // Initialize preferences storage
  preferences.begin("puppy-tracker", false);
  serverIP = preferences.getString("serverIP", "192.168.1.100");
  serverPort = preferences.getInt("serverPort", 8000);

  // Initialize NeoPixels
  pixels.begin();
  pixels.setBrightness(128); // 50% brightness
  pixels.clear();
  pixels.show();
  Serial.println("✓ NeoPixels initialized");

  // Initialize buttons with internal pull-up resistors
  pinMode(PEE_BUTTON_PIN, INPUT_PULLUP);
  pinMode(POO_BUTTON_PIN, INPUT_PULLUP);
  Serial.println("✓ Buttons initialized");

  // Initialize buzzer
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  Serial.println("✓ Buzzer initialized");

  // Startup beep sequence
  beep(100);
  delay(100);
  beep(100);

  // Show startup pattern (blue)
  setLED(PEE_LED_INDEX, 0, 0, 255);
  setLED(POO_LED_INDEX, 0, 0, 255);
  pixels.show();

  // Setup WiFi with WiFiManager
  setupWiFiManager();

  // Initial status update
  Serial.println("\nFetching initial status...");
  updateStatus();

  Serial.println("\n✓ Setup complete! Device is ready.\n");
  beep(50);
  delay(100);
  beep(50);
  delay(100);
  beep(50);
}

// ===== MAIN LOOP =====
void loop() {
  unsigned long currentTime = millis();

  // Check for WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    currentError = WIFI_ERROR;
    handleErrors();
    delay(5000);
    ESP.restart(); // Restart to trigger WiFiManager
    return;
  }

  // Handle error display
  if (currentError != NO_ERROR) {
    handleErrors();
  }

  // Check buttons
  checkButtons();

  // Poll server for status updates
  if (currentTime - lastPollTime >= POLL_INTERVAL) {
    lastPollTime = currentTime;
    updateStatus();
  }

  // Handle alarm chirping
  handleAlarms();

  delay(10); // Small delay to prevent watchdog issues
}

// ===== WIFI MANAGER SETUP =====
void setupWiFiManager() {
  Serial.println("Starting WiFiManager...");

  // Set callback for when config is saved
  wifiManager.setSaveConfigCallback(saveConfigCallback);

  // Custom parameters for server configuration
  WiFiManagerParameter custom_server_ip("server_ip", "Server IP", serverIP.c_str(), 40);
  WiFiManagerParameter custom_server_port("server_port", "Server Port", String(serverPort).c_str(), 6);

  wifiManager.addParameter(&custom_server_ip);
  wifiManager.addParameter(&custom_server_port);

  // Set timeout for config portal
  wifiManager.setConfigPortalTimeout(CONFIG_PORTAL_TIMEOUT);

  // Try to connect to saved WiFi or start config portal
  if (!wifiManager.autoConnect("PuppyTracker-Setup")) {
    Serial.println("Failed to connect and hit timeout");
    delay(3000);
    ESP.restart();
  }

  // Save custom parameters
  serverIP = custom_server_ip.getValue();
  serverPort = String(custom_server_port.getValue()).toInt();

  // Store in preferences
  preferences.putString("serverIP", serverIP);
  preferences.putInt("serverPort", serverPort);

  Serial.println("✓ WiFi connected!");
  Serial.print("  IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("  Server: http://");
  Serial.print(serverIP);
  Serial.print(":");
  Serial.println(serverPort);
}

void saveConfigCallback() {
  Serial.println("Config saved!");
}

// ===== BUTTON HANDLING =====
void checkButtons() {
  unsigned long currentTime = millis();

  // Check Pee button (active LOW)
  if (digitalRead(PEE_BUTTON_PIN) == LOW && !peeButtonPressed) {
    if (currentTime - lastPeePress > BUTTON_DEBOUNCE) {
      peeButtonPressed = true;
      lastPeePress = currentTime;
      
      Serial.println("🔵 Pee button pressed!");
      beep(BUZZER_BEEP_DURATION);
      
      // Log event to server
      logEvent("pee");
      
      // Immediate status update
      delay(500); // Give server time to process
      updateStatus();
    }
  } else if (digitalRead(PEE_BUTTON_PIN) == HIGH) {
    peeButtonPressed = false;
  }

  // Check Poo button (active LOW)
  if (digitalRead(POO_BUTTON_PIN) == LOW && !pooButtonPressed) {
    if (currentTime - lastPooPress > BUTTON_DEBOUNCE) {
      pooButtonPressed = true;
      lastPooPress = currentTime;
      
      Serial.println("🟤 Poo button pressed!");
      beep(BUZZER_BEEP_DURATION);
      
      // Log event to server
      logEvent("poo");
      
      // Immediate status update
      delay(500); // Give server time to process
      updateStatus();
    }
  } else if (digitalRead(POO_BUTTON_PIN) == HIGH) {
    pooButtonPressed = false;
  }
}

// ===== API FUNCTIONS =====
void logEvent(const char* eventType) {
  if (WiFi.status() != WL_CONNECTED) {
    currentError = WIFI_ERROR;
    return;
  }

  String url = getServerURL("/api/v1/events");
  
  http.begin(url);
  http.addHeader("Content-Type", "application/json");

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["event_type"] = eventType;

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  Serial.print("Logging event: ");
  Serial.println(eventType);

  int httpResponseCode = http.POST(jsonPayload);

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.print("  Server response: ");
    Serial.println(response);
    currentError = NO_ERROR;
  } else {
    Serial.print("  Error: ");
    Serial.println(httpResponseCode);
    currentError = SERVER_ERROR;
  }

  http.end();
}

void updateStatus() {
  if (WiFi.status() != WL_CONNECTED) {
    currentError = WIFI_ERROR;
    return;
  }

  String url = getServerURL("/api/v1/status");
  
  http.begin(url);
  int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    String payload = http.getString();
    
    // Parse JSON response
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (error) {
      Serial.print("JSON parse error: ");
      Serial.println(error.c_str());
      currentError = JSON_ERROR;
      http.end();
      return;
    }

    // Extract pee status
    peeStatus.r = doc["pee"]["r"];
    peeStatus.g = doc["pee"]["g"];
    peeStatus.b = doc["pee"]["b"];
    peeStatus.alarm = doc["pee_alarm"];

    // Extract poo status
    pooStatus.r = doc["poo"]["r"];
    pooStatus.g = doc["poo"]["g"];
    pooStatus.b = doc["poo"]["b"];
    pooStatus.alarm = doc["poo_alarm"];

    // Update LEDs
    setLED(PEE_LED_INDEX, peeStatus.r, peeStatus.g, peeStatus.b);
    setLED(POO_LED_INDEX, pooStatus.r, pooStatus.g, pooStatus.b);
    pixels.show();

    // Debug output
    float peeTime = doc["pee_time_since"];
    float pooTime = doc["poo_time_since"];
    float peePct = doc["pee_percentage"];
    float pooPct = doc["poo_percentage"];

    Serial.println("\n--- Status Update ---");
    Serial.printf("Pee: RGB(%d,%d,%d) | %.1fh (%.0f%%) | Alarm: %s\n",
                  peeStatus.r, peeStatus.g, peeStatus.b,
                  peeTime, peePct,
                  peeStatus.alarm ? "YES" : "no");
    Serial.printf("Poo: RGB(%d,%d,%d) | %.1fh (%.0f%%) | Alarm: %s\n",
                  pooStatus.r, pooStatus.g, pooStatus.b,
                  pooTime, pooPct,
                  pooStatus.alarm ? "YES" : "no");
    Serial.println("---------------------\n");

    currentError = NO_ERROR;
  } else {
    Serial.print("Status fetch error: ");
    Serial.println(httpResponseCode);
    currentError = SERVER_ERROR;
  }

  http.end();
}

// ===== ALARM HANDLING =====
void handleAlarms() {
  unsigned long currentTime = millis();

  // Check if any alarm is active
  if (peeStatus.alarm || pooStatus.alarm) {
    // Chirp buzzer every 3 seconds
    if (currentTime - lastAlarmChirp >= ALARM_CHIRP_INTERVAL) {
      lastAlarmChirp = currentTime;
      chirp();
    }
  }
}

// ===== ERROR HANDLING =====
void handleErrors() {
  unsigned long currentTime = millis();

  // Flash white every 500ms to indicate error
  if (currentTime - errorFlashTimer >= 500) {
    errorFlashTimer = currentTime;
    errorFlashState = !errorFlashState;

    if (errorFlashState) {
      setLED(PEE_LED_INDEX, 255, 255, 255);
      setLED(POO_LED_INDEX, 255, 255, 255);
    } else {
      setLED(PEE_LED_INDEX, 0, 0, 0);
      setLED(POO_LED_INDEX, 0, 0, 0);
    }
    pixels.show();
  }

  // Print error message periodically
  static unsigned long lastErrorPrint = 0;
  if (currentTime - lastErrorPrint >= 5000) {
    lastErrorPrint = currentTime;
    Serial.print("ERROR: ");
    switch (currentError) {
      case WIFI_ERROR:
        Serial.println("WiFi disconnected");
        break;
      case SERVER_ERROR:
        Serial.println("Cannot reach server");
        break;
      case JSON_ERROR:
        Serial.println("Invalid server response");
        break;
      default:
        break;
    }
  }
}

// ===== HELPER FUNCTIONS =====
void setLED(int index, uint8_t r, uint8_t g, uint8_t b) {
  pixels.setPixelColor(index, pixels.Color(r, g, b));
}

void beep(int duration) {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(duration);
  digitalWrite(BUZZER_PIN, LOW);
}

void chirp() {
  // Short double beep pattern for alarms
  beep(80);
  delay(50);
  beep(80);
}

String getServerURL(const char* endpoint) {
  return "http://" + serverIP + ":" + String(serverPort) + String(endpoint);
}
