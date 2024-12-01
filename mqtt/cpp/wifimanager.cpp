#include "wifi_manager.h"
#include <WiFi.h>
#include "lcd_manager.h"
#include "config.h"

void setupWiFi() {
    lcdPrint("Conectando WiFi...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        lcdAppend(".");
    }

    lcdPrint("WiFi conectado");
    lcdAppend(WiFi.localIP().toString().c_str());
    delay(2000);
}
