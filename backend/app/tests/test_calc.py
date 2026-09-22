import pytest
from app.engines.amortization import equal_payment_schedule

def test_monthly_payment():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["monthly_payment"] == 4490.45

def test_first_period_interest():
    s = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][0]["interest"] == 2916.67
    assert s["rows"][0]["period"] == 1

def test_zero_rate():
    s = equal_payment_schedule(120000, 0, 12)
    assert s["monthly_payment"] == 10000.0

def test_bad_months():
    with pytest.raises(ValueError):
        equal_payment_schedule(100, 3, 0)

def test_default_days_is_thirty_and_matches_explicit():
    # 缺省按 30 天，与改造前完全一致
    implicit = equal_payment_schedule(1_000_000, 3.5, 360)
    explicit = equal_payment_schedule(1_000_000, 3.5, 360, 30)
    assert implicit == explicit
    assert implicit["first_period_days"] == 30
    assert implicit["daily_first_interest"] is False
    assert implicit["first_interest"] == 2916.67
    assert implicit["first_payment"] == implicit["subsequent_payment"] == implicit["monthly_payment"]

def test_daily_first_period_interest():
    # 年利率 / 360 × 本金 × D = 3.5% / 360 × 1_000_000 × 45 = 4375.0
    s = equal_payment_schedule(1_000_000, 3.5, 360, 45)
    assert s["first_period_days"] == 45
    assert s["daily_first_interest"] is True
    assert s["first_interest"] == 4375.0
    # 首期本金仍为等额本息首期本金部分：4490.45 - 2916.67
    assert s["first_principal"] == 1573.78
    assert s["first_payment"] == 5948.78
    # 自第二期起恢复常规月供
    assert s["subsequent_payment"] == 4490.45
    assert s["rows"][0]["payment"] == 5948.78
    assert s["rows"][1]["payment"] == 4490.45
    # 首期本金不变 → 首期后余额与标准表一致
    base = equal_payment_schedule(1_000_000, 3.5, 360)
    assert s["rows"][1:] == base["rows"][1:]

def test_daily_first_period_zero_rate():
    s = equal_payment_schedule(120000, 0, 12, 45)
    assert s["first_interest"] == 0
    assert s["first_principal"] == 10000.0
    assert s["first_payment"] == 10000.0
    assert s["subsequent_payment"] == 10000.0

def test_days_out_of_range_rejected():
    with pytest.raises(ValueError):
        equal_payment_schedule(1_000_000, 3.5, 360, 0)
    with pytest.raises(ValueError):
        equal_payment_schedule(1_000_000, 3.5, 360, 91)
