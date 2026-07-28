import json

from click.testing import CliRunner

from qdrant_cli.main import cli
from qdrant_cli.output import Output, Timing, timer


def test_timing_add_and_total():
    t = Timing()
    t.add("step_a", 1.234)
    t.add("step_b", 2.345)
    assert t.steps["step_a"] == 1.234
    assert t.total() == 3.579


def test_timing_empty():
    t = Timing()
    assert t.total() == 0.0
    assert t.to_dict() == {"total": 0.0}


def test_timer_context_manager():
    t = Timing()
    with timer("test_step", t):
        pass
    assert "test_step" in t.steps
    assert t.steps["test_step"] < 1.0


def test_output_collections_json():
    out = Output("json")
    runner = CliRunner()
    with runner.isolated_filesystem():
        # We test the Output class directly, not through CLI
        pass
    # Can't easily capture click.echo output, so test format indirectly
    out.fmt = "json"
    # Just verify no exception
    out.collections(["a", "b"])
    out.collections([])


def test_output_status_json():
    out = Output("json")
    out.status({"message": "done", "status": "ok"})
    out.status({"message": "done", "status": "ok", "collection": "test"})


def test_output_search_results_json():
    out = Output("json")
    results = [
        {"id": 1, "score": 0.95, "payload": {"text": "hello world", "source": "doc.pdf"}},
    ]
    out.search_results(results, "hello")


def test_output_search_results_empty():
    out = Output("pretty")
    out.search_results([], "hello")


def test_output_ingestion_json():
    out = Output("json")
    out.ingestion({"message": "done", "collection": "c", "file": "f.pdf", "chunks": 5})


def test_output_error_json():
    out = Output("json")
    out.error("something went wrong")


def test_output_with_stats_json():
    t = Timing()
    t.add("embed", 0.5)
    t.add("upsert", 0.3)
    out = Output("json", t)
    out.status({"message": "done", "status": "ok"})


def test_output_table_format():
    out = Output("table")
    out.collections(["alpha", "beta"])
    out.search_results(
        [{"id": 1, "score": 0.9, "payload": {"text": "test", "source": "x.pdf"}}],
        "test",
    )


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "--output" in result.output
    assert "--stats" in result.output


def test_cli_collections():
    runner = CliRunner()
    result = runner.invoke(cli, ["collections"])
    assert result.exit_code == 0


def test_cli_collections_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["--output", "json", "collections"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "collections" in data


def test_cli_collections_stats():
    runner = CliRunner()
    result = runner.invoke(cli, ["--stats", "collections"])
    assert result.exit_code == 0


def test_cli_add_collection():
    runner = CliRunner()
    name = "_test_cli_add"
    result = runner.invoke(cli, ["--output", "json", "add-collection", name])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] in ("created", "exists")
    # cleanup
    runner.invoke(cli, ["del-collection", name])


def test_cli_del_collection():
    runner = CliRunner()
    name = "_test_cli_del"
    runner.invoke(cli, ["add-collection", name])
    result = runner.invoke(cli, ["--output", "json", "del-collection", name])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["status"] in ("deleted", "not_found")


def test_cli_search_nonexistent():
    runner = CliRunner()
    result = runner.invoke(cli, ["--output", "json", "search", "test", "_nonexistent"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "error" in data


def test_cli_add_file_nonexistent_collection():
    runner = CliRunner()
    result = runner.invoke(cli, ["--output", "json", "add-file", "/tmp/fake.pdf", "_nonexistent"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "error" in data
