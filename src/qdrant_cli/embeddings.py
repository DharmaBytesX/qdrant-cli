import os
from abc import ABC, abstractmethod


class Embedder(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...


_EMBEDDER: Embedder | None = None


def reset_embedder() -> None:
    global _EMBEDDER
    _EMBEDDER = None


def get_embedder(model_spec: str | None = None) -> Embedder:
    global _EMBEDDER
    if _EMBEDDER is not None and model_spec is None:
        return _EMBEDDER

    spec = model_spec or os.environ.get("EMBEDDING_MODEL", "local")

    if spec == "local" or spec.startswith("local:"):
        model_name = spec.split(":", 1)[1] if ":" in spec else "all-MiniLM-L6-v2"
        embedder = LocalEmbedder(model_name)
    elif spec.startswith("openrouter:"):
        model = spec.split(":", 1)[1]
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable is required "
                "for remote embeddings"
            )
        base_url = os.environ.get(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
        )
        embedder = RemoteEmbedder(
            model=model, api_key=api_key, base_url=base_url
        )
    else:
        raise ValueError(
            f"Unknown embedding model spec: {spec}. "
            "Use 'local', 'local:model_name', or 'openrouter:model_name'."
        )

    if model_spec is None:
        _EMBEDDER = embedder
    return embedder


def embed(text: str) -> list[float]:
    return get_embedder().embed(text)


def embed_batch(texts: list[str]) -> list[list[float]]:
    return get_embedder().embed_batch(texts)


class LocalEmbedder(Embedder):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)

    @property
    def dimension(self) -> int:
        return self._model.get_embedding_dimension()

    def embed(self, text: str) -> list[float]:
        return self._model.encode(
            text, normalize_embeddings=True
        ).tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return self._model.encode(
            texts, normalize_embeddings=True
        ).tolist()


class RemoteEmbedder(Embedder):
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
    ):
        import httpx
        self._model = model
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=120,
        )
        self._dim: int | None = None

    @property
    def dimension(self) -> int:
        if self._dim is None:
            self._dim = len(self.embed("probe"))
        return self._dim

    def embed(self, text: str) -> list[float]:
        resp = self._client.post(
            "/embeddings",
            json={"model": self._model, "input": text},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["embedding"]

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        resp = self._client.post(
            "/embeddings",
            json={"model": self._model, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()
        sorted_data = sorted(data["data"], key=lambda x: x["index"])
        return [d["embedding"] for d in sorted_data]
