# 15-mortgage（房贷月供）

Mortgage — 等额本息月供与逐期本金利息拆分

## 启动

```bash
docker compose up --build
```

| 入口 | 地址 |
| --- | --- |
| 前端 | http://localhost:4400 |
| API | http://localhost:9400 |

## 主链

贷额期限利率 → 等额本息还款表 → 利息合计

## 首期按日计息

- 试算台勾选「首期按日计息」后可提交起息日至首次还款日的实际天数 D（缺省 30，此时与常规月供完全一致）。
- 首期利息 = 年利率 ÷ 360 × 本金 × D；首期本金仍按等额本息本金部分，自第二期起恢复常规。
- `POST /api/schedule` 增加 `first_period_daily`、`first_period_days`；回包含 `first_period_days`、`first_period_interest`、`first_period_payment` 与后续月供 `monthly_payment`。
- D 合法范围 1–60，越界拒绝（422）且不写记录；`persist=false` 不写记录。
- `GET /api/history/{id}` 可再打开已写入的试算，首期利息与写入时一致。

## 技术栈

Python 3.12 + FastAPI + SQLite；Vue 3 + Vite + Nginx。
