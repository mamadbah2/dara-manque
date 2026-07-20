/*
 * Monitoring RC522 — imprime la version chaque seconde (pour juger la
 * stabilité de la liaison SPI) et l'UID dès qu'une carte est détectée.
 * SPI à 500 kHz (défini dans MFRC522.h).
 */
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN   5
#define RST_PIN  4

MFRC522 mfrc522(SS_PIN, RST_PIN);
unsigned long last = 0;

String uidHex(const MFRC522::Uid &uid) {
  String s;
  for (byte i = 0; i < uid.size; i++) {
    if (uid.uidByte[i] < 0x10) s += "0";
    s += String(uid.uidByte[i], HEX);
  }
  s.toUpperCase();
  return s;
}

void setup() {
  Serial.begin(115200);
  SPI.begin(18, 19, 23);   // SCK, MISO, MOSI — PAS de SS (CS géré par la lib)
  mfrc522.PCD_Init();
  mfrc522.PCD_SetAntennaGain(mfrc522.RxGain_max);   // sensibilité max
  mfrc522.PCD_AntennaOn();
  // TxControlReg : bits Tx1RFEn/Tx2RFEn (0x03) => driver d'antenne allumé.
  // 0x83 = antenne ON. 0x80 = antenne OFF.
  byte tx = mfrc522.PCD_ReadRegister(MFRC522::TxControlReg);
  Serial.print("TXCTRL:0x"); Serial.println(tx, HEX);
  // Test écriture directe : on force 0x83 et on relit.
  mfrc522.PCD_WriteRegister(MFRC522::TxControlReg, 0x83);
  byte tx2 = mfrc522.PCD_ReadRegister(MFRC522::TxControlReg);
  Serial.print("TXCTRL_APRES_ECRITURE:0x"); Serial.println(tx2, HEX);
  // Test écriture sur un registre banal (TReloadRegL, R/W libre) : on écrit
  // 0xA5 et on relit. 0xA5 => les écritures marchent (problème isolé au RF).
  // Autre valeur => échec d'écriture global (MOSI/câblage).
  mfrc522.PCD_WriteRegister(MFRC522::TReloadRegL, 0xA5);
  byte tr = mfrc522.PCD_ReadRegister(MFRC522::TReloadRegL);
  Serial.print("TRELOAD_TEST:0x"); Serial.println(tr, HEX);
  Serial.println("MON_READY");
}

void loop() {
  if (millis() - last > 1000) {
    last = millis();
    byte v = mfrc522.PCD_ReadRegister(MFRC522::VersionReg);
    Serial.print("VER:0x");
    Serial.println(v, HEX);
  }
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
    Serial.print("UID:");
    Serial.println(uidHex(mfrc522.uid));
    mfrc522.PICC_HaltA();
    mfrc522.PCD_StopCrypto1();
  }
}
