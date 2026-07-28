# qdrant-cli

CLI tool to interact with a [Qdrant](https://qdrant.tech) vector database. Supports searching, managing collections, and ingesting documents (docx, pdf, xlsx) with paragraph-aware chunking and local embeddings.

## Features

- **Manage collections** — list, create, delete
- **Ingest documents** — add docx/pdf/xlsx files, automatically chunked by paragraph
- **Semantic search** — query collections using vector similarity
- **Local embeddings** — uses `sentence-transformers/all-MiniLM-L6-v2` (384-dim, cosine distance), runs entirely on your machine
- **Output formats** — `pretty` (default), `json`, `table`
- **Timing stats** — per-step benchmarking with `--stats`

## Requirements

- Python >= 3.10
- Qdrant server running (e.g. [AppImage](https://github.com/qdrant/qdrant/releases))

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```
Usage: qdrant-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -o, --output [pretty|json|table]  Output format
  -s, --stats                       Show timing statistics
  --help                            Show this message and exit.

Commands:
  add-collection  Create a new collection.
  add-file        Add a file (docx/pdf/xlsx) to a collection.
  collections     List all collections.
  del-collection  Delete a collection.
  search          Search a collection.
```

### Examples

```bash
# List collections
qdrant-cli collections

# Create a collection
qdrant-cli add-collection my_docs

# Ingest a document
qdrant-cli add-file report.pdf my_docs

# Search with JSON output + timing
qdrant-cli --output json --stats search "network security" my_docs

# Table output
qdrant-cli --output table collections
```

## Development

```bash
# Lint
task lint

# Test
task test-full
task test-client    # client tests only
task test-file      # file processor tests only
```

## Project structure

```
src/qdrant_cli/
├── client.py          # Qdrant wrapper (collections, upsert, query)
├── embeddings.py      # sentence-transformers model
├── file_processor.py  # markitdown + paragraph-aware chunking
├── main.py            # click CLI
└── output.py          # output formatting + timing
```

## License

MIT
