import os, tempfile
# 服务层测试需要独立数据库；须在导入 app 模块前设定 DATA_DIR
os.environ.setdefault("DATA_DIR", tempfile.mkdtemp(prefix="mortgage-test-"))

import pytest
from app.engines.amortization import equal_payment_schedule
from app import seed
from app.services.mortgage_service import MortgageService

P, RATE, N = 1_000_000, 3.5, 360


# ---------- 引擎 ----------

def test_daily_default_30_matches_plain():
    """启用按日且 D=30（缺省）时，结果与改造前完全一致。"""
    plain = equal_payment_schedule(P, RATE, N)
    daily = equal_payment_schedule(P, RATE, N, first_period_daily=True, first_period_days=30)
    assert daily == plain

def test_daily_first_period_math():
    s = equal_payment_schedule(P, RATE, N, first_period_daily=True, first_period_days=45)
    plain = equal_payment_schedule(P, RATE, N)
    first = s["rows"][0]
    # 首期利息 = 年利率/360 × 本金 × D
    assert first["interest"] == round(P * RATE / 100 / 360 * 45, 2)
    # 首期本金仍按等额本息本金部分
    assert first["principal"] == plain["rows"][0]["principal"]
    # 首期月供 = 首期本金 + 首期按日利息
    assert first["payment"] == round(first["principal"] + first["interest"], 2)
    # 自第二期起恢复常规：与未启用按日的对应期完全一致
    assert s["rows"][1:] == plain["rows"][1:]
    assert s["monthly_payment"] == plain["monthly_payment"]
    # D=45 > 30，总利息应高于常规
    assert s["total_interest"] > plain["total_interest"]

@pytest.mark.parametrize("d", [1, 30, 60])
def test_daily_days_boundary_ok(d):
    s = equal_payment_schedule(P, RATE, N, first_period_daily=True, first_period_days=d)
    assert s["rows"][0]["interest"] == round(P * RATE / 100 / 360 * d, 2)

@pytest.mark.parametrize("d", [0, -1, 61, 1000])
def test_daily_days_out_of_range_rejected(d):
    with pytest.raises(ValueError):
        equal_payment_schedule(P, RATE, N, first_period_daily=True, first_period_days=d)

def test_daily_disabled_ignores_days():
    """未启用按日时 D 不参与计算，结果与改造前一致。"""
    assert equal_payment_schedule(P, RATE, N, first_period_daily=False, first_period_days=100) \
        == equal_payment_schedule(P, RATE, N)


# ---------- 服务层（写库行为） ----------

def _svc():
    seed.init_db()
    return MortgageService()

def test_response_carries_first_period_fields():
    """回包给出 D、首期利息、首期月供与后续月供。"""
    with _svc() as s:
        out = s.schedule(800000, 4.2, 360, None, False, first_period_daily=True, first_period_days=20)
        assert out["run_id"] is None
        assert out["first_period_daily"] is True
        assert out["first_period_days"] == 20
        assert out["first_period_interest"] == round(800000 * 4.2 / 100 / 360 * 20, 2)
        assert out["first_period_payment"] == out["preview"][0]["payment"]
        assert out["monthly_payment"] == out["preview"][1]["payment"]

def test_persist_false_writes_nothing():
    with _svc() as s:
        before = len(s.history(1000))
        out = s.schedule(800000, 4.2, 360, None, False, first_period_daily=True, first_period_days=45)
        assert out["run_id"] is None
        assert len(s.history(1000)) == before

def test_persist_true_then_reopen_first_interest_consistent():
    """带 D 写入后再打开，首期利息须与写入时一致。"""
    with _svc() as s:
        out = s.schedule(800000, 4.2, 360, None, True, first_period_daily=True, first_period_days=45)
        rid = out["run_id"]
        assert rid is not None
        again = s.run(rid)
        assert again["input"]["first_period_daily"] is True
        assert again["input"]["first_period_days"] == 45
        assert again["result"]["first_period_days"] == 45
        assert again["result"]["first_period_interest"] == out["first_period_interest"]
        assert again["result"]["first_period_payment"] == out["first_period_payment"]

def test_out_of_range_days_rejected_and_not_persisted():
    """D 越界则拒绝且不写记录。"""
    with _svc() as s:
        before = len(s.history(1000))
        with pytest.raises(ValueError):
            s.schedule(800000, 4.2, 360, None, True, first_period_daily=True, first_period_days=0)
        assert len(s.history(1000)) == before

def test_schema_rejects_out_of_range_days():
    from pydantic import ValidationError
    from app.schemas.schedule import ScheduleRequest
    with pytest.raises(ValidationError):
        ScheduleRequest(principal=1, annual_rate=1, months=12,
                        first_period_daily=True, first_period_days=61)
