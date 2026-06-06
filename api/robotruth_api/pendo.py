"""Server-side Pendo Track Event helper."""
from __future__ import annotations

import logging
import time
import httpx

logger = logging.getLogger(__name__)

PENDO_TRACK_URL = "https://data.pendo.io/data/track"
PENDO_INTEGRATION_KEY = "c9df071f-327a-4815-9a67-7814fe4987dc"


def track(event: str, properties: dict | None = None, visitor_id: str = "system", account_id: str = "system") -> None:
    """Fire a Pendo server-side track event. Never raises; failures are logged."""
    payload = {
        "type": "track",
        "event": event,
        "visitorId": visitor_id,
        "accountId": account_id,
        "timestamp": int(time.time() * 1000),
        "properties": properties or {},
    }
    try:
        with httpx.Client(timeout=5) as client:
            client.post(
                PENDO_TRACK_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-pendo-integration-key": PENDO_INTEGRATION_KEY,
                },
            )
    except Exception:
        logger.debug("Pendo track event '%s' failed to send", event, exc_info=True)
