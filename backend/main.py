from fastapi import FastAPI
from routers import leads

app = FastAPI()

app.include_router(leads.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "API da Prospectiva funcionando!"}
    
@app.get("/status")
def status():
    return {"ok": True, "service": "prospectiva"}

@app.post("/lead")
def create_lead(payload: dict):
    return {"received": payload}
