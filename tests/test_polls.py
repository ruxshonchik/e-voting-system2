from datetime import datetime, timedelta


def make_poll_payload(title="Test Poll", options=None):
    if options is None:
        options = ["Option A", "Option B"]
    now = datetime.utcnow()
    return {
        "title": title,
        "description": "A test poll",
        "start_date": (now - timedelta(hours=1)).isoformat(),
        "end_date": (now + timedelta(hours=2)).isoformat(),
        "options": options
    }


def test_create_poll_as_admin(admin_client):
    resp = admin_client.post("/api/admin/polls", json=make_poll_payload())
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Poll"
    assert data["status"] == "draft"
    assert len(data["options"]) == 2


def test_create_poll_requires_auth(client):
    resp = client.post("/api/admin/polls", json=make_poll_payload())
    assert resp.status_code == 403


def test_create_poll_too_few_options(admin_client):
    payload = make_poll_payload(options=["Only one"])
    resp = admin_client.post("/api/admin/polls", json=payload)
    assert resp.status_code in (400, 422)


def test_get_polls_as_user(user_client):
    resp = user_client.get("/api/polls")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_start_and_get_active_poll(admin_client, user_client):
    poll = admin_client.post("/api/admin/polls", json=make_poll_payload("Active Poll Test")).json()
    poll_id = poll["id"]

    start_resp = admin_client.post(f"/api/admin/polls/{poll_id}/start")
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "active"

    active_polls = user_client.get("/api/polls?status=active").json()
    ids = [p["id"] for p in active_polls]
    assert poll_id in ids


def test_stop_poll(admin_client):
    poll = admin_client.post("/api/admin/polls", json=make_poll_payload("Stop Poll Test")).json()
    poll_id = poll["id"]
    admin_client.post(f"/api/admin/polls/{poll_id}/start")
    resp = admin_client.post(f"/api/admin/polls/{poll_id}/stop")
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"


def test_delete_draft_poll(admin_client):
    poll = admin_client.post("/api/admin/polls", json=make_poll_payload("Delete Me")).json()
    poll_id = poll["id"]
    resp = admin_client.delete(f"/api/admin/polls/{poll_id}")
    assert resp.status_code == 204


def test_delete_active_poll_fails(admin_client):
    poll = admin_client.post("/api/admin/polls", json=make_poll_payload("No Delete Active")).json()
    poll_id = poll["id"]
    admin_client.post(f"/api/admin/polls/{poll_id}/start")
    resp = admin_client.delete(f"/api/admin/polls/{poll_id}")
    assert resp.status_code == 409


def test_get_poll_by_id(admin_client, user_client):
    poll = admin_client.post("/api/admin/polls", json=make_poll_payload("Get By ID")).json()
    poll_id = poll["id"]
    resp = user_client.get(f"/api/polls/{poll_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == poll_id
