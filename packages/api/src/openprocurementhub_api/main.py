"""FastAPI application factory for OpenProcurementHub."""
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from openprocurementhub_connector_belgium import BelgiumFederalConnector
from openprocurementhub_core.config import Settings, load_settings
from openprocurementhub_core.models import Page, Tender
from openprocurementhub_core.observability import configure_logging
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest


def get_settings() -> Settings: return load_settings()
def create_app() -> FastAPI:
    settings = get_settings(); configure_logging(settings.log_level)
    app = FastAPI(title="OpenProcurementHub", version="0.1.0-alpha.0", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc")
    tenders: list[Tender] = []
    connector = BelgiumFederalConnector()
    @app.get("/api/v1/health")
    async def health() -> dict[str, str]: return {"status":"ok"}
    @app.get("/api/v1/ready")
    async def ready() -> dict[str, str]: return {"status":"ready"}
    @app.get("/api/v1/metrics")
    async def metrics() -> Response: return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
    @app.get("/api/v1/tenders", response_model=Page[Tender])
    async def list_tenders(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)) -> Page[Tender]: return Page(items=tenders[offset:offset+limit], total=len(tenders), limit=limit, offset=offset)
    @app.get("/api/v1/tenders/{external_id}", response_model=Tender)
    async def get_tender(external_id: str) -> Tender:
        for tender in tenders:
            if tender.external_id == external_id: return tender
        raise HTTPException(status_code=404, detail="Tender not found")
    @app.get("/api/v1/search", response_model=Page[Tender])
    async def search(q: str, limit: int = 50, offset: int = 0) -> Page[Tender]:
        matches=[t for t in tenders if q.lower() in t.title.lower() or (t.description and q.lower() in t.description.lower())]
        return Page(items=matches[offset:offset+limit], total=len(matches), limit=limit, offset=offset)
    @app.get("/api/v1/connectors")
    async def connectors() -> list[dict[str, object]]: return [connector.metadata() | {"capabilities": connector.capabilities().model_dump()}]
    @app.post("/api/v1/sync")
    async def sync(cursor: str | None = None) -> dict[str, object]: return (await connector.sync(cursor)).model_dump()
    for name in ["buyers","contracts","awards","suppliers","documents","stats"]:
        app.add_api_route(f"/api/v1/{name}", lambda: {"items": []}, methods=["GET"])
    return app
app=create_app()
def run() -> None:
    uvicorn.run("openprocurementhub_api.main:app", host="0.0.0.0", port=8000, reload=False)
