import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_activity(monkeypatch):
    activity_name = "Test Activity"
    activity = {
        "description": "An activity created for API tests",
        "schedule": "Mondays, 3:00 PM - 4:00 PM",
        "max_participants": 5,
        "participants": [],
    }
    monkeypatch.setitem(activities, activity_name, activity)
    return activity_name, activity


def test_get_activities_returns_activity_details(client, test_activity):
    # Arrange
    activity_name, activity = test_activity

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json()[activity_name] == activity


def test_signup_adds_participant(client, test_activity):
    # Arrange
    activity_name, activity = test_activity
    email = "student@example.com"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert activity["participants"] == [email]


def test_signup_rejects_duplicate_participant(client, test_activity):
    # Arrange
    activity_name, activity = test_activity
    email = "student@example.com"
    activity["participants"].append(email)

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activity["participants"] == [email]


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client, test_activity):
    # Arrange
    activity_name, activity = test_activity
    email = "student@example.com"
    activity["participants"].append(email)

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert activity["participants"] == []


def test_unregister_returns_not_found_for_missing_participant(client, test_activity):
    # Arrange
    activity_name, activity = test_activity
    email = "student@example.com"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activity["participants"] == []


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"