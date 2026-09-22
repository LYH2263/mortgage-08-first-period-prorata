from fastapi import APIRouter, HTTPException
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/runs/{run_id}")
def get_run(run_id: int):
    with MortgageService() as s:
        row = s.run(run_id)
        if not row: raise HTTPException(404)
        return row
