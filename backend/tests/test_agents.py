import pytest
from fastapi.testclient import TestClient
from ...main import app

client = TestClient(app)

def test_start_quiz():
    response = client.post("/courses/quiz/start")
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert data["question"] == "What is the capital of France?"

def test_answer_quiz_correct():
    state = {
        "question": "What is the capital of France?",
        "answer": "Paris",
        "history": [],
        "feedback": "",
        "difficulty": "easy"
    }
    response = client.post("/courses/quiz/answer", json=state)
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"] == "Correct!"
    assert data["difficulty"] == "medium"

def test_answer_quiz_incorrect():
    state = {
        "question": "What is the capital of France?",
        "answer": "London",
        "history": [],
        "feedback": "",
        "difficulty": "easy"
    }
    response = client.post("/courses/quiz/answer", json=state)
    assert response.status_code == 200
    data = response.json()
    assert data["feedback"] == "Incorrect. The correct answer is Paris."
    assert data["difficulty"] == "easy"

def test_submit_for_peer_review():
    submission = {
        "submission": "This is my work.",
        "reviewers": [],
        "feedback": [],
        "status": ""
    }
    response = client.post("/courses/peer_review/submit", json=submission)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
