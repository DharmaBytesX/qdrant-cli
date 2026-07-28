from qdrant_cli.embeddings import embed, embed_batch


def test_embed_returns_list_of_floats():
    result = embed("hello world")
    assert isinstance(result, list)
    assert all(isinstance(v, float) for v in result)
    assert len(result) > 0


def test_embed_normalized():
    result = embed("test")
    magnitude = sum(v * v for v in result) ** 0.5
    assert abs(magnitude - 1.0) < 1e-4


def test_embed_batch():
    texts = ["hello", "world", "foo"]
    results = embed_batch(texts)
    assert len(results) == 3
    assert all(len(r) > 0 for r in results)


def test_embed_batch_empty():
    result = embed_batch([])
    assert result == []
