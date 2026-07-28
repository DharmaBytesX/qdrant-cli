import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field

import click


@dataclass
class Timing:
    steps: dict[str, float] = field(default_factory=dict)

    def add(self, label: str, seconds: float) -> None:
        self.steps[label] = round(seconds, 4)

    def total(self) -> float:
        return round(sum(self.steps.values()), 4)

    def to_dict(self) -> dict:
        return {**self.steps, "total": self.total()}


@contextmanager
def timer(label: str, timing: Timing):
    start = time.perf_counter()
    yield
    timing.add(label, time.perf_counter() - start)


class Output:
    def __init__(self, fmt: str = "pretty", timing: Timing | None = None):
        self.fmt = fmt
        self.timing = timing

    def _stats_block(self) -> str:
        if not self.timing or not self.timing.steps:
            return ""
        parts = [f"  {k}: {v}s" for k, v in self.timing.steps.items()]
        parts.append(f"  total: {self.timing.total()}s")
        return "\n".join(parts)

    def _msg(self, data: dict) -> str:
        msg = data.get("message", "")
        stats = self._stats_block()
        if stats:
            return f"{msg}\n{stats}"
        return msg

    def collections(self, names: list[str]) -> None:
        if self.fmt == "json":
            out = {"collections": names}
            if self.timing:
                out["stats"] = self.timing.to_dict()
            click.echo(json.dumps(out, indent=2, ensure_ascii=False))
        elif self.fmt == "table":
            if not names:
                click.echo("No collections found.")
                return
            click.echo("Collections")
            click.echo("-----------")
            for n in names:
                click.echo(n)
            stats = self._stats_block()
            if stats:
                click.echo(stats)
        else:
            if not names:
                click.echo("No collections found.")
            else:
                for n in names:
                    click.echo(n)

    def status(self, data: dict) -> None:
        if self.fmt == "json":
            out = dict(data)
            if self.timing:
                out["stats"] = self.timing.to_dict()
            click.echo(json.dumps(out, indent=2, ensure_ascii=False))
        elif self.fmt == "table":
            click.echo(data.get("message", ""))
            stats = self._stats_block()
            if stats:
                click.echo(stats)
        else:
            click.echo(data.get("message", ""))

    def search_results(self, results: list[dict], query: str) -> None:
        if self.fmt == "json":
            out = {"query": query, "results": results}
            if self.timing:
                out["stats"] = self.timing.to_dict()
            click.echo(json.dumps(out, indent=2, ensure_ascii=False, default=str))
        elif self.fmt == "table":
            if not results:
                click.echo("No results found.")
                return
            click.echo(f"{'Score':<8} {'Text':<60} {'Source':<30}")
            click.echo(f"{'-----':<8} {'----':<60} {'------':<30}")
            for r in results:
                score = f"{r['score']:.4f}"
                text = (r["payload"] or {}).get("text", "")[:58]
                source = (r["payload"] or {}).get("source", "")[:28]
                click.echo(f"{score:<8} {text:<60} {source:<30}")
            stats = self._stats_block()
            if stats:
                click.echo(stats)
        else:
            if not results:
                click.echo("No results found.")
            else:
                for r in results:
                    score = r["score"]
                    payload = r["payload"] or {}
                    text = payload.get("text", "")[:200]
                    click.echo(f"  [{score:.4f}] {text}")

    def ingestion(self, data: dict) -> None:
        if self.fmt == "json":
            out = dict(data)
            if self.timing:
                out["stats"] = self.timing.to_dict()
            click.echo(json.dumps(out, indent=2, ensure_ascii=False))
        elif self.fmt == "table":
            click.echo(data.get("message", ""))
            for k, v in data.items():
                if k not in ("message",):
                    click.echo(f"  {k}: {v}")
            stats = self._stats_block()
            if stats:
                click.echo(stats)
        else:
            click.echo(data.get("message", ""))

    def error(self, message: str) -> None:
        data = {"error": message}
        if self.fmt == "json":
            out = dict(data)
            if self.timing:
                out["stats"] = self.timing.to_dict()
            click.echo(json.dumps(out, indent=2, ensure_ascii=False))
        else:
            click.echo(f"Error: {message}")
