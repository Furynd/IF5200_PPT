"""
Seed test users into Neo4j for development and recommendation testing.

Creates a realistic social graph:
  - 1 "seeker" user (Budi, user-001) — the person looking for a job
  - 9 direct connections (1-hop) of Budi, several working at the same companies
  - 6 friends-of-friends (2-hop), also at various companies
  - 5 unconnected users (control group — should never appear in results)

Each user has a latent_vector (8-dim) and bias matching Fang et al. (2013).
Vector semantics:
  dims 0–1 : Software Engineering  (Python, Java, Go, DevOps)
  dims 2–3 : Data / ML             (Machine Learning, Data Analysis, SQL)
  dims 4–5 : Frontend / Design     (React, JS/TS, UI/UX)
  dims 6–7 : Business              (PM, Finance, Biz Dev, Marketing)

Run with:
    cd backend
    python scripts/seed_users.py
"""

import os
import math
from datetime import datetime, timezone
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")


def normalize(vec: list[float]) -> list[float]:
    """L2-normalize a vector so dot products are bounded in [−1, 1]."""
    mag = math.sqrt(sum(x * x for x in vec))
    if mag == 0:
        return vec
    return [x / mag for x in vec]


# ── Users ─────────────────────────────────────────────────────────────────────
#
# latent_vector: raw values normalized below.
# is_open_to_refer: controls whether they appear in recommendation results.
#
USERS = [
    # ── Seeker ──────────────────────────────────────────────────────────────
    # Budi is the "logged-in" user in test scenarios. No WORKS_AT — he's
    # job-seeking. Strong in engineering + data.
    {
        "id": "user-001",
        "full_name": "Budi Santoso",
        "phone_number": "+6281234567001",
        "is_open_to_refer": False,
        "latent_vector": normalize([0.8, 0.6, 0.7, 0.6, 0.2, 0.1, 0.1, 0.1]),
        "bias": 0.05,
        "company_id": None,
        "job_title": None,
        "skills": [
            ("skill-001", 4),   # Python
            ("skill-009", 4),   # Machine Learning
            ("skill-010", 3),  # Data Analysis
            ("skill-007", 2),   # React
        ],
    },

    # ── 1-hop: direct connections of Budi ───────────────────────────────────
    # High Fang score vs Budi (similar engineering/data vectors)
    {
        "id": "user-002",
        "full_name": "Andi Wijaya",
        "phone_number": "+6281234567002",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.7, 0.5, 0.9, 0.8, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.08,
        "company_id": "comp-001",   # GoTo
        "job_title": "Senior Data Scientist",
        "skills": [
            ("skill-001", 4),   # Python
            ("skill-009", 4),   # Machine Learning
            ("skill-010", 4),   # Data Analysis
            ("skill-017", 3),  # Cloud
        ],
    },
    {
        "id": "user-003",
        "full_name": "Sari Dewi",
        "phone_number": "+6281234567003",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.1, 0.1, 0.9, 0.8, 0.2, 0.1]),
        "bias": 0.03,
        "company_id": "comp-001",   # GoTo
        "job_title": "Product Designer",
        "skills": [
            ("skill-007", 4),   # React
            ("skill-002", 4),   # JavaScript
            ("skill-012", 4),   # UI/UX
        ],
    },
    {
        "id": "user-004",
        "full_name": "Rizky Pratama",
        "phone_number": "+6281234567004",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.9, 0.4, 0.5, 0.4, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.06,
        "company_id": "comp-001",   # GoTo
        "job_title": "DevOps Engineer",
        "skills": [
            ("skill-001", 4),   # Python
            ("skill-018", 4),   # DevOps
            ("skill-017", 4),   # Cloud
            ("skill-006", 3),  # SQL
        ],
    },
    {
        "id": "user-005",
        "full_name": "Maya Kusuma",
        "phone_number": "+6281234567005",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.5, 0.3, 0.8, 0.9, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.07,
        "company_id": "comp-003",   # Shopee
        "job_title": "Data Analyst",
        "skills": [
            ("skill-010", 4),   # Data Analysis
            ("skill-006", 4),   # SQL
            ("skill-009", 3),  # ML
            ("skill-001", 3),  # Python
        ],
    },
    {
        "id": "user-006",
        "full_name": "Deni Firmansyah",
        "phone_number": "+6281234567006",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.2, 0.3, 0.1, 0.1, 0.9, 0.8]),
        "bias": 0.04,
        "company_id": "comp-021",   # BCA
        "job_title": "Financial Analyst",
        "skills": [
            ("skill-014", 4),   # Financial Analysis
            ("skill-006", 3),  # SQL
            ("skill-016", 4),   # Communication
        ],
    },
    {
        "id": "user-007",
        "full_name": "Ratna Sari",
        "phone_number": "+6281234567007",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.8, 0.9]),
        "bias": 0.03,
        "company_id": "comp-004",   # Traveloka
        "job_title": "Product Manager",
        "skills": [
            ("skill-020", 4),   # Product Management
            ("skill-016", 4),   # Communication
            ("skill-015", 3),  # Business Development
        ],
    },
    {
        "id": "user-008",
        "full_name": "Hendra Putra",
        "phone_number": "+6281234567008",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.4, 0.8, 0.4, 0.5, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.05,
        "company_id": "comp-001",   # GoTo
        "job_title": "Backend Engineer",
        "skills": [
            ("skill-004", 4),   # Java
            ("skill-006", 4),   # SQL
            ("skill-018", 3),  # DevOps
        ],
    },
    {
        "id": "user-009",
        "full_name": "Fitriani Ahmad",
        "phone_number": "+6281234567009",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.7, 0.4, 0.8, 0.7, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.06,
        "company_id": "comp-002",   # Grab
        "job_title": "ML Engineer",
        "skills": [
            ("skill-001", 4),   # Python
            ("skill-009", 4),   # Machine Learning
            ("skill-010", 3),  # Data Analysis
        ],
    },
    # Not open to refer — should be excluded from results
    {
        "id": "user-010",
        "full_name": "Bayu Setiawan",
        "phone_number": "+6281234567010",
        "is_open_to_refer": False,
        "latent_vector": normalize([0.6, 0.5, 0.6, 0.5, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.04,
        "company_id": "comp-001",   # GoTo
        "job_title": "Software Engineer",
        "skills": [
            ("skill-001", 3),  # Python
            ("skill-005", 3),  # Go
        ],
    },

    # ── 2-hop: friends of Budi's friends ────────────────────────────────────
    # These are connected to user-002 or user-005, not directly to Budi.
    {
        "id": "user-011",
        "full_name": "Citra Lestari",
        "phone_number": "+6281234567011",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.8, 0.5, 0.9, 0.7, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.09,
        "company_id": "comp-001",   # GoTo
        "job_title": "Staff ML Engineer",
        "skills": [
            ("skill-009", 4),   # Machine Learning
            ("skill-001", 4),   # Python
            ("skill-017", 4),   # Cloud
        ],
    },
    {
        "id": "user-012",
        "full_name": "Agus Salim",
        "phone_number": "+6281234567012",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.2, 0.2, 0.1, 0.1, 0.8, 0.9, 0.1, 0.1]),
        "bias": 0.03,
        "company_id": "comp-001",   # GoTo
        "job_title": "Frontend Engineer",
        "skills": [
            ("skill-007", 4),   # React
            ("skill-003", 4),   # TypeScript
            ("skill-002", 4),   # JavaScript
        ],
    },
    {
        "id": "user-013",
        "full_name": "Putri Wahyu",
        "phone_number": "+6281234567013",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.5, 0.3, 0.7, 0.9, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.07,
        "company_id": "comp-003",   # Shopee
        "job_title": "Senior Data Analyst",
        "skills": [
            ("skill-010", 4),   # Data Analysis
            ("skill-006", 4),   # SQL
            ("skill-001", 3),  # Python
        ],
    },
    {
        "id": "user-014",
        "full_name": "Eko Prasetyo",
        "phone_number": "+6281234567014",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.9, 0.6, 0.8, 0.7, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.10,
        "company_id": "comp-049",   # Google Indonesia
        "job_title": "Software Engineer",
        "skills": [
            ("skill-009", 4),   # Machine Learning
            ("skill-001", 4),   # Python
            ("skill-017", 4),   # Cloud
            ("skill-019", 3),  # Cybersecurity
        ],
    },
    {
        "id": "user-015",
        "full_name": "Nadia Rahmawati",
        "phone_number": "+6281234567015",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.1, 0.2, 0.3, 0.3, 0.9, 0.8]),
        "bias": 0.04,
        "company_id": "comp-004",   # Traveloka
        "job_title": "Business Analyst",
        "skills": [
            ("skill-015", 4),   # Business Development
            ("skill-020", 3),  # Product Management
            ("skill-016", 4),   # Communication
        ],
    },
    {
        "id": "user-016",
        "full_name": "Irwan Susanto",
        "phone_number": "+6281234567016",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.6, 0.4, 0.5, 0.5, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.05,
        "company_id": "comp-001",   # GoTo
        "job_title": "Platform Engineer",
        "skills": [
            ("skill-005", 4),   # Go
            ("skill-018", 4),   # DevOps
            ("skill-006", 3),  # SQL
        ],
    },

    # ── Unconnected users (control group) ───────────────────────────────────
    # No CONNECTED_TO path to Budi — must never appear in his search results.
    {
        "id": "user-017",
        "full_name": "Lina Marliana",
        "phone_number": "+6281234567017",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]),
        "bias": 0.02,
        "company_id": "comp-001",   # GoTo — same company, but not reachable
        "job_title": "HR Business Partner",
        "skills": [("skill-016", 4)],
    },
    {
        "id": "user-018",
        "full_name": "Yusuf Hakim",
        "phone_number": "+6281234567018",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.5, 0.5, 0.5, 0.5, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.03,
        "company_id": "comp-050",   # Microsoft
        "job_title": "Cloud Architect",
        "skills": [("skill-017", 4), ("skill-001", 4)],
    },
    {
        "id": "user-019",
        "full_name": "Dewi Anggraeni",
        "phone_number": "+6281234567019",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.1, 0.1, 0.9, 0.9, 0.1, 0.1]),
        "bias": 0.02,
        "company_id": "comp-015",   # Ruangguru
        "job_title": "UX Lead",
        "skills": [("skill-012", 4), ("skill-007", 4)],
    },
    {
        "id": "user-020",
        "full_name": "Fauzan Maulana",
        "phone_number": "+6281234567020",
        "is_open_to_refer": True,
        "latent_vector": normalize([0.1, 0.1, 0.9, 0.9, 0.1, 0.1, 0.1, 0.1]),
        "bias": 0.05,
        "company_id": "comp-003",   # Shopee — same as Maya but unreachable
        "job_title": "Analytics Engineer",
        "skills": [("skill-010", 4), ("skill-006", 4)],
    },
]

# ── Social graph edges ────────────────────────────────────────────────────────
#
# (from_id, to_id) — CONNECTED_TO is undirected in queries (no arrow) but
# we store it directed for provenance. We create both directions here so
# the CONNECTED_TO pattern matches regardless of traversal direction.
#
CONNECTIONS = [
    # Budi (001) ↔ 1-hop friends
    ("user-001", "user-002"),
    ("user-001", "user-003"),
    ("user-001", "user-004"),
    ("user-001", "user-005"),
    ("user-001", "user-006"),
    ("user-001", "user-007"),
    ("user-001", "user-008"),
    ("user-001", "user-009"),
    ("user-001", "user-010"),

    # 2-hop: friends-of-friends (not directly connected to Budi)
    ("user-002", "user-011"),  # Citra is Andi's colleague/friend
    ("user-002", "user-014"),  # Eko is Andi's former colleague (now at Google)
    ("user-003", "user-012"),  # Agus is Sari's colleague
    ("user-005", "user-013"),  # Putri is Maya's colleague at Shopee
    ("user-007", "user-015"),  # Nadia is Ratna's colleague at Traveloka
    ("user-004", "user-016"),  # Irwan is Rizky's colleague at GoTo

    # Some cross-connections among 1-hop friends (realistic social graph)
    ("user-002", "user-004"),
    ("user-003", "user-008"),
    ("user-005", "user-009"),
]


def seed_users(tx, users: list[dict]):
    tx.run("""
        UNWIND $users AS u
        MERGE (user:User {id: u.id})
        SET
            user.full_name       = u.full_name,
            user.phone_number    = u.phone_number,
            user.is_open_to_refer = u.is_open_to_refer,
            user.latent_vector   = u.latent_vector,
            user.bias            = u.bias,
            user.created_at      = datetime()
    """, users=[
        {
            "id": u["id"],
            "full_name": u["full_name"],
            "phone_number": u["phone_number"],
            "is_open_to_refer": u["is_open_to_refer"],
            "latent_vector": u["latent_vector"],
            "bias": u["bias"],
        }
        for u in users
    ])
    print(f"Upserted {len(users)} user nodes.")


def seed_works_at(tx, users: list[dict]):
    employees = [u for u in users if u["company_id"] is not None]
    tx.run("""
        UNWIND $employees AS e
        MATCH (u:User {id: e.user_id})
        MATCH (c:Company {id: e.company_id})
        MERGE (u)-[r:WORKS_AT]->(c)
        SET r.job_title = e.job_title,
            r.since = datetime()
    """, employees=[
        {"user_id": u["id"], "company_id": u["company_id"], "job_title": u["job_title"]}
        for u in employees
    ])
    print(f"Created WORKS_AT edges for {len(employees)} users.")


def seed_connections(tx, connections: list[tuple]):
    edges = [{"from_id": f, "to_id": t} for f, t in connections]
    tx.run("""
        UNWIND $edges AS e
        MATCH (a:User {id: e.from_id})
        MATCH (b:User {id: e.to_id})
        MERGE (a)-[:CONNECTED_TO {source: 'seed', created_at: datetime()}]->(b)
        MERGE (b)-[:CONNECTED_TO {source: 'seed', created_at: datetime()}]->(a)
    """, edges=edges)
    print(f"Created CONNECTED_TO edges for {len(connections)} pairs (both directions).")


def seed_skills(tx, users: list[dict]):
    has_skill_rows = []
    for u in users:
        for skill_id, level in u.get("skills", []):
            has_skill_rows.append({
                "user_id": u["id"],
                "skill_id": skill_id,
                "level": level,
            })
    tx.run("""
        UNWIND $rows AS row
        MATCH (u:User {id: row.user_id})
        MATCH (s:Skill {id: row.skill_id})
        MERGE (u)-[r:HAS_SKILL]->(s)
        SET r.level = row.level
    """, rows=has_skill_rows)
    print(f"Created HAS_SKILL edges ({len(has_skill_rows)} total).")


def verify(tx):
    counts = {
        "Users": "MATCH (u:User) RETURN count(u) AS n",
        "WORKS_AT": "MATCH ()-[:WORKS_AT]->() RETURN count(*) AS n",
        "CONNECTED_TO": "MATCH ()-[:CONNECTED_TO]->() RETURN count(*) AS n",
        "HAS_SKILL": "MATCH ()-[:HAS_SKILL]->() RETURN count(*) AS n",
    }
    print("\n── Graph summary ──────────────────────────────")
    for label, q in counts.items():
        n = tx.run(q).single()["n"]
        print(f"  {label:<15}: {n}")

    # Spot-check: direct connections at GoTo for Budi
    result = tx.run("""
        MATCH (me:User {id: 'user-001'})-[:CONNECTED_TO]-(c:User)-[:WORKS_AT]->(co:Company {id: 'comp-001'})
        WHERE c.is_open_to_refer = true
        RETURN c.full_name AS name, c.id AS id
    """).data()
    print(f"\n  1-hop connections of Budi at GoTo (open to refer): {len(result)}")
    for r in result:
        print(f"    → {r['name']} ({r['id']})")

    result = tx.run("""
        MATCH path = (me:User {id: 'user-001'})-[:CONNECTED_TO*1..2]-(c:User)-[:WORKS_AT]->(co:Company {id: 'comp-001'})
        WHERE c.is_open_to_refer = true AND c.id <> 'user-001'
        RETURN DISTINCT c.full_name AS name, c.id AS id, (length(path) - 1) AS hops
        ORDER BY hops
    """).data()
    print(f"\n  1-and-2-hop connections of Budi at GoTo (open to refer): {len(result)}")
    for r in result:
        print(f"    → {r['name']} ({r['hops']}-hop)")


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    print("=== Seeding test users into Referly Neo4j ===\n")

    with driver.session() as session:
        session.execute_write(seed_users, USERS)
        session.execute_write(seed_works_at, USERS)
        session.execute_write(seed_connections, CONNECTIONS)
        session.execute_write(seed_skills, USERS)
        session.execute_read(verify)

    driver.close()
    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
