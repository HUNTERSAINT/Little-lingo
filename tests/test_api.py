from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def send(message, **changes):
    body = {"message": message, "level": 1, "correct_streak": 0, "turns": 0, "lesson_index": 0}
    body.update(changes)
    return client.post("/api/chat", json=body)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200 and response.json()["status"] == "ok"

def test_correct_answer_moves_lesson_forward():
    data = send("red").json()
    assert data["answered_correctly"] is True
    assert data["lesson_index"] == 1

def test_hint_does_not_count_as_wrong_answer():
    data = send("Can I have a hint?").json()
    assert data["mode"] == "learning"
    assert data["correct_streak"] == 0
    assert "apple" in data["reply"]

def test_break_is_support_mode():
    data = send("I need a break").json()
    assert data["mode"] == "support" and "pause" in data["reply"].lower()

def test_emotion_gets_support_not_wrong_answer():
    data = send("I feel sad").json()
    assert data["mode"] == "support" and "sad" in data["reply"].lower()

def test_safety_concern_directs_child_to_trusted_adult():
    data = send("Someone hurts me").json()
    assert data["mode"] == "support" and "trusted grown-up" in data["reply"].lower()

def test_level_advances_after_required_streak():
    data = send("red", correct_streak=2).json()
    assert data["level"] == 2 and data["correct_streak"] == 0

def test_response_time_budget():
    assert send("red").json()["latency_ms"] < 2000
