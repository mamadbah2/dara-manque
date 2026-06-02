def test_login_success_doctor(client, doctor):
    res = client.post("/auth/login", json={"email": "doctor@test.com", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "doctor"
    assert data["token_type"] == "bearer"


def test_login_success_pharmacist(client, pharmacist):
    res = client.post("/auth/login", json={"email": "pharmacist@test.com", "password": "password123"})
    assert res.status_code == 200
    assert res.json()["role"] == "pharmacist"


def test_login_wrong_password(client, doctor):
    res = client.post("/auth/login", json={"email": "doctor@test.com", "password": "wrong"})
    assert res.status_code == 401


def test_login_unknown_email(client):
    res = client.post("/auth/login", json={"email": "unknown@test.com", "password": "password123"})
    assert res.status_code == 401
