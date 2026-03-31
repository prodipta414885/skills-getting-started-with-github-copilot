"""
Tests for the FastAPI application endpoints.
"""

import pytest


def test_root_redirect(client):
    """Test that root endpoint redirects to static/index.html."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    # Verify structure and expected activities exist
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    
    # Verify Chess Club details
    chess = data["Chess Club"]
    assert chess["description"] == "Learn strategies and compete in chess tournaments"
    assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess["max_participants"] == 12
    assert len(chess["participants"]) == 2


def test_signup_for_activity_success(client):
    """Test successfully signing up for an activity."""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "Signed up newstudent@mergington.edu for Chess Club" in data["message"]
    
    # Verify the student was added
    activities = client.get("/activities").json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_activity_not_found(client):
    """Test signing up for a non-existent activity."""
    response = client.post(
        "/activities/Non-Existent Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_multiple_students(client):
    """Test that multiple students can sign up for the same activity."""
    # Get initial count
    initial_activities = client.get("/activities").json()
    initial_gym_count = len(initial_activities["Gym Class"]["participants"])
    
    # Sign up two students
    response1 = client.post(
        "/activities/Gym Class/signup?email=student1@mergington.edu"
    )
    response2 = client.post(
        "/activities/Gym Class/signup?email=student2@mergington.edu"
    )
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify both were added
    activities = client.get("/activities").json()
    gym_participants = activities["Gym Class"]["participants"]
    assert len(gym_participants) == initial_gym_count + 2
    assert "student1@mergington.edu" in gym_participants
    assert "student2@mergington.edu" in gym_participants


def test_signup_preserves_existing_participants(client):
    """Test that signing up doesn't remove existing participants."""
    # Get initial participants
    initial = client.get("/activities").json()
    initial_chess_participants = set(initial["Chess Club"]["participants"])
    
    # Sign up a new student
    client.post("/activities/Chess Club/signup?email=new@mergington.edu")
    
    # Verify original participants are still there
    updated = client.get("/activities").json()
    updated_participants = set(updated["Chess Club"]["participants"])
    
    # Original participants should be subset
    assert initial_chess_participants.issubset(updated_participants)
    assert "new@mergington.edu" in updated_participants


def test_activities_structure(client):
    """Test that each activity has the required fields."""
    response = client.get("/activities")
    data = response.json()
    
    required_fields = {"description", "schedule", "max_participants", "participants"}
    
    for activity_name, activity_data in data.items():
        assert isinstance(activity_name, str)
        assert required_fields.issubset(activity_data.keys())
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
