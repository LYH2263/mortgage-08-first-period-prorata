from app.modules.first_period_daily import (
    DEFAULT_FIRST_PERIOD_DAYS,
    daily_first_interest,
    normalize_days,
)


def equal_payment_schedule(principal: float, annual_rate: float, months: int, first_period_days=None) -> dict:
    """等额本息摊还表。

    first_period_days 为起息日到首次还款日的实际天数 D，缺省 30（与改造前
    完全一致）。启用按日计息（D != 30）时，首期利息改为
    年利率 / 360 × 本金 × D，首期本金仍取等额本息的首期本金部分，因此首期
    之后的余额与标准表一致，自第二期起恢复常规月供。
    """
    days = normalize_days(first_period_days)
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        interest = bal * r
        principal_part = pay - interest
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        else:
            pay_i = pay
        bal = max(0.0, bal - principal_part)
        interest_sum += interest
        rows.append({
            "period": i,
            "payment": round(pay_i, 2),
            "principal": round(principal_part, 2),
            "interest": round(interest, 2),
            "balance": round(bal, 2),
        })
    if days != DEFAULT_FIRST_PERIOD_DAYS:
        # 首期按日计息：仅替换首期利息与月供，本金部分不变，
        # 故首期后余额与标准表一致，后续各行保持常规。
        first = dict(rows[0])
        first_interest_raw = daily_first_interest(P, annual_rate, days)
        first_principal_raw = pay - P * r if n > 1 else P
        first["interest"] = round(first_interest_raw, 2)
        first["principal"] = round(first_principal_raw, 2)
        first["payment"] = round(first_interest_raw + first_principal_raw, 2)
        rows = [first, *rows[1:]]
        total_interest = round(interest_sum - P * r + first_interest_raw, 2)
    else:
        total_interest = round(interest_sum, 2)
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": total_interest,
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "first_period_days": days,
        "daily_first_interest": days != DEFAULT_FIRST_PERIOD_DAYS,
        "first_interest": rows[0]["interest"],
        "first_principal": rows[0]["principal"],
        "first_payment": rows[0]["payment"],
        "subsequent_payment": round(pay if n else 0, 2),
        "rows": rows,
    }
