#include <Arduino.h>
#include "wifi_manager.h"
#include "mqtt_manager.h"
#include "biometric_manager.h"
#include "lcd_manager.h"
#include "config.h"

void setup() {
    Serial.begin(115200);
    lcdInit();
    lcdPrint("Iniciando...");
    delay(2000);

    setupWiFi();
    setupMQTT();
    biometricInit();
    pinSetup();
}

void loop() {
    if (!mqttConnected()) {
        mqttReconnect();
    }
    mqttLoop();

    int result = captureFingerprintID();
    if (result >= 0) {
        String msg = "{\"id\":" + String(result) + "}";
        mqttPublish(MQTT_TOPIC_VALIDATION, msg);
    }
}
