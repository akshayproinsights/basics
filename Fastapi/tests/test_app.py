from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from unittest.mock import Mock
import requests

import pytest
from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

import main
from api_client import ApiClient, ApiError, normalize, status_for, id_path


@pytest.fixture
def client(monkeypatch):
    store = {"1001": {"full_name": "Test Student", "email": "test@example.com", "major": "CS", "gpa": 6.0}}
    monkeypatch.setattr(main, "get_data", lambda: deepcopy(store))
    def save(data):
        store.clear()
        store.update(deepcopy(data))
    monkeypatch.setattr(main, "data_dump_json", save)
    return TestClient(main.app)


def test_contract_and_crud(client):
    assert client.get("/").status_code == 200
    assert normalize(client.get("/data_read").json())[0]["id_new"] == "1001"
    assert client.get("/data_filter", params={"branch": "CS"}).json()
    assert client.get("/data_filter", params={"branch": "cs"}).json() == {}
    assert client.get("/data_sort", params={"sort_by": "gpa", "order": "desc"}).json()[0]["id_new"] == "1001"
    assert client.get("/data_paginate", params={"page": 1, "limit": 1}).json()[0]["id_new"] == "1001"
    assert client.get("/data_paginate", params={"page": 0}).status_code == 422
    student = {"id_new": "test 2", "full_name": "New Student", "email": "new@example.com", "major": "AI", "gpa": 4.0}
    assert client.post("/add_student", json=student).json()["student"]["validate_gpa"] == "Pass"
    assert client.post("/add_student", json=student).status_code == 400
    assert client.put(id_path("update_student", "test 2"), json={"gpa": 9}).json()["student"]["gpa"] == 9
    assert client.put(id_path("update_student", "test 2"), json={"gpa": 11}).status_code == 400
    assert client.get(id_path("data_read", "test 2")).json()["gpa"] == 9
    assert client.delete(id_path("delete_student", "test 2")).status_code == 200
    assert client.get(id_path("data_read", "test 2")).status_code == 404


def test_data_filter_skips_records_without_major(client, monkeypatch):
    data = {
        "1001": {"major": "CS"},
        "1003": {"gpa": 9.9},
    }
    monkeypatch.setattr(main, "get_data", lambda: deepcopy(data))

    response = client.get("/data_filter", params={"branch": "CS"})

    assert response.status_code == 200
    assert response.json() == {"1001": {"major": "CS"}}


@pytest.mark.parametrize("value,status", [(0,"Fail"),(3,"Fail"),(3.1,"Pass"),(5,"Pass"),(5.1,"Excellent"),(10,"Excellent"),(11,"Invalid GPA"),(None,"Invalid GPA")])
def test_status(value, status):
    assert status_for(value) == status


def test_normalization():
    source = {"1003": {"gpa": 9.9}, "bad": {"gpa": 10000}}
    before = deepcopy(source)
    rows = normalize(source)
    assert source == before
    assert all(row["data_quality"] == "Needs review" for row in rows)
    assert rows[1]["validate_gpa"] == "Invalid GPA"
    with pytest.raises(ApiError):
        normalize([1])


def test_ui(client):
    def request(method, url, **kwargs):
        kwargs.pop("timeout", None)
        response = client.request(method, url.replace("http://127.0.0.1:8000", ""), **kwargs)
        response.ok = response.is_success
        return response
    with patch("api_client.requests.request", side_effect=request):
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "streamlit_app.py").run(timeout=20)
        assert not app.exception
        assert app.metric[0].value == "1"
        app.text_input[0].set_value("missing").run()
        assert not app.exception


def test_ui_with_incomplete_data():
    data = {"1003": {"gpa": 9.9}, "bad": {"full_name": "Bad GPA", "major": "CS", "gpa": 10000}}
    def request(self, method, path, **kwargs):
        if path == "/data_read":
            return data
        if path == "/data_paginate":
            return [{"id_new": key, **row} for key, row in data.items()]
        raise ApiError("HTTP 500: backend record is incomplete")
    with patch.object(ApiClient, "request", request):
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "streamlit_app.py").run(timeout=30)
        assert not app.exception
        assert app.metric[3].value == "2"
        next(s for s in app.selectbox if s.label == "Major").select("CS").run()
        assert not app.exception
        assert app.warning
        next(s for s in app.selectbox if s.label == "Sort by").select("major").run()
        assert not app.exception


def test_offline_ui():
    with patch.object(ApiClient, "request", side_effect=ApiError("API offline")):
        app = AppTest.from_file(Path(__file__).resolve().parents[1] / "streamlit_app.py").run(timeout=20)
        assert not app.exception
        assert any("API offline" in e.value for e in app.error)


def test_http_failures_and_logging():
    log = []
    api = ApiClient("http://localhost:8000/", log)
    response = Mock(status_code=422, ok=False)
    response.json.return_value = {"detail": [{"loc": ["body", "email"], "msg": "Invalid email"}]}
    with patch("api_client.requests.request", return_value=response):
        with pytest.raises(ApiError, match="body.email: Invalid email"):
            api.request("POST", "/add_student", json={})
    response.json.side_effect = ValueError()
    with patch("api_client.requests.request", return_value=response):
        with pytest.raises(ApiError, match="non-JSON"):
            api.request("GET", "/data_read")
    with patch("api_client.requests.request", side_effect=requests.Timeout("timeout")):
        with pytest.raises(ApiError, match="Cannot reach"):
            api.request("GET", "/data_read")
    assert len(log) == 3
    assert log[-1]["Status"] == "Network error"
