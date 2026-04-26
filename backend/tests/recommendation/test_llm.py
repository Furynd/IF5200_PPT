import os

from dotenv import load_dotenv

from backend.app.recommendation.llm import init_gemini_embed_pipeline

def prepare_llm_pipeline():
    load_dotenv()

    API_KEY = os.getenv("GEMINI_API_KEY", "???")
    MODEL_NAME = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")

    return init_gemini_embed_pipeline(api_key=API_KEY, model_name=MODEL_NAME)

def test_embedding():
    pipeline = prepare_llm_pipeline()
    result = pipeline("UI/UX Design")
    print(result)
    assert result is not None
