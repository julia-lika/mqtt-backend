#include "mqtt_manager.h"
#include <PubSubClient.h>
#include "lcd_manager.h"
#include "config.h"

WiFiClient espClient;
PubSubClient client(espClient);

void setupMQTT() {
    client.setServer(MQTT_SERVER, MQTT_PORT);
    client.setCallback([](char* topic, byte* payload, unsigned int length) {
        handleMQTTMessage(topic, payload, length);
    });
}

bool mqttConnected() {
    return client.connected();
}

void mqttReconnect() {
    while (!client.connected()) {
        lcdPrint("Conectando MQTT...");
        if (client.connect("clientId-NiczoLeBwO")) {
            lcdPrint("MQTT conectado!");
            client.subscribe(MQTT_TOPIC_CONFIG);
        } else {
            lcdPrint("Falha MQTT:");
            lcdAppend(String(client.state()));
            delay(2000);
        }
    }
}

void mqttLoop() {
    client.loop();
}

void mqttPublish(const char* topic, const String& msg) {
    client.publish(topic, msg.c_str());
}

void handleMQTTMessage(char* topic, byte* payload, unsigned int length) {
    // Implementar manipulação de mensagens
}
