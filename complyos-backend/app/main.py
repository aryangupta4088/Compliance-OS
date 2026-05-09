from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth, documents, compliance, ws_aria,
    business, ca, loans, freelancers, 
    notifications, registration, admin
)
from app.database import init_db

app = FastAPI(title="ComplianceOS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(auth.router, prefix="/auth")
app.include_router(documents.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(business.router, prefix="/api")
app.include_router(ca.router, prefix="/api")
app.include_router(loans.router, prefix="/api")
app.include_router(freelancers.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(registration.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(ws_aria.router)

@app.get("/health")
async def health():
    return {"status": "operational"}