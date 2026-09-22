import importlib
import json

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    import app.config as config
    importlib.reload(config)
    import app.db as db
    importlib.reload(db)
    import app.seed as seed
    importlib.reload(seed)
    import app.main as main
    importlib.reload(main)
    with TestClient(main.app) as c:
        yield c, db


def _run_count(db):
    with db.connect() as conn:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]


def test_default_schedule_unchanged(client):
    c, _ = client
    r = c.post("/api/schedule", json={"principal": 1_000_000, "annual_rate": 3.5, "months": 360, "persist": False})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is None
    assert body["first_period_days"] == 30
    assert body["daily_first_interest"] is False
    assert body["first_interest"] == 2916.67
    assert body["first_payment"] == body["subsequent_payment"] == body["monthly_payment"]


def test_daily_first_period_trial(client):
    c, _ = client
    r = c.post("/api/schedule", json={"principal": 1_000_000, "annual_rate": 3.5, "months": 360,
                                      "first_period_days": 45, "persist": False})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is None
    assert body["first_period_days"] == 45
    assert body["first_interest"] == 4375.0
    assert body["first_payment"] == 5948.78
    assert body["subsequent_payment"] == 4490.45


def test_persist_false_writes_nothing(client):
    c, db = client
    before = _run_count(db)
    r = c.post("/api/schedule", json={"principal": 800000, "annual_rate": 4.2, "months": 240,
                                      "first_period_days": 45, "persist": False})
    assert r.status_code == 200
    assert r.json()["run_id"] is None
    assert _run_count(db) == before


def test_days_out_of_range_rejected_and_not_persisted(client):
    c, db = client
    for bad in (0, 91, -1):
        before = _run_count(db)
        r = c.post("/api/schedule", json={"principal": 800000, "annual_rate": 4.2, "months": 240,
                                          "first_period_days": bad, "persist": True})
        assert r.status_code == 422, bad
        assert _run_count(db) == before


def test_persisted_run_reopens_with_same_first_interest(client):
    c, db = client
    r = c.post("/api/schedule", json={"principal": 1_000_000, "annual_rate": 3.5, "months": 360,
                                      "first_period_days": 45, "persist": True})
    assert r.status_code == 200
    written = r.json()
    rid = written["run_id"]
    assert rid is not None

    got = c.get(f"/api/runs/{rid}")
    assert got.status_code == 200
    record = got.json()
    # 再打开：首期利息须与写入时一致
    assert record["result_json"]["first_interest"] == written["first_interest"] == 4375.0
    assert record["result_json"]["first_payment"] == written["first_payment"]
    assert record["input_json"]["first_period_days"] == 45

    # 按写入的输入重算，结果同样一致
    from app.engines.amortization import equal_payment_schedule
    recalc = equal_payment_schedule(**{k: record["input_json"][k] for k in ("principal", "annual_rate", "months", "first_period_days")})
    assert recalc["first_interest"] == record["result_json"]["first_interest"]


def test_missing_run_404(client):
    c, _ = client
    assert c.get("/api/runs/99999").status_code == 404
