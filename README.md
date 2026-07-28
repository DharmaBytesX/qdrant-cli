# qdrant-cli

CLI tool to interact with a [Qdrant](https://qdrant.tech) vector database.
Designed for both **human operators** and **AI agents** — JSON output mode and
structured timing make it easy to integrate into agentic workflows.

## Features

- **Manage collections** — list, create, delete
- **Ingest documents** — add **docx / pdf / xlsx** files via
  [MarkItDown](https://github.com/microsoft/markitdown) (Microsoft), automatically
  chunked by paragraph to preserve technical context
- **Semantic search** — query collections using vector similarity
- **Local embeddings** — `sentence-transformers/all-MiniLM-L6-v2` (384-dim, cosine),
  runs entirely on your machine
- **Remote embeddings** — use any OpenAI-compatible endpoint (e.g.
  [OpenRouter](https://openrouter.ai)) via `--embedding-model openrouter:<model>`
- **Output formats** — `pretty` (default), `json`, `table`
- **Timing stats** — per-step benchmarking with `--stats`
- **Agent-friendly** — `--output json` produces structured, machine-parseable output
  with optional timing breakdown; all operations are self-contained CLI commands
- **Test reports** — [Allure 3](https://allurereport.org) integration for rich HTML
  test reports with live monitoring

## Requirements

- Python >= 3.10
- Qdrant server running (e.g. [AppImage](https://github.com/qdrant/qdrant/releases))
- Node.js >= 18 (for Allure 3 reports, optional)

## Install

```bash
python -m venv .venv
.venv/bin/pip install -e ".[test]"   # includes test dependencies (pytest, allure-pytest)

# Optional: install Allure 3 CLI for test reports
npm install -g allure
```

## Usage

```
Usage: qdrant-cli [OPTIONS] COMMAND [ARGS]...

Options:
  -o, --output [pretty|json|table]    Output format
  -s, --stats                         Show timing statistics
  -e, --embedding-model TEXT          Embedding model spec:
                                      'local' (default),
                                      'local:model_name',
                                      or 'openrouter:model_name'
                                      Can also be set via EMBEDDING_MODEL env var.
  --help                              Show this message and exit.

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

# Search with JSON output + timing (agent-friendly)
qdrant-cli --output json --stats search "network security" my_docs

# Table output
qdrant-cli --output table collections

# Use a remote embedding model via OpenRouter
export OPENROUTER_API_KEY="sk-or-v1-..."
qdrant-cli --embedding-model openrouter:nvidia/nemotron-3-embed-1b:free search "query" my_docs
```

## Test Reports (Allure 3)

[Allure 3](https://allurereport.org) is a TypeScript-based test report framework
that produces rich, interactive HTML reports.

### Quick start

```bash
# Run tests with Allure results, then generate and open the report
task test-full
task allure-report
task allure-open
```

Or in one step:

```bash
task allure-run
```

### Commands

```bash
# Run all tests and capture Allure results
task test-full            # adds --alluredir=allure-results automatically

# Generate the HTML report from captured results
task allure-report        # runs `npx allure generate allure-results -o allure-report`

# Open the report in your browser
task allure-open

# Watch mode — live-update the report as tests run
task allure-watch         # runs `npx allure watch allure-results`
```

The report is configured via `allurerc.mjs` (Awesome plugin, single-file HTML).

## Development

```bash
# Lint
task lint

# Test
task test-full                    # all tests with Allure results
task test-client                  # client tests only
task test-embeddings              # embedding tests only
task test-file                    # file processor tests only

# Full check (lint + test)
task check-all
```

## Project structure

```
src/qdrant_cli/
├── client.py          # Qdrant wrapper (collections, upsert, query)
├── embeddings.py      # Local (sentence-transformers) + remote (OpenAI-compatible) embedders
├── file_processor.py  # MarkItDown + paragraph-aware chunking
├── main.py            # Click CLI
└── output.py          # Output formatting (pretty/json/table) + timing

allurerc.mjs           # Allure 3 configuration
Taskfile.yaml          # Lint, test, and Allure report tasks
```

## License

MIT
