from datetime import datetime, timedelta


def make_active_poll(admin_client, title="Vote Poll"):
    now = datetime.utcnow()
    payload = {
        "title": title,
        "description": "Voting test",
        "start_date": (now - timedelta(hours=1)).isoformat(),
        "end_date": (now + timedelta(hours=2)).isoformat(),
        "options": ["Choice X", "Choice Y", "Choice Z"]
    }
    poll = admin_client.post("/api/admin/polls", json=payload).json()
    poll_id = poll["id"]
    admin_client.post(f"/api/admin/polls/{poll_id}/start")
    return poll


def test_cast_vote(admin_client, user_client):
    poll = make_active_poll(admin_client, "Vote Test 1")
    poll_id = poll["id"]
    option_id = poll["options"][0]["id"]

    resp = user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    assert resp.status_code == 201


def test_vote_duplicate_rejected(admin_client, user_client):
    poll = make_active_poll(admin_client, "Vote Test Dup")
    poll_id = poll["id"]
    option_id = poll["options"][0]["id"]

    user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    resp = user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    assert resp.status_code == 409


def test_vote_on_draft_poll_fails(admin_client, user_client):
    now = datetime.utcnow()
    payload = {
        "title": "Draft Poll",
        "description": "Should not vote",
        "start_date": (now - timedelta(hours=1)).isoformat(),
        "end_date": (now + timedelta(hours=2)).isoformat(),
        "options": ["A", "B"]
    }
    poll = admin_client.post("/api/admin/polls", json=payload).json()
    poll_id = poll["id"]
    option_id = poll["options"][0]["id"]

    resp = user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})
    assert resp.status_code == 409


def test_vote_wrong_option_fails(admin_client, user_client):
    poll = make_active_poll(admin_client, "Vote Wrong Option")
    poll_id = poll["id"]
    resp = user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": 99999})
    assert resp.status_code == 400


def test_get_results(admin_client, user_client):
    poll = make_active_poll(admin_client, "Results Test")
    poll_id = poll["id"]
    option_id = poll["options"][1]["id"]
    user_client.post(f"/api/polls/{poll_id}/vote", json={"option_id": option_id})

    resp = user_client.get(f"/api/polls/{poll_id}/results")
    assert resp.status_code == 200
    data = resp.json()
    assert data["poll_id"] == poll_id
    assert data["total_votes"] == 1
    voted_option = next(r for r in data["results"] if r["option_id"] == option_id)
    assert voted_option["vote_count"] == 1
    assert voted_option["percentage"] == 100.0


def test_stats_endpoint(admin_client):
    resp = admin_client.get("/api/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_users" in data
    assert "total_polls" in data
    assert "active_polls" in data
    assert "total_votes" in data
