#!/usr/bin/env python3
"""Pont série -> backend pour le lecteur ESP32 (variante série).

Lit les lignes "UID:<HEX>" émises par l'ESP32 sur le port USB et fait un
POST /cards/scan vers le backend. Aucune dépendance WiFi : l'ESP32 est branché
en USB, le backend tourne en local.

Dépendances : pyserial (déjà installé). Le reste est de la stdlib.

Usage :
    python3 hardware/serial_bridge.py                 # /dev/ttyUSB0, localhost:9000
    python3 hardware/serial_bridge.py /dev/ttyUSB0 http://localhost:9000
"""
import json
import sys
import time
import urllib.request
import urllib.error

import serial  # pyserial

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/ttyUSB0"
BASE = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:9000"
SCAN_URL = BASE.rstrip("/") + "/cards/scan"
BAUD = 115200

# Anti-rebond sur FRONT : le lecteur re-lit une carte présente en continu (voire
# fait des lectures fantômes). On ne transmet un scan que lorsqu'une lecture
# arrive APRÈS un silence >= GAP secondes = une vraie nouvelle pose de carte.
# Tant que les lectures s'enchaînent sans trou, on ignore (une seule pose = un scan).
GAP = 1.5
_last_line_ts = 0.0


def post_scan(uid: str):
    data = json.dumps({"uid": uid}).encode()
    req = urllib.request.Request(
        SCAN_URL, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return r.status, json.loads(r.read().decode())


def main():
    print(f"[bridge] port={PORT}  ->  {SCAN_URL}")
    while True:
        try:
            ser = serial.Serial(PORT, BAUD, timeout=1)
        except Exception as e:
            print(f"[bridge] ouverture du port impossible ({e}); nouvelle tentative dans 2s")
            time.sleep(2)
            continue

        print("[bridge] port ouvert, en attente de cartes…")
        try:
            while True:
                line = ser.readline().decode("utf-8", "replace").strip()
                if not line:
                    continue
                print(f"[série] {line}")
                if line.startswith("UID:"):
                    uid = line[4:].strip()
                    if not uid:
                        continue
                    global _last_line_ts
                    now = time.time()
                    fresh = (now - _last_line_ts) >= GAP  # lecture après un silence ?
                    _last_line_ts = now
                    if not fresh:
                        continue  # lecture continue de la même pose -> on ignore
                    try:
                        status, body = post_scan(uid)
                        known = body.get("known")
                        who = body.get("patient", {}).get("full_name") if body.get("patient") else None
                        print(f"[scan] {uid} -> HTTP {status} known={known} patient={who}")
                    except urllib.error.URLError as e:
                        print(f"[scan] {uid} -> POST échoué: {e}")
        except serial.SerialException as e:
            print(f"[bridge] port perdu ({e}); reconnexion…")
            time.sleep(2)
        finally:
            try:
                ser.close()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bridge] arrêt.")
