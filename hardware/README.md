# Lecteur de carte NFC — matériel (ESP32 + RC522)

Lecteur physique qui lit l'UID d'une carte NFC/RFID et l'envoie au backend
(`POST /cards/scan`). Le dashboard médecin web réagit : carte connue → ouvre le
dossier ; carte inconnue → formulaire d'enrôlement pré-rempli avec l'UID.

## Matériel

- **ESP32** (DevKit, USB-série)
- Module **RC522** (RFID 13,56 MHz)
- Buzzer **KY-006**

### Câblage

| RC522 | ESP32 | | KY-006 | ESP32 |
|-------|-------|-|--------|-------|
| SDA/SS | GPIO 5 | | S | GPIO 13 |
| SCK | GPIO 18 | | – (GND) | GND |
| MOSI | GPIO 23 | | (milieu) | non connecté |
| MISO | GPIO 19 |
| RST | **GPIO 4** |
| 3.3V | 3V3 (⚠ pas 5V) |
| GND | GND |
| IRQ | non connecté |

> ⚠️ Les fils dupont/breadboard doivent être **bien enfoncés** (surtout MOSI et
> l'alim) : un contact marginal donne des lectures/écritures SPI incohérentes.

## Firmwares

- **`esp32_card_reader_serial/`** — firmware de production (variante **série**,
  pas de WiFi). Lit l'UID et l'imprime `UID:<HEX>` sur l'USB. Robuste et
  indépendant du réseau. **C'est celui à utiliser.**
- `esp32_card_reader/` — variante WiFi (POST direct au backend ; dépend de l'IP).
- Sketches de diagnostic : `rc522_monitor/` (lit la version + teste les
  écritures registre), `rc522_pin_scanner/` (trouve le bon brochage),
  `ami_wifi_test/` (code WiFi tiers — attend une autre forme de réponse API).

### Toolchain (arduino-cli, sans sudo)

```bash
# installé dans ~/.local/bin ; core esp32:esp32 ; lib MFRC522
export PATH="$HOME/.local/bin:$PATH"
arduino-cli compile --fqbn esp32:esp32:esp32 hardware/esp32_card_reader_serial
arduino-cli upload  -p /dev/ttyUSB0 --fqbn esp32:esp32:esp32 hardware/esp32_card_reader_serial
```

> La lib **MFRC522** a son horloge SPI abaissée (`MFRC522_SPICLOCK` 4 MHz → 1 MHz
> dans `MFRC522.h`) pour tolérer la breadboard. Ce fichier est hors du repo
> (`~/Arduino/libraries/`) — à re-appliquer sur une autre machine.

## Accès au port série

L'utilisateur n'est pas dans le groupe `dialout`, donc après chaque
(re)branchement USB :

```bash
sudo chmod a+rw /dev/ttyUSB0
```

Permanent (nécessite déconnexion/reconnexion) : `sudo usermod -aG dialout $USER`.

## Lancer la démo

1. Backend sur `:9000` et web sur `:5174` up.
2. `python3 hardware/serial_bridge.py` (lit l'USB → `POST /cards/scan`).
   Anti-rebond **front-trigger** : un scan n'est transmis qu'à une **nouvelle
   pose** (lecture après un silence ≥ 1,5 s). Garder la carte **loin** du module
   sauf pour scanner.
3. Web sur « En attente de carte… » → approcher la carte → dossier/enrôlement.

### Sans matériel

`python3 hardware/sim_card.py` — simulateur clé en main (menu `n` = carte
inconnue → enrôlement, `r` = re-scan → dossier retrouvé).
