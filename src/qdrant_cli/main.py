import os

import click
from qdrant_client.http.models import PointStruct

from qdrant_cli.client import (
    create_collection,
    list_collections,
    upsert_points,
)
from qdrant_cli.client import (
    delete_collection as qdrant_delete_collection,
)
from qdrant_cli.client import (
    search as qdrant_search,
)
from qdrant_cli.embeddings import embed, embed_batch, get_embedder
from qdrant_cli.file_processor import process_file_chunked
from qdrant_cli.output import Output, Timing, timer


@click.group()
@click.option(
    "--output", "-o",
    type=click.Choice(["pretty", "json", "table"]),
    default="pretty",
    help="Output format",
)
@click.option(
    "--stats", "-s",
    is_flag=True,
    default=False,
    help="Show timing statistics",
)
@click.option(
    "--embedding-model", "-e",
    default=None,
    help=(
        "Embedding model spec. "
        "'local' (default), 'local:model_name', or "
        "'openrouter:model_name'. "
        "Can also be set via EMBEDDING_MODEL env var."
    ),
)
@click.pass_context
def cli(ctx: click.Context, output: str, stats: bool, embedding_model: str | None):
    ctx.ensure_object(dict)
    ctx.obj["output_fmt"] = output
    ctx.obj["show_stats"] = stats

    if embedding_model is not None:
        os.environ["EMBEDDING_MODEL"] = embedding_model
    get_embedder()


def _make_out(ctx: click.Context) -> tuple[Output, Timing | None]:
    show = ctx.obj["show_stats"]
    timing = Timing() if show else None
    return Output(ctx.obj["output_fmt"], timing), timing


def _nullcontext():
    class _NullCtx:
        def __enter__(self):
            return None
        def __exit__(self, *a):
            pass
    return _NullCtx()


@cli.command()
@click.pass_context
def collections(ctx: click.Context):
    """List all collections."""
    out, t = _make_out(ctx)
    with timer("list_collections", t) if t else _nullcontext():
        cols = list_collections()
    out.collections(cols)


@cli.command()
@click.argument("name")
@click.pass_context
def add_collection(ctx: click.Context, name: str):
    """Create a new collection."""
    out, t = _make_out(ctx)
    dim = get_embedder().dimension
    with timer("create_collection", t) if t else _nullcontext():
        created = create_collection(name, size=dim)
    out.status({
        "message": f"Collection '{name}' created (dim={dim})." if created
                   else f"Collection '{name}' already exists.",
        "collection": name,
        "status": "created" if created else "exists",
        "dimension": dim,
    })


@cli.command()
@click.argument("name")
@click.pass_context
def del_collection(ctx: click.Context, name: str):
    """Delete a collection."""
    out, t = _make_out(ctx)
    with timer("delete_collection", t) if t else _nullcontext():
        deleted = qdrant_delete_collection(name)
    out.status({
        "message": f"Collection '{name}' deleted." if deleted
                   else f"Collection '{name}' not found.",
        "collection": name,
        "status": "deleted" if deleted else "not_found",
    })


@cli.command()
@click.argument("file_path")
@click.argument("collection")
@click.pass_context
def add_file(ctx: click.Context, file_path: str, collection: str):
    """Add a file (docx/pdf/xlsx) to a collection."""
    out, t = _make_out(ctx)

    cols = list_collections()
    if collection not in cols:
        out.error(f"Collection '{collection}' does not exist. Create it first.")
        return

    with timer("process_file", t) if t else _nullcontext():
        chunks = process_file_chunked(file_path)

    if not chunks:
        out.error("No content extracted from file.")
        return

    with timer("embed", t) if t else _nullcontext():
        texts = [c[0] for c in chunks]
        vectors = embed_batch(texts)

    with timer("upsert", t) if t else _nullcontext():
        points = [
            PointStruct(
                id=hash(text) & 0x7FFFFFFFFFFFFFFF,
                vector=vector,
                payload={"text": text, "source": file_path, "chunk_idx": idx},
            )
            for (text, idx), vector in zip(chunks, vectors)
        ]
        upsert_points(collection, points)

    out.ingestion({
        "message": f"Added {len(points)} chunks to '{collection}'.",
        "collection": collection,
        "file": file_path,
        "chunks": len(points),
        "source": file_path,
    })


@cli.command()
@click.argument("query")
@click.argument("collection")
@click.option("--limit", default=10, help="Number of results")
@click.pass_context
def search(ctx: click.Context, query: str, collection: str, limit: int):
    """Search a collection."""
    out, t = _make_out(ctx)

    cols = list_collections()
    if collection not in cols:
        out.error(f"Collection '{collection}' does not exist.")
        return

    with timer("embed_query", t) if t else _nullcontext():
        query_vector = embed(query)

    with timer("qdrant_search", t) if t else _nullcontext():
        results = qdrant_search(collection, query_vector, limit=limit)

    out.search_results(results, query)
