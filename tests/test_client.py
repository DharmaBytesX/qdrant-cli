import pytest
from qdrant_client.http.models import PointStruct

from qdrant_cli.client import (
    create_collection,
    delete_collection,
    list_collections,
    search,
    upsert_points,
)
from qdrant_cli.embeddings import embed


@pytest.fixture(autouse=True)
def cleanup():
    yield
    for name in list_collections():
        if name.startswith("_test_"):
            delete_collection(name)


def test_create_and_list_collection():
    name = "_test_create_list"
    assert create_collection(name) is True
    assert name in list_collections()


def test_create_duplicate():
    name = "_test_dup"
    create_collection(name)
    assert create_collection(name) is False


def test_delete_collection():
    name = "_test_delete"
    create_collection(name)
    assert delete_collection(name) is True
    assert name not in list_collections()


def test_delete_nonexistent():
    assert delete_collection("_test_nonexistent") is False


def test_upsert_and_search():
    name = "_test_upsert_search"
    create_collection(name)

    texts = ["apple banana fruit", "dog cat animal", "car bus vehicle"]
    points = [
        PointStruct(id=i, vector=embed(t), payload={"text": t})
        for i, t in enumerate(texts)
    ]
    upsert_points(name, points)

    query_vec = embed("fruit apple")
    results = search(name, query_vec, limit=3)
    assert len(results) > 0
    assert any("fruit" in r["payload"].get("text", "") for r in results)
