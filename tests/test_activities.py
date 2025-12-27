import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module
from src.app import app, activities

client = TestClient(app)

# Keep a deep copy of the original activities so tests can reset state
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # Sanity check - expect some known activities from the seed data
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_remove_participant():
    activity = "Chess Club"
    email = "teststudent@mergington.edu"

    # Sign up new participant
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

    # Duplicate signup should be rejected
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Remove participant
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]

    # Removing same participant again should result in 404
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404


def test_remove_from_nonexistent_activity():
    resp = client.delete("/activities/NotExist/participants?email=foo@bar.com")
    assert resp.status_code == 404


def test_signup_nonexistent_activity():
    resp = client.post("/activities/NotExist/signup?email=foo@bar.com")
    assert resp.status_code == 404
