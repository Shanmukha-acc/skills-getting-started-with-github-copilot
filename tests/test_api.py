import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball Team" in data
    assert "participants" in data["Basketball Team"]

def test_root_redirect():
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to /static/index.html

def test_signup_success():
    # First, get initial participants
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Basketball Team"]["participants"])
    
    # Sign up a new participant
    response = client.post("/activities/Basketball%20Team/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test@example.com for Basketball Team" in data["message"]
    
    # Check that participant was added
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Basketball Team"]["participants"])
    assert updated_count == initial_count + 1
    assert "test@example.com" in updated_data["Basketball Team"]["participants"]

def test_signup_duplicate():
    # Sign up first time
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")
    assert response.status_code == 200
    
    # Try to sign up again
    response = client.post("/activities/Basketball%20Team/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student already signed up" in data["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Invalid%20Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]

def test_unregister_success():
    # First sign up
    client.post("/activities/Tennis%20Club/signup?email=unregister@example.com")
    
    # Get initial count
    response = client.get("/activities")
    initial_data = response.json()
    initial_count = len(initial_data["Tennis Club"]["participants"])
    
    # Unregister
    response = client.delete("/activities/Tennis%20Club/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered unregister@example.com from Tennis Club" in data["message"]
    
    # Check that participant was removed
    response = client.get("/activities")
    updated_data = response.json()
    updated_count = len(updated_data["Tennis Club"]["participants"])
    assert updated_count == initial_count - 1
    assert "unregister@example.com" not in updated_data["Tennis Club"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball%20Team/unregister?email=notsignedup@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "Student not signed up" in data["detail"]

def test_unregister_invalid_activity():
    response = client.delete("/activities/Invalid%20Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]