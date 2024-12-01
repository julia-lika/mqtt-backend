#ifndef CONFIG_H
#define CONFIG_H

// Wi-Fi
#define WIFI_SSID "julia lmao"
#define WIFI_PASSWORD "lika1234"

// MQTT
#define MQTT_SERVER "broker.hivemq.com"
#define MQTT_PORT 1883
#define MQTT_TOPIC_VALIDATION "instituto/biometria/acesso"
#define MQTT_TOPIC_CONFIG "instituto/config/cadastro"

// LCD
#define LCD_ADDRESS 0x27

// Biometric pins
#define BIOMETRIC_RX_PIN 16
#define BIOMETRIC_TX_PIN 17

#endif
