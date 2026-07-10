from openprocurementhub_core.models import Metadata, Tender


def test_tender_serializes() -> None:
    tender = Tender(title="Road works", metadata=Metadata(source="test", source_id="1"))
    assert Tender.model_validate_json(tender.model_dump_json()).title == "Road works"
