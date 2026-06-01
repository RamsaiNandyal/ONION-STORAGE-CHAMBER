#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <DHT.h>

// ===== WIFI (USE YOUR WORKING HOTSPOT) =====
const char* ssid = "NodeMCU";
const char* password = "123456789";

// ===== SERVER (YOUR LAPTOP IP) =====
const char* server = "http://10.50.45.37:5000/data";

// ===== SENSOR PINS =====
#define DHTPIN D4
#define DHTTYPE DHT11
#define MQ2_PIN A0

// ===== OUTPUT PINS =====
#define RELAY_HUMIDIFIER D2
#define LED_GREEN D5
#define LED_YELLOW D6
#define LED_RED D7

DHT dht(DHTPIN, DHTTYPE);

// ===== THRESHOLDS =====
int gasLow = 200;
int gasMedium = 400;

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n===== SYSTEM STARTED =====");

  dht.begin();

  pinMode(RELAY_HUMIDIFIER, OUTPUT);
  pinMode(LED_GREEN, OUTPUT);
  pinMode(LED_YELLOW, OUTPUT);
  pinMode(LED_RED, OUTPUT);

  digitalWrite(RELAY_HUMIDIFIER, HIGH); // OFF

  // ===== WIFI CONNECT =====
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// ===== LOOP =====
void loop() {

  float temp = dht.readTemperature();
  float humidity = dht.readHumidity();
  int gas = analogRead(MQ2_PIN);

  // ===== SENSOR CHECK =====
  if (isnan(temp) || isnan(humidity)) {
    Serial.println("❌ DHT Error!");
    delay(2000);
    return;
  }

  Serial.println("\n------ SENSOR DATA ------");
  Serial.print("Temp: ");
  Serial.print(temp);
  Serial.print(" °C | Humidity: ");
  Serial.print(humidity);
  Serial.print(" % | Gas: ");
  Serial.println(gas);

  // ===== CONTROL LOGIC =====
  if (gas < gasLow) {
    Serial.println("STATUS: SAFE");

    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, LOW);

    digitalWrite(RELAY_HUMIDIFIER, HIGH); // OFF
  }
  else if (gas < gasMedium) {
    Serial.println("STATUS: WARNING");

    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, HIGH);
    digitalWrite(LED_RED, LOW);

    digitalWrite(RELAY_HUMIDIFIER, LOW); // ON
  }
  else {
    Serial.println("STATUS: DANGER");

    digitalWrite(LED_GREEN, LOW);
    digitalWrite(LED_YELLOW, LOW);
    digitalWrite(LED_RED, HIGH);

    digitalWrite(RELAY_HUMIDIFIER, LOW); // ON
  }

  // ===== SEND DATA TO FLASK =====
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;

    http.begin(client, server);
    http.addHeader("Content-Type", "application/json");

    String json = "{";
    json += "\"temp\":" + String(temp) + ",";
    json += "\"humidity\":" + String(humidity) + ",";
    json += "\"gas\":" + String(gas);
    json += "}";

    Serial.println("Sending Data:");
    Serial.println(json);

    int response = http.POST(json);

    Serial.print("Server Response: ");
    Serial.println(response);

    http.end();
  } else {
    Serial.println("❌ WiFi Disconnected!");
  }

  delay(3000);
}