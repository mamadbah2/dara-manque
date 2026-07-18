/*
 * Dara Manqué — Lecteur de carte NFC (proto matériel)
 * ESP32 + module RFID RC522 (+ buzzer).
 *
 * Quand une carte est posée sur le RC522, l'ESP32 lit son UID d'usine et le
 * POST au backend (POST /cards/scan). Le backend répond {uid, known, patient} ;
 * le buzzer confirme : 2 bips courts = carte connue, 1 bip long = inconnue/erreur.
 *
 * -------------------------------------------------------------------------
 * CÂBLAGE RC522 -> ESP32 (bus VSPI par défaut) :
 *   RC522 SDA/SS  -> GPIO 5
 *   RC522 SCK     -> GPIO 18
 *   RC522 MOSI    -> GPIO 23
 *   RC522 MISO    -> GPIO 19
 *   RC522 RST     -> GPIO 22
 *   RC522 3.3V    -> 3V3   (⚠ PAS 5V)
 *   RC522 GND     -> GND
 *   Buzzer +      -> GPIO 4   (adapte à TON câblage)
 *   Buzzer -      -> GND
 *
 * BIBLIOTHÈQUES (Arduino IDE -> Gérer les bibliothèques) :
 *   - "MFRC522" by GithubCommunity
 *   (WiFi.h et HTTPClient.h sont inclus dans le core ESP32)
 *
 * AVANT DE FLASHER : renseigner WIFI_SSID / WIFI_PASS ci-dessous.
 * L'ESP32 doit être sur le MÊME réseau WiFi que le serveur backend.
 * -------------------------------------------------------------------------
 */

#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ---- WiFi (à renseigner) ----
const char* WIFI_SSID = "TON_WIFI";
const char* WIFI_PASS = "TON_MOT_DE_PASSE";

// ---- Backend ----
// IP LAN de la machine qui fait tourner le backend (interface WiFi).
const char* SCAN_URL = "http://172.20.10.2:9000/cards/scan";

// ---- Broches ----
#define SS_PIN     5
#define RST_PIN    22
#define BUZZER_PIN 4

MFRC522 mfrc522(SS_PIN, RST_PIN);

void beep(int durationMs, int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(durationMs);
    digitalWrite(BUZZER_PIN, LOW);
    if (i < times - 1) delay(120);
  }
}

void connectWifi() {
  Serial.printf("Connexion WiFi à \"%s\"", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("WiFi OK — IP ESP32 : ");
  Serial.println(WiFi.localIP());
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

void postScan(const String &uid) {
  if (WiFi.status() != WL_CONNECTED) connectWifi();

  HTTPClient http;
  http.begin(SCAN_URL);
  http.addHeader("Content-Type", "application/json");

  String body = "{\"uid\":\"" + uid + "\"}";
  int code = http.POST(body);
  String resp = http.getString();
  Serial.printf("POST %s -> HTTP %d\n%s\n", SCAN_URL, code, resp.c_str());

  if (code == 200 && resp.indexOf("\"known\":true") >= 0) {
    beep(120, 2);   // patient connu
  } else {
    beep(500, 1);   // inconnu / erreur réseau
  }
  http.end();
}

void setup() {
  Serial.begin(115200);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  SPI.begin();            // SCK=18, MISO=19, MOSI=23 (VSPI par défaut)
  mfrc522.PCD_Init();
  Serial.println("RC522 prêt.");

  connectWifi();
  Serial.println("Pose une carte sur le lecteur…");
}

void loop() {
  // Rien à faire tant qu'aucune nouvelle carte n'est présente.
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    delay(50);
    return;
  }

  String uid = uidToHex(mfrc522.uid);
  Serial.println("Carte détectée, UID = " + uid);
  postScan(uid);

  mfrc522.PICC_HaltA();      // arrête la communication avec la carte
  mfrc522.PCD_StopCrypto1();
  delay(1500);               // anti-rebond : évite les lectures multiples
}
