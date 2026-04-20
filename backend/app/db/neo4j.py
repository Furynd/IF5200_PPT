"""
Neo4j async driver singleton.

Usage in FastAPI:
    from app.db.neo4j import get_neo4j_driver

    async def my_endpoint(driver = Depends(get_neo4j_driver)):
        async with driver.session() as session:
            ...
"""

import os
from pathlib import Path
from neo4j import AsyncGraphDatabase, AsyncDriver
from dotenv import load_dotenv

# Explicit path so this works regardless of where uvicorn is launched from
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")  # Aura uses NEO4J_USERNAME, not NEO4J_USER
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise RuntimeError("NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD must be set in environment")

_driver: AsyncDriver | None = None


async def init_neo4j() -> AsyncDriver:
    """Initialize the driver. Call once at FastAPI startup."""
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Verify connectivity early so we fail fast
        await _driver.verify_connectivity()
    return _driver


async def close_neo4j() -> None:
    """Close the driver. Call at FastAPI shutdown."""
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


def get_neo4j_driver() -> AsyncDriver:
    """FastAPI dependency injection helper."""
    if _driver is None:
        raise RuntimeError("Neo4j driver not initialized. Call init_neo4j() at startup.")
    return _driver
