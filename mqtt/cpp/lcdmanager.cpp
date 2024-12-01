#include "lcd_manager.h"
#include <LiquidCrystal_I2C.h>
#include "config.h"

LiquidCrystal_I2C lcd(LCD_ADDRESS, 16, 2);

void lcdInit() {
    lcd.init();
    lcd.backlight();
}

void lcdPrint(const char* msg) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(msg);
}

void lcdAppend(const char* msg) {
    lcd.setCursor(0, 1);
    lcd.print(msg);
}
