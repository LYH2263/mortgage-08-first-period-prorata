# 首期按日计息：起息日到首次还款日的实际天数 D 的合法范围与缺省值。
# 缺省 30 天时，年利率/360×30 与月利率（年利率/12）相等，结果与改造前一致。
FIRST_PERIOD_DAYS_DEFAULT = 30
FIRST_PERIOD_DAYS_MIN = 1
FIRST_PERIOD_DAYS_MAX = 60


def equal_payment_schedule(principal: float, annual_rate: float, months: int,
                           first_period_daily: bool = False,
                           first_period_days: int = FIRST_PERIOD_DAYS_DEFAULT) -> dict:
    P = float(principal)
    n = int(months)
    r = float(annual_rate) / 12.0 / 100.0
    if n <= 0:
        raise ValueError("months")
    if first_period_daily and not FIRST_PERIOD_DAYS_MIN <= int(first_period_days) <= FIRST_PERIOD_DAYS_MAX:
        raise ValueError("first_period_days")
    if r == 0:
        pay = P / n
    else:
        pay = P * r * (1 + r) ** n / ((1 + r) ** n - 1)
    rows = []
    bal = P
    interest_sum = 0.0
    for i in range(1, n + 1):
        daily_first = first_period_daily and i == 1
        if daily_first:
            # 首期按日：利息 = 年利率/360 × 本金 × D
            interest = P * float(annual_rate) / 100.0 / 360.0 * int(first_period_days)
        else:
            interest = bal * r
        if i == n:
            principal_part = bal
            pay_i = principal_part + interest
        elif daily_first:
            # 首期本金仍按等额本息本金部分，月供 = 该本金 + 按日利息；第二期起恢复常规
            principal_part = pay - bal * r
            pay_i = principal_part + interest
        else:
            principal_part = pay - interest
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
    return {
        "monthly_payment": round(pay if n else 0, 2),
        "total_interest": round(interest_sum, 2),
        "total_payment": round(sum(x["payment"] for x in rows), 2),
        "rows": rows,
    }
