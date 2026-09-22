DEFAULT_FIRST_PERIOD_DAYS = 30
MIN_FIRST_PERIOD_DAYS = 1
MAX_FIRST_PERIOD_DAYS = 90
DAYS_PER_YEAR = 360


def normalize_days(first_period_days) -> int:
    """起息日到首次还款日的实际天数；缺省 30，与改造前口径一致。"""
    if first_period_days is None:
        return DEFAULT_FIRST_PERIOD_DAYS
    d = int(first_period_days)
    if d < MIN_FIRST_PERIOD_DAYS or d > MAX_FIRST_PERIOD_DAYS:
        raise ValueError("first_period_days")
    return d


def daily_first_interest(principal: float, annual_rate: float, days: int) -> float:
    """首期按日利息：年利率 / 360 × 本金 × D。"""
    return float(principal) * (float(annual_rate) / 100.0) / DAYS_PER_YEAR * days
