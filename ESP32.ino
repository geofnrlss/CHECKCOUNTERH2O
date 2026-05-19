#include <WiFi.h>
#include <WiFiManager.h> 

WiFiServer server(80);
const int PIN_LAMP = 18;  const int PIN_PUMP = 19;
const int SW_MANUAL = 14; const int SW_AUTO = 27;
const int NIR_PIN = 34;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LAMP, OUTPUT); pinMode(PIN_PUMP, OUTPUT);
  pinMode(SW_MANUAL, INPUT_PULLUP); pinMode(SW_AUTO, INPUT_PULLUP);
  digitalWrite(PIN_LAMP, HIGH); digitalWrite(PIN_PUMP, HIGH);

  WiFiManager wm;
  // Portal muncul dengan nama "ESP32_SSD_SETUP" jika WiFi tidak ditemukan
  if(!wm.autoConnect("ESP32_SSD_SETUP")) {
    Serial.println("Gagal konek, restart...");
    ESP.restart();
  }
  Serial.println("Terhubung! IP: " + WiFi.localIP().toString());
  server.begin();
}

void loop() {
  int mode = (digitalRead(SW_MANUAL) == LOW) ? 1 : (digitalRead(SW_AUTO) == LOW ? 2 : 0);
  WiFiClient client = server.available();

  if (client) {
    while (client.connected()) {
      static unsigned long lastSend = 0;
      if (millis() - lastSend >= 1000) {
        client.print("DATA:"); client.print(analogRead(NIR_PIN));
        client.print(","); client.println(mode);
        lastSend = millis();
      }

      if (client.available()) {
        String cmd = client.readStringUntil('\n'); cmd.trim();
        if (mode == 1) { // MANUAL
          digitalWrite(PIN_LAMP, LOW); digitalWrite(PIN_PUMP, LOW);
        } else if (mode == 2) { // AUTO
          if (cmd == "LAMP_ON") digitalWrite(PIN_LAMP, LOW);
          if (cmd == "LAMP_OFF") digitalWrite(PIN_LAMP, HIGH);
          if (cmd == "PUMP_ON") digitalWrite(PIN_PUMP, LOW);
          if (cmd == "PUMP_OFF") digitalWrite(PIN_PUMP, HIGH);
        } else { // OFF
          digitalWrite(PIN_LAMP, HIGH); digitalWrite(PIN_PUMP, HIGH);
        }
      }
    }
  }
}