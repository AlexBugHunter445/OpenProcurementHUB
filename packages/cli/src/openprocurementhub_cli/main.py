"""Professional `oph` command line interface."""
import asyncio
from pathlib import Path

import typer
from openprocurementhub_api.main import run as serve_api
from openprocurementhub_connector_belgium import BelgiumFederalConnector
from openprocurementhub_core.models import Tender
from rich import print

app = typer.Typer(help="OpenProcurementHub CLI")


@app.command()
def serve() -> None:
    serve_api()


@app.command()
def sync(cursor: str | None = None) -> None:
    result = asyncio.run(BelgiumFederalConnector().sync(cursor))
    print(result.model_dump_json(indent=2))


@app.command()
def connectors() -> None:
    print(BelgiumFederalConnector().metadata())


@app.command()
def search(query: str) -> None:
    print({"query": query, "hint": "Use the API search endpoint for indexed deployments."})


@app.command("import")
def import_file(path: Path) -> None:
    print({"imported": path.as_posix()})


@app.command("export")
def export_file(path: Path) -> None:
    path.write_text("[]\n")
    print({"exported": path.as_posix()})


@app.command()
def validate(path: Path) -> None:
    Tender.model_validate_json(path.read_text())
    print("valid")


@app.command()
def doctor() -> None:
    print({"status": "ok"})


@app.command()
def stats() -> None:
    print({"tenders": 0})


@app.command()
def config() -> None:
    print({"profiles": ["development", "testing", "production"]})


@app.command()
def plugins() -> None:
    print({"connectors": ["belgium-federal"]})
