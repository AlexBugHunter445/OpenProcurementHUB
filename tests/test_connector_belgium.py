import json
from datetime import UTC, datetime

import pytest
from openprocurementhub_connector_belgium import BelgiumFederalConnector
from openprocurementhub_connector_sdk import RawDocument


@pytest.mark.asyncio
async def test_belgium_normalizes_record() -> None:
    connector=BelgiumFederalConnector(endpoint="https://example.test")
    doc=RawDocument(source="belgium-federal", source_id="BE-1", fetched_at=datetime.now(UTC), content=json.dumps({"title":"School renovation","buyer":"City"}).encode())
    tender=await connector.normalize(doc)
    assert tender.title == "School renovation"
    assert tender.buyers[0].name == "City"
