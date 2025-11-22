from .utils import make_team

def test_create_pr(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True), ("u3", "Charlie", True)])
    client.post("/team/add", json=team_data)
    response = client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    assert response.status_code == 201
    pr = response.json()
    assert pr["author_id"] == "u1"
    assert pr["status"] == "OPEN"
    assert len(pr["assigned_reviewers"]) == 2
    assert "u1" not in pr["assigned_reviewers"]

def test_create_pr_author_not_found(client):
    response = client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "unknown"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"

def test_create_duplicate_pr(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    response = client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix2", "author_id": "u1"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PR_EXISTS"

def test_merge_pr(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    response = client.post("/pullRequest/merge", json={"pull_request_id": "pr1"})
    assert response.status_code == 200
    pr = response.json()
    assert pr["status"] == "MERGED"
    assert pr["mergedAt"] is not None

def test_merge_idempotent(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    client.post("/pullRequest/merge", json={"pull_request_id": "pr1"})
    response = client.post("/pullRequest/merge", json={"pull_request_id": "pr1"})
    assert response.status_code == 200

def test_reassign_non_assigned_reviewer(client):
    team_data = make_team("backend", [
        ("u1", "Alice", True),
        ("u2", "Bob", True),
        ("u3", "Charlie", True),
        ("u4", "David", True)
    ])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    response = client.post("/pullRequest/reassign", json={"pull_request_id": "pr1", "old_user_id": "u4"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "NOT_ASSIGNED"

def test_reassign_on_merged_pr(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    client.post("/pullRequest/merge", json={"pull_request_id": "pr1"})
    response = client.post("/pullRequest/reassign", json={"pull_request_id": "pr1", "old_user_id": "u2"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "PR_MERGED"


def test_reassign_non_assigned_reviewer(client):
    team_data = make_team("backend", [
        ("u1", "Alice", True),
        ("u2", "Bob", True),
        ("u3", "Charlie", True),
        ("u4", "David", True)
    ])
    client.post("/team/add", json=team_data)

    client.post("/pullRequest/create", json={
        "pull_request_id": "pr1",
        "pull_request_name": "Fix",
        "author_id": "u1"
    })

    response = client.post("/pullRequest/reassign", json={
        "pull_request_id": "pr1",
        "old_user_id": "u4"
    })

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "NOT_ASSIGNED"


def test_no_candidates_for_reassign(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", True)])
    client.post("/team/add", json=team_data)
    client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    client.post("/users/setIsActive", json={"user_id": "u2", "is_active": False})
    response = client.post("/pullRequest/reassign", json={"pull_request_id": "pr1", "old_user_id": "u2"})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "NO_CANDIDATE"

def test_inactive_users_not_assigned(client):
    team_data = make_team("backend", [("u1", "Alice", True), ("u2", "Bob", False), ("u3", "Charlie", True)])
    client.post("/team/add", json=team_data)
    response = client.post("/pullRequest/create", json={"pull_request_id": "pr1", "pull_request_name": "Fix", "author_id": "u1"})
    reviewers = response.json()["assigned_reviewers"]
    assert "u2" not in reviewers
    assert reviewers == ["u3"]