#!/usr/bin/env python3
"""Simulateur de lecteur de carte — remplace l'ESP32 pour la démo.

Chaque « scan » fait un POST /cards/scan au backend, exactement comme le
lecteur physique. Le dashboard médecin web (écran « En attente de carte »)
réagit : carte connue -> ouvre le dossier ; carte inconnue -> formulaire
d'enrôlement pré-rempli avec l'UID.

Aucune dépendance (stdlib uniquement).

Usage :
    python3 hardware/sim_card.py                 # menu interactif
    python3 hardware/sim_card.py 1001            # scanne directement l'UID 1001
    python3 hardware/sim_card.py --url http://localhost:9000 1001

Rappel : garde le navigateur sur l'écran « En attente de carte… » (idle),
sinon le scan est ignoré. Si rien ne se passe : Ctrl+Shift+R sur la page.
"""
import json
import random
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:9000"

# Cartes de démo pré-enrôlées dans le seed / créées pendant les tests.
PRESETS = {
    "1001": "Mamadou Diallo (déjà enrôlé — démo consultation)",
}

last_uid = None


def _post(path, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode())


def _get(path):
    with urllib.request.urlopen(BASE + path, timeout=5) as r:
        return json.loads(r.read().decode())


def scan(uid):
    """Simule le dépôt d'une carte sur le lecteur."""
    global last_uid
    uid = uid.strip()
    if not uid:
        return
    try:
        res = _post("/cards/scan", {"uid": uid})
    except urllib.error.URLError as e:
        print(f"  ✗ backend injoignable ({e}). Le backend tourne-t-il sur {BASE} ?")
        return
    last_uid = res["uid"]
    print(f"\n  📇 Carte scannée : {res['uid']}")
    if res["known"] and res.get("patient"):
        p = res["patient"]
        print(f"  ✅ CONNUE → dossier : {p['full_name']} (ID {p['id']})")
        if p.get("allergies"):
            print(f"       ⚠ allergies : {p['allergies']}")
        print("  👉 Le web ouvre le DOSSIER de ce patient.")
    else:
        print("  🆕 INCONNUE → pas encore de patient lié.")
        print(f"  👉 Le web ouvre le FORMULAIRE d'enrôlement (Carte : {res['uid']}).")
        print("     Remplis-le côté web, puis reviens ici et choisis [r] pour re-scanner.")
    print()


def new_card():
    """Génère un UID neuf (façon UID MIFARE 4 octets) et le scanne."""
    uid = "".join(random.choice("0123456789ABCDEF") for _ in range(8))
    print(f"  → nouvelle carte générée : {uid}")
    scan(uid)


def check_backend():
    try:
        _get("/cards/last-scan")
        return True
    except Exception as e:
        print(f"⚠  Backend injoignable sur {BASE} ({e}).")
        print("   Lance-le : cd backend && source venv/bin/activate && "
              "uvicorn app.main:app --host 0.0.0.0 --port 9000")
        return False


def menu():
    print("=" * 58)
    print("  SIMULATEUR DE CARTE — Dara Manqué")
    print(f"  backend : {BASE}")
    print("=" * 58)
    print("  Garde le navigateur sur « En attente de carte… »\n")
    if not check_backend():
        return
    while True:
        print("-" * 58)
        print("  [n] Nouvelle carte INCONNUE   → démo enrôlement")
        if last_uid:
            print(f"  [r] Re-scanner la dernière ({last_uid}) → démo dossier retrouvé")
        for uid, label in PRESETS.items():
            print(f"  [{uid}] {label}")
        print("  [<UID>] scanner un UID précis   |   [q] quitter")
        choice = input("  > ").strip()
        if choice.lower() == "q":
            print("  Fin de la démo.")
            return
        elif choice.lower() == "n":
            new_card()
        elif choice.lower() == "r":
            if last_uid:
                scan(last_uid)
            else:
                print("  (aucune carte scannée pour l'instant)")
        elif choice:
            scan(choice)


def main():
    global BASE
    args = sys.argv[1:]
    if "--url" in args:
        i = args.index("--url")
        BASE = args[i + 1]
        del args[i:i + 2]
    if args:  # un UID passé en argument → scan direct, pas de menu
        if not check_backend():
            return
        scan(args[0])
    else:
        menu()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n  Interrompu.")
