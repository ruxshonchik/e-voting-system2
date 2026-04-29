def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "newuser@example.com",
        "password": "securepassword",
        "role": "user"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    payload = {"name": "Dup", "email": "dup@example.com", "password": "pass1234", "role": "user"}
    client.post("/api/auth/register", json=payload)
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/api/auth/register", json={
        "name": "Login User",
        "email": "loginuser@example.com",
        "password": "mypassword",
        "role": "user"
    })
    resp = client.post("/api/auth/login", json={
        "email": "loginuser@example.com",
        "password": "mypassword"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "name": "Wrong Pass User",
        "email": "wrongpass@example.com",
        "password": "correctpassword",
        "role": "user"
    })
    resp = client.post("/api/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "wrongpassword"
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/api/auth/login", json={
        "email": "nobody@example.com",
        "password": "anypassword"
    })
    assert resp.status_code == 401


def test_refresh_token(client):
    reg = client.post("/api/auth/register", json={
        "name": "Refresh User",
        "email": "refresh@example.com",
        "password": "refreshpass",
        "role": "user"
    })
    refresh_token = reg.json()["refresh_token"]
    resp = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_refresh_invalid_token(client):
    resp = client.post("/api/auth/refresh", json={"refresh_token": "invalid.token.here"})
    assert resp.status_code == 401
