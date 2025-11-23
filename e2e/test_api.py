import os
import requests
import pytest

BASE_URL = os.getenv("INTEGRATION_TEST_BASE_URL", "http://localhost:8080")


@pytest.mark.integration
def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.integration
def test_create_team_and_get():
    team_name = "test-team-integ"

    create_resp = requests.post(f"{BASE_URL}/team/add", json={"team_name": team_name})
    assert create_resp.status_code == 201

    get_resp = requests.get(f"{BASE_URL}/team/get?team_name={team_name}")
    assert get_resp.status_code == 200
    assert get_resp.json()["team_name"] == team_name
