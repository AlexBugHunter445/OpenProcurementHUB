"""Logging and metrics helpers."""
import logging

import structlog
from prometheus_client import Counter, Histogram

SYNC_TOTAL = Counter("oph_connector_sync_total", "Connector sync attempts", ["connector", "status"])
REQUEST_LATENCY = Histogram("oph_api_request_seconds", "API request latency", ["path", "method"])
def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(level=level)
    structlog.configure(processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()], wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)))
