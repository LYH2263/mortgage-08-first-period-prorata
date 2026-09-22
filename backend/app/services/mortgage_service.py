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
    def run(self, rid): return runs.get(self._c, rid)
    def schedule(self, principal, annual_rate, months, loan_id, persist, preview_rows=12, first_period_days=None):
        full = equal_payment_schedule(principal, annual_rate, months, first_period_days)
        out = {k: full[k] for k in (
            "monthly_payment", "total_interest", "total_payment",
            "first_period_days", "daily_first_interest",
            "first_interest", "first_principal", "first_payment", "subsequent_payment",
        )}
        out["preview"] = full["rows"][:preview_rows]
        out["row_count"] = len(full["rows"])
        rid = None
        if persist:
            payload = {"principal": principal, "annual_rate": annual_rate, "months": months,
                       "first_period_days": full["first_period_days"]}
            rid = runs.insert(self._c, "schedule", payload, out, loan_id)
        return {"run_id": rid, **out}
    def dashboard(self):
        items = loans.list_all(self._c)
        return {"loan_count": len(items), "clean": len([x for x in items if "种子" not in x["name"]]), "dirty": len([x for x in items if "种子" in x["name"]])}
