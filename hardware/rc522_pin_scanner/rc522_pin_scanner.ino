/*
 * Scanner de brochage RC522 pour ESP32.
 * Essaie les combinaisons de broches les plus courantes et lit le registre
 * de version du RC522 pour chacune. Une valeur 0x91 / 0x92 = le module répond
 * sur CE brochage. 0x00 / 0xFF = pas de réponse.
 *
 * Si AUCUNE combinaison ne répond -> c'est l'alimentation (3V3/GND) ou le
 * module, pas le brochage des signaux.
 */
#include <SPI.h>
#include <MFRC522.h>

struct Combo { int sck, miso, mosi, ss, rst; };

// Brochages ESP32 + RC522 rencontrés dans la nature.
Combo combos[] = {
  {18, 19, 23,  5, 22},  // VSPI standard (par défaut)
  {18, 19, 23,  5, 27},
  {18, 19, 23,  5,  4},
  {18, 19, 23,  5,  0},
  {18, 19, 23,  5,  2},
  {18, 19, 23, 21, 22},
  {18, 19, 23, 15, 22},
  {14, 12, 13, 15,  4},  // HSPI
  {14, 12, 13, 15, 27},
  {14, 12, 13, 15,  2},
  {14, 12, 13,  5, 22},
  {25, 33, 26, 32, 27},
};

void tryCombo(const Combo &c) {
  SPI.end();
  SPI.begin(c.sck, c.miso, c.mosi, c.ss);
  MFRC522 m(c.ss, c.rst);
  m.PCD_Init();
  delay(60);
  byte v = m.PCD_ReadRegister(MFRC522::VersionReg);
  bool ok = (v == 0x91 || v == 0x92);
  Serial.print("SCK="); Serial.print(c.sck);
  Serial.print(" MISO="); Serial.print(c.miso);
  Serial.print(" MOSI="); Serial.print(c.mosi);
  Serial.print(" SS="); Serial.print(c.ss);
  Serial.print(" RST="); Serial.print(c.rst);
  Serial.print(" -> 0x"); Serial.print(v, HEX);
  Serial.println(ok ? "  <=== OK !!!" : "");
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println("SCAN_START");
  for (Combo &c : combos) tryCombo(c);
  Serial.println("SCAN_DONE");
}

void loop() {}
