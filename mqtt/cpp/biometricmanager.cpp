#include "biometric_manager.h"
#include <Adafruit_Fingerprint.h>
#include "config.h"

Adafruit_Fingerprint finger(&Serial2);

void biometricInit() {
    Serial2.begin(57600, SERIAL_8N1, BIOMETRIC_RX_PIN, BIOMETRIC_TX_PIN);
    finger.begin(57600);

    if (!finger.verifyPassword()) {
        Serial.println("Erro ao conectar ao leitor biométrico.");
        while (1); // Loop infinito indicando erro
    }
}

int captureFingerprintID() {
    uint8_t p = finger.getImage();
    if (p != FINGERPRINT_OK) return -1;

    p = finger.image2Tz();
    if (p != FINGERPRINT_OK) return -1;

    p = finger.fingerFastSearch();
    return (p == FINGERPRINT_OK) ? finger.fingerID : -1;
}
