#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ─── BROCHES ──────────────────────────────────────────
#define SS_PIN    5
#define RST_PIN   4
#define BUZZER    13

// ─── WIFI ─────────────────────────────────────────────
const char* WIFI_SSID     = "Abdoulaye";
const char* WIFI_PASSWORD = "pckg744&";

// ─── SERVEUR ──────────────────────────────────────────
const char* SERVEUR_URL = "http://172.31.57.145:9000/cards/scan";

MFRC522 rfid(SS_PIN, RST_PIN);

// ─── BUZZER ───────────────────────────────────────────
void bipSucces() {
  // 2 bips courts aigus = carte reconnue
  digitalWrite(BUZZER, HIGH); delay(150);
  digitalWrite(BUZZER, LOW);  delay(100);
  digitalWrite(BUZZER, HIGH); delay(150);
  digitalWrite(BUZZER, LOW);
}

void bipEchec() {
  // 1 bip long grave = carte inconnue
  digitalWrite(BUZZER, HIGH); delay(600);
  digitalWrite(BUZZER, LOW);
}

void bipScan() {
  // 1 bip très court = scan détecté
  digitalWrite(BUZZER, HIGH); delay(80);
  digitalWrite(BUZZER, LOW);
}

// ─── CONNEXION WIFI ───────────────────────────────────
void connecterWiFi() {
  Serial.println("Initialisation WiFi...");

  WiFi.mode(WIFI_STA); // Force le mode Station (client)
  WiFi.disconnect(true); // Efface toute connexion précédente
  delay(100);

  Serial.print("Connexion a : ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int tentatives = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    tentatives++;
    if (tentatives > 40) { // 20 secondes max
      Serial.println("\nEchec connexion WiFi !");
      Serial.println("Verifie le nom et mot de passe WiFi");
      bipEchec();
      return;
    }
  }

  Serial.println("\nWiFi connecte !");
  Serial.print("IP ESP32 : ");
  Serial.println(WiFi.localIP());
  Serial.print("Signal : ");
  Serial.print(WiFi.RSSI());
  Serial.println(" dBm");
}

// ─── LIRE UID ─────────────────────────────────────────
String lireUID() {
  String uid = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) uid += "0";
    uid += String(rfid.uid.uidByte[i], HEX);
  }
  uid.toUpperCase();
  return uid;
}

// ─── ENVOYER UID AU SERVEUR ───────────────────────────
void envoyerUID(String uid) {

  // Vérifier la connexion WiFi avant d'envoyer
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi deconnecte ! Tentative reconnexion...");
    connecterWiFi(); // Tentative de reconnexion automatique
    if (WiFi.status() != WL_CONNECTED) {
      bipEchec();
      return;
    }
  }

  HTTPClient http;
  http.begin(SERVEUR_URL);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(5000); // Timeout 5 secondes

  // JSON à envoyer
  String json = "{\"uid\":\"" + uid + "\"}";
  Serial.println("Envoi vers serveur : " + json);

  int httpCode = http.POST(json);
  Serial.println("Code HTTP recu : " + String(httpCode));

  if (httpCode == 200 || httpCode == 201) {
    String reponse = http.getString();
    Serial.println("Reponse serveur : " + reponse);

    JsonDocument doc;   // ArduinoJson 7 (remplace StaticJsonDocument<256>)
    DeserializationError erreur = deserializeJson(doc, reponse);

    if (erreur) {
      Serial.println("Erreur parsing JSON : " + String(erreur.c_str()));
      bipEchec();
    } else {
      String status = doc["status"].as<String>();

      if (status == "succes") {
        String nom    = doc["nom"].as<String>();
        String prenom = doc["prenom"].as<String>();
        Serial.println("---------------------------");
        Serial.println("Patient identifie !");
        Serial.println("Nom    : " + nom);
        Serial.println("Prenom : " + prenom);
        Serial.println("---------------------------");
        bipSucces();
      } else {
        String message = doc["message"].as<String>();
        Serial.println("Carte inconnue : " + message);
        bipEchec();
      }
    }

  } else if (httpCode < 0) {
    Serial.println("Impossible de joindre le serveur !");
    Serial.println("Verifie que le backend tourne sur 172.31.57.145:9000");
    bipEchec();
  } else {
    Serial.println("Erreur serveur code : " + String(httpCode));
    bipEchec();
  }

  http.end();
}

// ─── SETUP ────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);

  // Initialisation SPI et MFRC522
  SPI.begin();
  rfid.PCD_Init();
  delay(100);

  Serial.println("=== Smart Health Card ===");
  Serial.println("Initialisation du lecteur RFID...");
  rfid.PCD_DumpVersionToSerial(); // Affiche la version du lecteur

  // Connexion WiFi
  connecterWiFi();

  Serial.println("=========================");
  Serial.println("Systeme pret !");
  Serial.println("Approche ta carte...");
  Serial.println("=========================");
}

// ─── LOOP ─────────────────────────────────────────────
void loop() {

  // Vérification périodique du WiFi toutes les 30 secondes
  static unsigned long dernierCheck = 0;
  if (millis() - dernierCheck > 30000) {
    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("WiFi perdu, reconnexion...");
      connecterWiFi();
    }
    dernierCheck = millis();
  }

  // Attendre une carte
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Bip de scan détecté
  bipScan();

  // Lire et afficher l'UID
  String uid = lireUID();
  Serial.println("Carte detectee ! UID : " + uid);

  // Envoyer au serveur
  envoyerUID(uid);

  // Arrêter la communication avec la carte
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  // Attendre 2 secondes avant le prochain scan
  delay(2000);
}
