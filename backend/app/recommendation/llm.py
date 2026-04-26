from google import genai

def init_gemini_embed_pipeline(api_key: str, model_name: str):
    client = genai.Client(api_key=api_key)

    def f(text: str) -> list[float] | None:
        response = client.models.embed_content(
            model=model_name, 
            contents=text
        )
        embeddings = response.embeddings
        if embeddings is None or embeddings[0].values is None:
            return None
        else:
            return embeddings[0].values

    return f
