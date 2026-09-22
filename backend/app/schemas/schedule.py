from pydantic import BaseModel, Field
from app.engines.amortization import FIRST_PERIOD_DAYS_DEFAULT, FIRST_PERIOD_DAYS_MAX, FIRST_PERIOD_DAYS_MIN

class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
    first_period_daily: bool = False
    # 起息日到首次还款日的实际天数 D；越界直接 422，不进入服务层、不写记录
    first_period_days: int = Field(default=FIRST_PERIOD_DAYS_DEFAULT, ge=FIRST_PERIOD_DAYS_MIN, le=FIRST_PERIOD_DAYS_MAX)
