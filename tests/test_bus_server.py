import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from bus_server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_bus_missing_param(client):
    response = client.get('/bus')
    assert response.status_code == 400
    assert b"Missing 'bus_stop_code' parameter" in response.data

def test_bus_with_param(monkeypatch, client):
    # Mock requests.get to avoid real API call
    class MockResponse:
        def raise_for_status(self): pass
        def json(self): return {"mock": "bus"}
    monkeypatch.setattr('requests.get', lambda *a, **kw: MockResponse())
    response = client.get('/bus?bus_stop_code=12345')
    assert response.status_code == 200
    assert response.get_json() == {"mock": "bus"}

def test_rainfall_station_not_found(monkeypatch, client):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self): return {"data": {"stations": [], "readings": []}}
    monkeypatch.setattr('requests.get', lambda *a, **kw: MockResponse())
    response = client.get('/rainfall')
    assert response.status_code == 404
    assert b"Station not found" in response.data

def test_rainfall_reading_found(monkeypatch, client):
    class MockResponse:
        def raise_for_status(self): pass
        def json(self):
            return {
                "data": {
                    "stations": [{"id": "S227", "name": "Woodlands Drive 62"}],
                    "readings": [{
                        "timestamp": "2025-08-30T11:10:00+08:00",
                        "data": [{"stationId": "S227", "value": 0}],
                        "readingUnit": "mm"
                    }]
                }
            }
    monkeypatch.setattr('requests.get', lambda *a, **kw: MockResponse())
    response = client.get('/rainfall')
    assert response.status_code == 200
    data = response.get_json()
    assert data["station"]["id"] == "S227"
    assert data["rainfall"] == 0
    assert data["unit"] == "mm"
