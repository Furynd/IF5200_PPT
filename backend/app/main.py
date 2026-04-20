from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.neo4j import init_neo4j, close_neo4j
from app.routers import connections


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_neo4j()
    yield
    await close_neo4j()


app = FastAPI(title="Referly API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connections.router, prefix="/api")
