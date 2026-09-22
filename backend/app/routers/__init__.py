from fastapi import APIRouter
from app.routers import dashboard, history, loans, runs, schedule, settings
api = APIRouter(prefix="/api")
for r in (dashboard, loans, schedule, runs, history, settings): api.include_router(r.router)
