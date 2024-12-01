#ifndef MQTT_MANAGER_H
#define MQTT_MANAGER_H

void setupMQTT();
bool mqttConnected();
void mqttReconnect();
void mqttLoop();
void mqttPublish(const char* topic, const String& msg);

#endif
