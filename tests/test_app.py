import pytest
import os
os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost/fake"
os.environ["OPENWEATHER_API_KEY"] = "fakekey"

from unittest.mock import patch, MagicMock
from app import create_app

@pytest.fixture
def client():
    with patch("app.database.init_db"):
        app = create_app()
    app.config["TESTING"] = True
    return app.test_client()

def test_health_endpoint_db_down(client):
    with patch("app.routes.get_connection", side_effect=Exception("no db")):
        res = client.get("/health")
        data = res.get_json()
        assert res.status_code == 503
        assert data["db"] is False

def test_weather_missing_city(client):
    res = client.get("/weather")
    assert res.status_code == 400
    assert "error" in res.get_json()

def test_returns_joined_result_when_both_sources_available(client):
    mock_weather = {
        "city": "Dublin", "country": "IE", "temperature": 12.0,
        "feels_like": 10.0, "humidity": 80, "description": "Cloudy", "icon": "04d"
    }
    with patch("app.routes.get_weather", return_value=mock_weather), \
         patch("app.routes.save_search"):
        res = client.get("/weather?city=Dublin")
        assert res.status_code == 200
        assert res.get_json()["city"] == "Dublin"

def test_graceful_degradation_on_upstream_failure(client):
    with patch("app.routes.get_weather", return_value={"error": "Weather service unavailable. Please try again later."}):
        res = client.get("/weather?city=Dublin")
        data = res.get_json()
        assert "error" in data

def test_health_endpoint_reports_dependencies(client):
    mock_conn = MagicMock()
    with patch("app.routes.get_connection", return_value=mock_conn):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.get_json()["db"] is True