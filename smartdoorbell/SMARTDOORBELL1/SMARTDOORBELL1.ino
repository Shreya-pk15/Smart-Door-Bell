#include "esp_camera.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// ===========================
// Camera Model: AI Thinker
// ===========================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35  
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ===========================
// Flash LED & Button Pins
// ===========================
#define LED_PIN     4      // Flash LED on AI Thinker board
#define BUTTON_PIN  13     // Push button to trigger camera

// ===========================
// WiFi Credentials
// ===========================
const char* ssid = "Salvatore";
const char* password = "0987654321";

// ===========================
// Flask + Ngrok Server URL
// ===========================
// Replace this each time you restart ngrok
const char* serverUrl = "https://pentapodic-macy-matrimonially.ngrok-free.dev/verify_face";

// ===========================
// Camera Initialization
// ===========================
void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 10000000; // 20 MHz is more stable
  config.frame_size   = FRAMESIZE_XGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.jpeg_quality = 8;
  config.fb_count     = 2;

  // config.frame_size = FRAMESIZE_XGA;  // 1600x1200 resolution
  // config.jpeg_quality = 8;             // Lower = better quality (but bigger size)
  // config.fb_count = 2;                 // Double buffer for stability


  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed (0x%x)\n", err);
    return;
  }
  Serial.println("Camera initialized successfully!");

  // Adjust sensor settings after init
  // sensor_t * s = esp_camera_sensor_get();
  // s->set_brightness(s, 1);
  // s->set_contrast(s, 1);
  // s->set_gain_ctrl(s, 1);
  // s->set_exposure_ctrl(s, 1);

  sensor_t *s = esp_camera_sensor_get();
  s->set_whitebal(s, 1);
  s->set_awb_gain(s, 1);
  s->set_brightness(s, 1);
  s->set_saturation(s, 0);
  s->set_contrast(s, 0);

}

// ===========================
// Send Image to Server
// ===========================
void sendImageToServer() {

  digitalWrite(LED_PIN, HIGH);
  delay(1000);  // warm-up for 1 second

  camera_fb_t* fb = esp_camera_fb_get();
  digitalWrite(LED_PIN, LOW);

  if (!fb) {
    Serial.println("Camera capture failed, retrying...");
    delay(500);
    fb = esp_camera_fb_get();
    if (!fb) {
      Serial.println("Still failed, skipping...");
      return;
    }
  }

  Serial.printf("Captured image (%d bytes)\n", fb->len);

  WiFiClientSecure client;
  client.setInsecure(); // ignore SSL certs
  HTTPClient http;

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected!");
    esp_camera_fb_return(fb);
    return;
  }

  http.begin(client, serverUrl); 
  http.addHeader("Content-Type", "image/jpeg"); 
  int httpResponseCode = http.POST(fb->buf, fb->len); 
  if (httpResponseCode > 0) { 
    String response = http.getString(); 
    Serial.printf("Response (%d): %s\n", httpResponseCode, response.c_str()); 
  } 
  else { 
    Serial.printf("HTTP POST failed, code: %d\n", httpResponseCode); 
  }

  http.end();
  esp_camera_fb_return(fb);
}

// ===========================
// Setup
// ===========================          
void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.println("\nConnecting to WiFi...");
  WiFi.begin(ssid, password);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 30) {
    delay(500);
    Serial.print(".");
    tries++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n WiFi connection failed!");
  }

  delay(1000);
  startCamera();
  Serial.println("System ready — press the doorbell button!");
}

// ===========================
// Doorbell Loop
// ===========================
void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println("\n Doorbell pressed! Sending image...");
    sendImageToServer();
    delay(3000);
  }
}
