# -*- coding: utf-8 -*-
# 데이터 전치리/정제 

from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Optional

SILVER_SCHEMA_VERSION = "1.0"

def clean_event_payload(payload: Any) -> Optional[str]:
    if payload is None:
        return None
    if isinstance(payload, bytes):
        try:
            payload = payload.decode("utf-8")
        except UnicodeDecodeError:
            return None
    if not isinstance(payload, str):
        payload = str(payload)
    try:
        event = json.loads(payload)
    except (json.JSONDecodeError, TypeError, ValueError):
        return None
    if not isinstance(event, dict):
        return None
    cleaned = {key: value for key, value in event.items() if value is not None}
    cleaned["_silver"] = {
        "layer": "silver",
        "processor": "apache-flink",
        "schema_version": SILVER_SCHEMA_VERSION,
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(
        cleaned,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )