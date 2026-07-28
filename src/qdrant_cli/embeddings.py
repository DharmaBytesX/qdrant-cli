from sentence_transformers import SentenceTransformer

_MODEL = None


def get_model() -> SentenceTransformer:
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def embed(text: str) -> list[float]:
    model = get_model()
    return model.encode(text, normalize_embeddings=True).tolist()


def embed_batch(texts: list[str]) -> list[list[float]]:
    model = get_model()
    return model.encode(texts, normalize_embeddings=True).tolist()
