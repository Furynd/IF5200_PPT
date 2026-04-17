from fastapi import FastAPI
from app.api import auth
from app.core.database import engine
from app.models.schema import Base

app = FastAPI(
    title="Referly API", 
    description="Sistem Referal Berbasis Collaborative Filtering",
    version="1.0.0"
)

app.include_router(auth.router)


@app.on_event("startup")
def create_tables() -> None:
    # Ensure required tables exist in local/dev environments.
    Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "Referly Backend is up and running!"}