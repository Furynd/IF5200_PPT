import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from neo4j import GraphDatabase
import redis

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 1. POSTGRESQL SETUP (Data Transaksional)
# ==========================================
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency Injection untuk FastAPI.
    Akan membuka sesi DB di awal request dan menutupnya setelah request selesai.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==========================================
# 2. NEO4J SETUP (Graph Koneksi)
# ==========================================
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j_graph_456")

# Inisialisasi driver Neo4j (koneksi pool)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def get_neo4j_session():
    """
    Dependency Injection untuk mengeksekusi Cypher query di Neo4j.
    """
    session = neo4j_driver.session()
    try:
        yield session
    finally:
        session.close()


# ==========================================
# 3. REDIS SETUP (Rate Limiting & Ghost Nodes)
# ==========================================
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# decode_responses=True agar hasil dari Redis berupa string, bukan byte
redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_redis():
    """
    Dependency Injection untuk Redis.
    """
    yield redis_client