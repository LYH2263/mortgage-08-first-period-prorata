import json
from app.db import connect
from app.engines.amortization import equal_payment_schedule
from app.repositories import loans, runs, settings

class MortgageService:
    def __init__(self): self._c = connect()
    def close(self): self._c.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()
    def list_loans(self): return loans.list_all(self._c)
    def loan(self, lid): return loans.get(self._c, lid)
    def settings(self): return settings.get_map(self._c)
    def history(self, limit=50): return runs.list_recent(self._c, limit)
    def run(self, rid):
        r = runs.get(self._c, rid)
        if not r: return None
        r["input"] = json.loads(r.pop("input_json"))
        r["result"] = json.loads(r.pop("result_json"))
        return r
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12,
                 first_period_daily=False, first_period_days=30):
        # 引擎在 D 越界时抛 ValueError，先于任何写库，保证越界请求不留记录
        full = equal_payment_schedule(principal, annual_rate, months,
                                      first_period_daily=first_period_daily,
                                      first_period_days=first_period_days)
        out = {k: full[k] for k in ("monthly_payment", "total_interest", "total_payment")}
        out["first_period_daily"] = bool(first_period_daily)
        out["first_period_days"] = int(first_period_days) if first_period_daily else None
        out["first_period_interest"] = full["rows"][0]["interest"]
        out["first_period_payment"] = full["rows"][0]["payment"]
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            rid = runs.insert(self._c, "schedule", {
                "principal": principal, "annual_rate": annual_rate, "months": months,
                "first_period_daily": bool(first_period_daily),
                "first_period_days": out["first_period_days"],
            }, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
