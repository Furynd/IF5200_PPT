"""
Neo4j Schema Initialization for Referly
Run once to create constraints, indexes, and seed data.

Usage:
    python scripts/init_neo4j.py

Requires:
    pip install neo4j python-dotenv
"""

import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv
from pathlib import Path


env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")



def init_schema(tx):
    """Create constraints and indexes matching the data model."""

    # ── Node uniqueness constraints ──
    # These also create indexes automatically
    tx.run("CREATE CONSTRAINT user_id IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE")
    tx.run("CREATE CONSTRAINT skill_id IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE")

    # ── Additional indexes for common lookups ──
    tx.run("CREATE INDEX user_phone IF NOT EXISTS FOR (u:User) ON (u.phone_number)")
    tx.run("CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)")
    tx.run("CREATE INDEX skill_name IF NOT EXISTS FOR (s:Skill) ON (s.name)")

    print("Schema constraints and indexes created.")


def seed_companies(tx, companies: list[dict]):
    """Batch insert companies using UNWIND for efficiency."""
    tx.run("""
        UNWIND $companies AS c
        MERGE (comp:Company {id: c.id})
        SET comp.name = c.name,
            comp.industry = c.industry
    """, companies=companies)
    print(f"Seeded {len(companies)} companies.")


def seed_skills(tx, skills: list[dict]):
    """Batch insert common skills."""
    tx.run("""
        UNWIND $skills AS s
        MERGE (sk:Skill {id: s.id})
        SET sk.name = s.name,
            sk.latent_vector = [],
            sk.bias = 0.0
    """, skills=skills)
    print(f"Seeded {len(skills)} skills.")


def verify_schema(tx):
    """Verify the schema was created correctly."""
    result = tx.run("SHOW CONSTRAINTS").data()
    print(f"\nConstraints ({len(result)}):")
    for r in result:
        print(f"  - {r.get('name', 'unnamed')}: {r.get('type', '?')}")

    result = tx.run("SHOW INDEXES").data()
    print(f"\nIndexes ({len(result)}):")
    for r in result:
        print(f"  - {r.get('name', 'unnamed')}: {r.get('type', '?')} on {r.get('labelsOrTypes', '?')}")

    result = tx.run("MATCH (c:Company) RETURN count(c) AS count").single()
    print(f"\nCompanies in DB: {result['count']}")

    result = tx.run("MATCH (s:Skill) RETURN count(s) AS count").single()
    print(f"Skills in DB: {result['count']}")


# ── Seed Data ──────────────────────────────────────────────

COMPANIES = [
    # Tech & Startups
    {"id": "comp-001", "name": "PT GoTo Gojek Tokopedia Tbk", "industry": "Technology"},
    {"id": "comp-002", "name": "Grab Indonesia", "industry": "Technology"},
    {"id": "comp-003", "name": "Shopee Indonesia", "industry": "E-Commerce"},
    {"id": "comp-004", "name": "Traveloka", "industry": "Technology"},
    {"id": "comp-005", "name": "Bukalapak", "industry": "E-Commerce"},
    {"id": "comp-006", "name": "Blibli", "industry": "E-Commerce"},
    {"id": "comp-007", "name": "Tiket.com", "industry": "Technology"},
    {"id": "comp-008", "name": "Xendit", "industry": "Fintech"},
    {"id": "comp-009", "name": "OVO", "industry": "Fintech"},
    {"id": "comp-010", "name": "Dana Indonesia", "industry": "Fintech"},
    {"id": "comp-011", "name": "Ajaib", "industry": "Fintech"},
    {"id": "comp-012", "name": "Stockbit", "industry": "Fintech"},
    {"id": "comp-013", "name": "Bibit", "industry": "Fintech"},
    {"id": "comp-014", "name": "Kredivo", "industry": "Fintech"},
    {"id": "comp-015", "name": "Ruangguru", "industry": "EdTech"},
    {"id": "comp-016", "name": "Zenius", "industry": "EdTech"},
    {"id": "comp-017", "name": "Vidio", "industry": "Media"},
    {"id": "comp-018", "name": "Kompas Gramedia", "industry": "Media"},
    {"id": "comp-019", "name": "Kopi Kenangan", "industry": "F&B"},
    {"id": "comp-020", "name": "Fore Coffee", "industry": "F&B"},

    # Banking
    {"id": "comp-021", "name": "Bank Central Asia (BCA)", "industry": "Banking"},
    {"id": "comp-022", "name": "Bank Mandiri", "industry": "Banking"},
    {"id": "comp-023", "name": "Bank Rakyat Indonesia (BRI)", "industry": "Banking"},
    {"id": "comp-024", "name": "Bank Negara Indonesia (BNI)", "industry": "Banking"},
    {"id": "comp-025", "name": "Bank Jago", "industry": "Banking"},
    {"id": "comp-026", "name": "Bank CIMB Niaga", "industry": "Banking"},
    {"id": "comp-027", "name": "Bank Danamon", "industry": "Banking"},
    {"id": "comp-028", "name": "Bank Permata", "industry": "Banking"},
    {"id": "comp-029", "name": "Bank BTPN", "industry": "Banking"},
    {"id": "comp-030", "name": "Bank Mega", "industry": "Banking"},

    # Telco
    {"id": "comp-031", "name": "Telkom Indonesia", "industry": "Telecommunications"},
    {"id": "comp-032", "name": "Telkomsel", "industry": "Telecommunications"},
    {"id": "comp-033", "name": "Indosat Ooredoo Hutchison", "industry": "Telecommunications"},
    {"id": "comp-034", "name": "XL Axiata", "industry": "Telecommunications"},

    # Consulting & Professional Services
    {"id": "comp-035", "name": "McKinsey & Company Indonesia", "industry": "Consulting"},
    {"id": "comp-036", "name": "Boston Consulting Group (BCG) Indonesia", "industry": "Consulting"},
    {"id": "comp-037", "name": "Bain & Company Indonesia", "industry": "Consulting"},
    {"id": "comp-038", "name": "Deloitte Indonesia", "industry": "Professional Services"},
    {"id": "comp-039", "name": "PwC Indonesia", "industry": "Professional Services"},
    {"id": "comp-040", "name": "EY Indonesia", "industry": "Professional Services"},
    {"id": "comp-041", "name": "KPMG Indonesia", "industry": "Professional Services"},

    # FMCG & Consumer
    {"id": "comp-042", "name": "Unilever Indonesia", "industry": "FMCG"},
    {"id": "comp-043", "name": "Procter & Gamble Indonesia", "industry": "FMCG"},
    {"id": "comp-044", "name": "Nestle Indonesia", "industry": "FMCG"},
    {"id": "comp-045", "name": "Indofood", "industry": "FMCG"},
    {"id": "comp-046", "name": "Wings Group", "industry": "FMCG"},
    {"id": "comp-047", "name": "Mayora Indah", "industry": "FMCG"},
    {"id": "comp-048", "name": "Danone Indonesia", "industry": "FMCG"},

    # Multinational Tech
    {"id": "comp-049", "name": "Google Indonesia", "industry": "Technology"},
    {"id": "comp-050", "name": "Microsoft Indonesia", "industry": "Technology"},
    {"id": "comp-051", "name": "Meta Indonesia", "industry": "Technology"},
    {"id": "comp-052", "name": "Amazon Web Services Indonesia", "industry": "Technology"},
    {"id": "comp-053", "name": "Samsung R&D Indonesia", "industry": "Technology"},
    {"id": "comp-054", "name": "Apple Indonesia", "industry": "Technology"},
    {"id": "comp-055", "name": "IBM Indonesia", "industry": "Technology"},
    {"id": "comp-056", "name": "Accenture Indonesia", "industry": "Technology"},

    # Automotive & Manufacturing
    {"id": "comp-057", "name": "Astra International", "industry": "Conglomerate"},
    {"id": "comp-058", "name": "Toyota Motor Manufacturing Indonesia", "industry": "Automotive"},
    {"id": "comp-059", "name": "Honda Prospect Motor", "industry": "Automotive"},
    {"id": "comp-060", "name": "Hyundai Motor Manufacturing Indonesia", "industry": "Automotive"},

    # Energy & Mining
    {"id": "comp-061", "name": "Pertamina", "industry": "Energy"},
    {"id": "comp-062", "name": "PLN (Perusahaan Listrik Negara)", "industry": "Energy"},
    {"id": "comp-063", "name": "Freeport Indonesia", "industry": "Mining"},
    {"id": "comp-064", "name": "Vale Indonesia", "industry": "Mining"},
    {"id": "comp-065", "name": "Adaro Energy", "industry": "Mining"},

    # State-Owned (BUMN)
    {"id": "comp-066", "name": "Garuda Indonesia", "industry": "Aviation"},
    {"id": "comp-067", "name": "Angkasa Pura", "industry": "Aviation"},
    {"id": "comp-068", "name": "Pelindo", "industry": "Logistics"},
    {"id": "comp-069", "name": "Pos Indonesia", "industry": "Logistics"},
    {"id": "comp-070", "name": "Biofarma", "industry": "Pharmaceutical"},

    # Healthcare
    {"id": "comp-071", "name": "Halodoc", "industry": "HealthTech"},
    {"id": "comp-072", "name": "Alodokter", "industry": "HealthTech"},
    {"id": "comp-073", "name": "Siloam Hospitals", "industry": "Healthcare"},
    {"id": "comp-074", "name": "Kalbe Farma", "industry": "Pharmaceutical"},
    {"id": "comp-075", "name": "Kimia Farma", "industry": "Pharmaceutical"},

    # Property & Construction
    {"id": "comp-076", "name": "Sinar Mas Land", "industry": "Property"},
    {"id": "comp-077", "name": "Ciputra Group", "industry": "Property"},
    {"id": "comp-078", "name": "Agung Podomoro Land", "industry": "Property"},
    {"id": "comp-079", "name": "Waskita Karya", "industry": "Construction"},
    {"id": "comp-080", "name": "Wijaya Karya (WIKA)", "industry": "Construction"},

    # Insurance
    {"id": "comp-081", "name": "Prudential Indonesia", "industry": "Insurance"},
    {"id": "comp-082", "name": "AIA Indonesia", "industry": "Insurance"},
    {"id": "comp-083", "name": "Allianz Indonesia", "industry": "Insurance"},
    {"id": "comp-084", "name": "Asuransi Jasindo", "industry": "Insurance"},

    # E-commerce & Logistics
    {"id": "comp-085", "name": "Lazada Indonesia", "industry": "E-Commerce"},
    {"id": "comp-086", "name": "JD.ID", "industry": "E-Commerce"},
    {"id": "comp-087", "name": "J&T Express", "industry": "Logistics"},
    {"id": "comp-088", "name": "SiCepat Ekspres", "industry": "Logistics"},
    {"id": "comp-089", "name": "AnterAja", "industry": "Logistics"},
    {"id": "comp-090", "name": "Ninja Express Indonesia", "industry": "Logistics"},

    # Media & Entertainment
    {"id": "comp-091", "name": "Emtek Group", "industry": "Media"},
    {"id": "comp-092", "name": "MNC Group", "industry": "Media"},
    {"id": "comp-093", "name": "Trans Media", "industry": "Media"},
    {"id": "comp-094", "name": "CT Corp", "industry": "Conglomerate"},

    # Agritech & Others
    {"id": "comp-095", "name": "eFishery", "industry": "AgriTech"},
    {"id": "comp-096", "name": "TaniHub", "industry": "AgriTech"},
    {"id": "comp-097", "name": "Amartha", "industry": "Fintech"},
    {"id": "comp-098", "name": "Kitabisa.com", "industry": "Social Enterprise"},
    {"id": "comp-099", "name": "Mekari", "industry": "SaaS"},
    {"id": "comp-100", "name": "Kata.ai", "industry": "AI"},
]

SKILLS = [
    {"id": "skill-001", "name": "Python"},
    {"id": "skill-002", "name": "JavaScript"},
    {"id": "skill-003", "name": "TypeScript"},
    {"id": "skill-004", "name": "Java"},
    {"id": "skill-005", "name": "Go"},
    {"id": "skill-006", "name": "SQL"},
    {"id": "skill-007", "name": "React"},
    {"id": "skill-008", "name": "Node.js"},
    {"id": "skill-009", "name": "Machine Learning"},
    {"id": "skill-010", "name": "Data Analysis"},
    {"id": "skill-011", "name": "Project Management"},
    {"id": "skill-012", "name": "UI/UX Design"},
    {"id": "skill-013", "name": "Digital Marketing"},
    {"id": "skill-014", "name": "Financial Analysis"},
    {"id": "skill-015", "name": "Business Development"},
    {"id": "skill-016", "name": "Communication"},
    {"id": "skill-017", "name": "Cloud Computing (AWS/GCP)"},
    {"id": "skill-018", "name": "DevOps"},
    {"id": "skill-019", "name": "Cybersecurity"},
    {"id": "skill-020", "name": "Product Management"},
]


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    with driver.session() as session:
        print("=== Initializing Referly Neo4j Schema ===\n")

        # Create schema
        session.execute_write(init_schema)

        # Seed data
        session.execute_write(seed_companies, COMPANIES)
        session.execute_write(seed_skills, SKILLS)

        # Verify
        session.execute_read(verify_schema)

    driver.close()
    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
