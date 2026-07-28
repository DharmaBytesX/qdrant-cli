from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams

_client: QdrantClient | None = None


def get_client(host: str = "localhost", port: int = 6333) -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=host, port=port)
    return _client


def list_collections() -> list[str]:
    client = get_client()
    collections = client.get_collections()
    return [c.name for c in collections.collections]


def create_collection(name: str, size: int = 384) -> bool:
    client = get_client()
    collections = [c.name for c in client.get_collections().collections]
    if name in collections:
        return False
    client.create_collection(
        collection_name=name,
        vectors_config=VectorParams(size=size, distance=Distance.COSINE),
    )
    return True


def delete_collection(name: str) -> bool:
    client = get_client()
    collections = [c.name for c in client.get_collections().collections]
    if name not in collections:
        return False
    client.delete_collection(name)
    return True


def upsert_points(
    collection_name: str, points: list[PointStruct], batch_size: int = 64
) -> None:
    client = get_client()
    for i in range(0, len(points), batch_size):
        client.upsert(collection_name=collection_name, points=points[i : i + batch_size])


def search(
    collection_name: str, query_vector: list[float], limit: int = 10
) -> list[dict]:
    client = get_client()
    response = client.query_points(
        collection_name=collection_name, query=query_vector, limit=limit
    )
    return [
        {
            "id": p.id,
            "score": p.score,
            "payload": p.payload,
        }
        for p in response.points
    ]
