from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth
from app.core.database import engine
from app.models.schema import Base

from app.db.neo4j import init_neo4j, close_neo4j
from app.core.database import engine
from app.models.schema import Base
from app.routers import connections, companies, cv, recommendations, referrals, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    await init_neo4j()
    yield
    await close_neo4j()


app = FastAPI(title="Referly API",
              description="Sistem Referal Berbasis Collaborative Filtering",
              version="1.0.0",
              lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "https://if-5200-ppt-git-dev-integration-referlyfufufafa-6551s-projects.vercel.app/", 
                   "https://if-5200-i7lo1heo8-referlyfufufafa-6551s-projects.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(connections.router, prefix="/api")
app.include_router(companies.router, prefix="/api")
app.include_router(cv.router, prefix="/api")
app.include_router(referrals.router, prefix="/api")
app.include_router(recommendations.router, prefix="/api")
app.include_router(users.router, prefix="/api")

@app.on_event("startup")
def create_tables() -> None:
    # Ensure required tables exist in local/dev environments.
    Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "Referly Backend is up and running!"}