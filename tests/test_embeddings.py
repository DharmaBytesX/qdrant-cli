from unittest.mock import patch

import pytest

from qdrant_cli.embeddings import (
    LocalEmbedder,
    RemoteEmbedder,
    embed,
    embed_batch,
    get_embedder,
    reset_embedder,
)


@pytest.fixture(autouse=True)
def clean_embedder():
    reset_embedder()
    yield
    reset_embedder()


def test_local_embed_returns_list_of_floats():
    result = embed("hello world")
    assert isinstance(result, list)
    assert all(isinstance(v, float) for v in result)
    assert len(result) > 0


def test_local_embed_normalized():
    result = embed("test")
    magnitude = sum(v * v for v in result) ** 0.5
    assert abs(magnitude - 1.0) < 1e-4


def test_local_embed_batch():
    texts = ["hello", "world", "foo"]
    results = embed_batch(texts)
    assert len(results) == 3
    assert all(len(r) > 0 for r in results)


def test_local_embed_batch_empty():
    result = embed_batch([])
    assert result == []


def test_local_embedder_class():
    e = LocalEmbedder()
    v = e.embed("test")
    assert len(v) == 384


def _mock_response(status=200, json_data=None):
    m = type("MockResp", (), {
        "status_code": status,
        "raise_for_status": lambda self: None,
        "json": lambda self: json_data or {},
    })()
    return m


def test_remote_embedder_class():
    json_data = {
        "data": [
            {"index": 0, "embedding": [0.1] * 384},
            {"index": 1, "embedding": [0.2] * 384},
        ]
    }

    with patch("httpx.Client") as mock_client:
        instance = mock_client.return_value
        instance.post.return_value = _mock_response(json_data=json_data)
        e = RemoteEmbedder(
            model="test-model",
            api_key="sk-test",
            base_url="https://test.example.com/v1",
        )
        v = e.embed("hello")
        assert len(v) == 384
        assert v[0] == 0.1

        vs = e.embed_batch(["a", "b"])
        assert len(vs) == 2
        assert vs[0][0] == 0.1
        assert vs[1][0] == 0.2

        assert instance.post.call_count == 2


def test_remote_embedder_batch_empty():
    with patch("httpx.Client"):
        e = RemoteEmbedder(
            model="test", api_key="sk-test",
        )
        assert e.embed_batch([]) == []


def test_get_embedder_local_default():
    e = get_embedder("local")
    assert isinstance(e, LocalEmbedder)


def test_get_embedder_local_with_model():
    e = get_embedder("local:all-MiniLM-L6-v2")
    assert isinstance(e, LocalEmbedder)
    v = e.embed("test")
    assert len(v) == 384


def test_get_embedder_openrouter_no_key():
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY"):
        get_embedder("openrouter:some-model")


def test_get_embedder_invalid():
    with pytest.raises(ValueError, match="Unknown embedding model spec"):
        get_embedder("invalid_spec")
