import os

from dotenv import load_dotenv
import neo4j

from backend.app.recommendation.llm import init_gemini_embed_pipeline
from backend.app.repositories import SkillRepository

def prepare_llm_pipeline():
    load_dotenv()

    API_KEY = os.getenv("GEMINI_API_KEY", "???")
    MODEL_NAME = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")

    return init_gemini_embed_pipeline(api_key=API_KEY, model_name=MODEL_NAME)

def prepare_neo4j_driver_and_database_name():
    load_dotenv()

    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://xxxxx.databases.neo4j.io")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    return driver, NEO4J_DATABASE

if __name__ == "__main__":
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    pipeline = prepare_llm_pipeline()
    def embed_fn(x: str):
        y = pipeline(x)
        if y is None:
            raise ValueError(f"Cannot embed {x}")
        
        return y
    
    repo = SkillRepository(driver, database=NEO4J_DATABASE)
    EMBED_ID = 120
    repo.create_new_embeddings_if_not_exists(EMBED_ID)
    result = repo.update_all_uninitialized_embeddings(EMBED_ID, embed_fn)
    print(result)
