from .utils import make_team


def test_set_user_active(client):
    team_data = make_team("backend", [("u1", "Alice", True)])
    client.post("/team/add", json=team_data)
    response = client.post(
        "/users/setIsActive", json={"user_id": "u1", "is_active": False}
    )
    assert response.status_code == 200
    user = response.json()
    assert user["is_active"] is False


def test_set_nonexistent_user_active(client):
    response = client.post(
        "/users/setIsActive", json={"user_id": "xxx", "is_active": False}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_get_user_reviews(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post(
        "/pullRequest/create",
        json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"},
    )
    response = client.get("/users/getReview?user_id=u2")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "u2"
    assert len(data["pull_requests"]) == 1
    assert data["pull_requests"][0]["pull_request_id"] == "pr1"
