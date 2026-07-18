from app.models import Patient


def _make_carded_patient(db, uid="04A2B3C1"):
    p = Patient(
        id=2001,
        full_name="Awa Ndiaye",
        allergies="Aucune",
        card_uid=uid,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# --- POST /cards/scan (ESP32 -> backend lookup) ---

def test_scan_known_card_returns_patient(client, db):
    _make_carded_patient(db)
    res = client.post("/cards/scan", json={"uid": "04A2B3C1"})
    assert res.status_code == 200
    data = res.json()
    assert data["known"] is True
    assert data["uid"] == "04A2B3C1"
    assert data["patient"]["id"] == 2001
    assert data["patient"]["full_name"] == "Awa Ndiaye"
    assert data["patient"]["card_uid"] == "04A2B3C1"


def test_scan_unknown_card_returns_not_known(client, db):
    res = client.post("/cards/scan", json={"uid": "DEADBEEF"})
    assert res.status_code == 200
    data = res.json()
    assert data["known"] is False
    assert data["uid"] == "DEADBEEF"
    assert data["patient"] is None


def test_scan_normalizes_uid_format(client, db):
    # stored uppercase compact, reader sends lowercase with colons
    _make_carded_patient(db, uid="04A2B3C1")
    res = client.post("/cards/scan", json={"uid": "04:a2:b3:c1"})
    assert res.status_code == 200
    assert res.json()["known"] is True
    assert res.json()["patient"]["id"] == 2001


def test_scan_empty_uid_rejected(client, db):
    res = client.post("/cards/scan", json={"uid": "  "})
    assert res.status_code == 422


# --- POST /patients (doctor enrolls a new patient + associates card) ---

def test_enroll_patient_creates_and_links_card(client, db, doctor_token):
    res = client.post(
        "/patients",
        json={
            "full_name": "Cheikh Fall",
            "allergies": "Pénicilline",
            "card_uid": "AABBCCDD",
        },
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["full_name"] == "Cheikh Fall"
    assert data["card_uid"] == "AABBCCDD"
    assert isinstance(data["id"], int)

    # the freshly enrolled card is now resolvable via scan
    scan = client.post("/cards/scan", json={"uid": "aa:bb:cc:dd"})
    assert scan.json()["known"] is True
    assert scan.json()["patient"]["id"] == data["id"]


def test_enroll_requires_doctor_role(client, db, pharmacist_token):
    res = client.post(
        "/patients",
        json={"full_name": "X", "card_uid": "11223344"},
        headers={"Authorization": f"Bearer {pharmacist_token}"},
    )
    assert res.status_code == 403


def test_enroll_no_auth_rejected(client, db):
    res = client.post("/patients", json={"full_name": "X", "card_uid": "11223344"})
    assert res.status_code in (401, 403)


def test_enroll_duplicate_card_conflicts(client, db, doctor_token):
    _make_carded_patient(db, uid="0F0F0F0F")
    res = client.post(
        "/patients",
        json={"full_name": "Autre", "card_uid": "0f:0f:0f:0f"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 409


# --- GET /cards/last-scan (bridge: reader -> web dashboard) ---

def test_last_scan_reflects_a_known_scan(client, db):
    _make_carded_patient(db)
    before = client.get("/cards/last-scan").json()["seq"]
    client.post("/cards/scan", json={"uid": "04:a2:b3:c1"})
    after = client.get("/cards/last-scan").json()
    assert after["seq"] == before + 1
    assert after["known"] is True
    assert after["uid"] == "04A2B3C1"
    assert after["patient"]["id"] == 2001


def test_last_scan_reflects_an_unknown_scan(client, db):
    before = client.get("/cards/last-scan").json()["seq"]
    client.post("/cards/scan", json={"uid": "12345678"})
    after = client.get("/cards/last-scan").json()
    assert after["seq"] == before + 1
    assert after["known"] is False
    assert after["uid"] == "12345678"
    assert after["patient"] is None


def test_last_scan_seq_increments_per_scan(client, db):
    s0 = client.get("/cards/last-scan").json()["seq"]
    client.post("/cards/scan", json={"uid": "AAAA"})
    client.post("/cards/scan", json={"uid": "BBBB"})
    assert client.get("/cards/last-scan").json()["seq"] == s0 + 2


def test_enroll_without_card_allowed(client, db, doctor_token):
    res = client.post(
        "/patients",
        json={"full_name": "Sans Carte"},
        headers={"Authorization": f"Bearer {doctor_token}"},
    )
    assert res.status_code == 201
    assert res.json()["card_uid"] is None
