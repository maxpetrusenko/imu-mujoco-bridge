#include <Adafruit_BNO055.h>
#include <M5Atom.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <utility/imumaths.h>

#include "config.h"

Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28);
WiFiUDP udp;

void setup() {
  M5.begin(true, false, true);
  Serial.begin(115200);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.printf("\nWiFi connected: %s\n", WiFi.localIP().toString().c_str());

  if (!bno.begin()) {
    Serial.println("BNO055 not detected");
    while (true) {
      M5.dis.drawpix(0, 0xff0000);
      delay(250);
      M5.dis.drawpix(0, 0x000000);
      delay(250);
    }
  }

  bno.setExtCrystalUse(true);
  M5.dis.drawpix(0, 0x00ff00);
}

void loop() {
  imu::Quaternion q = bno.getQuat();

  uint8_t sys = 0;
  uint8_t gyro = 0;
  uint8_t accel = 0;
  uint8_t mag = 0;
  bno.getCalibration(&sys, &gyro, &accel, &mag);

  char packet[160];
  snprintf(
      packet,
      sizeof(packet),
      "%.6f,%.6f,%.6f,%.6f,%u,%u,%u,%u,%lu",
      q.w(),
      q.x(),
      q.y(),
      q.z(),
      sys,
      gyro,
      accel,
      mag,
      millis());

  udp.beginPacket(UDP_HOST, UDP_PORT);
  udp.write(reinterpret_cast<const uint8_t *>(packet), strlen(packet));
  udp.endPacket();

  Serial.println(packet);
  delay(SAMPLE_DELAY_MS);
}

