/*
 * Dara Manqué — Lecteur de carte NFC (proto matériel, VARIANTE SÉRIE)
 * ESP32 + module RFID RC522 (+ buzzer).
 *
 * Cette variante N'UTILISE PAS le WiFi. Elle lit l'UID de la carte et l'imprime
 * sur le port USB série sous la forme "UID:<HEX>". Un script sur le PC
 * (hardware/serial_bridge.py) lit cette ligne et fait le POST /cards/scan vers
 * localhost:9000 — donc aucune dépendance au WiFi ni à l'adresse IP.
 *
 * Recommandé quand l'ESP32 est branché en USB à la machine du backend.
 *
 * -------------------------------------------------------------------------
 * CÂBLAGE RC522 -> ESP32 (bus VSPI par défaut) :
 *   RC522 SDA/SS  -> GPIO 5
 *   RC522 SCK     -> GPIO 18
 *   RC522 MOSI    -> GPIO 23
 *   RC522 MISO    -> GPIO 19
 *   RC522 RST     -> GPIO 4
 *   RC522 3.3V    -> 3V3   (⚠ PAS 5V)
 *   RC522 GND     -> GND
 *   Buzzer KY-006 S  -> GPIO 13
 *   Buzzer KY-006 -  -> GND
 *
 * BIBLIOTHÈQUE : "MFRC522" by GithubCommunity
 * VITESSE MONITEUR SÉRIE : 115200
 * -------------------------------------------------------------------------
 */

#include <SPI.h>
#include <MFRC522.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

#define SS_PIN     5
#define RST_PIN    4     // RST du RC522 câblé sur GPIO 4
#define BUZZER_PIN 13    // buzzer KY-006 câblé sur GPIO 13
// Broches SPI passées explicitement à SPI.begin() : sur ce core ESP32 le
// SPI.begin() sans arguments n'initialise pas correctement le bus (le RC522
// répondait 0xFF). En forçant SCK/MISO/MOSI/SS, le module répond.
#define SCK_PIN    18
#define MISO_PIN   19
#define MOSI_PIN   23

MFRC522 mfrc522(SS_PIN, RST_PIN);

void beep(int durationMs, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
    if (i < times - 1) delay(120);
  }
}

String uidToHex(const MFRC522::Uid &uid) {
  String s;
  for (byte i = 0; i < uid.size; i++) {
    if (uid.uidByte[i] < 0x10) s += "0";
    s += String(uid.uidByte[i], HEX);
  }
  s.toUpperCase();
  return s;
}

void setup() {
  // Désactive le détecteur de brownout : le champ RF du RC522 provoque un pic
  // de courant qui fait chuter la tension et rebooter l'ESP32. On l'ignore
  // pour encaisser le pic. (À compléter idéalement par un condensateur
  // 100-470µF sur le 3V3/GND du RC522 + une alim USB solide.)
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SS_PIN);   // broches explicites
  mfrc522.PCD_Init();

  // Info : version du RC522. 0x91/0x92 = puce d'origine ; d'autres valeurs
  // (ex. 0x82) = clone — on ne bloque pas dessus, le module lit quand même.
  byte v = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print("RC522_VERSION:0x");
  Serial.println(v, HEX);

  Serial.println("READY");   // le pont attend cette ligne au démarrage
}

void loop() {
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String uid = uidToHex(mfrc522.uid);
  Serial.print("UID:");        // ligne machine-parsable : "UID:04A2B3C1"
  Serial.println(uid);
  beep(120, 1);

  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
  delay(1500);                 // anti-rebond : évite les lectures multiples
}
