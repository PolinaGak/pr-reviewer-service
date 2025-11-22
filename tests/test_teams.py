from .utils import make_team


def test_create_team(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 201
    data = response.json()
    assert data["team_name"] == "backend"
    assert len(data["members"]) == 2


def test_create_existing_team(client):
    team_data = make_team("backend", [("u1", "Alice", True)])
    client.post("/team/add", json=team_data)
    response = client.post("/team/add", json=team_data)
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "TEAM_EXISTS"


def test_get_team(client):
    team_data = make_team("backend", [("u1", "Alice", True)])
    client.post("/team/add", json=team_data)
    response = client.get("/team/get?team_name=backend")
    assert response.status_code == 200
    assert response.json()["team_name"] == "backend"


def test_get_nonexistent_team(client):
    response = client.get("/team/get?team_name=unknown")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
