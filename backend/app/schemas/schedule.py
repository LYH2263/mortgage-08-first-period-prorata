from pydantic import BaseModel, Field
class ScheduleRequest(BaseModel):
    principal: float = Field(gt=0)
    annual_rate: float = Field(ge=0)
    months: int = Field(gt=0, le=600)
    # 起息日到首次还款日的实际天数 D；缺省/为空按 30，与改造前口径一致。
    # 越界（非 1..90）直接 422 拒绝，不写任何记录。
    first_period_days: int | None = Field(default=None, ge=1, le=90)
    loan_id: int | None = None
    persist: bool = True
    preview_rows: int = Field(default=12, ge=1, le=120)
