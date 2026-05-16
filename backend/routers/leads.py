from fastapi import APIRouter

router = APIRouter(prefix="/leads", tags=["Leads"])

fake_db = []

@router.post("/")
def create_lead(payload: dict):
    fake_db.append(payload)
    return {"status": "ok", "saved": payload}

@router.get("/")
def list_leads():
    return fake_db