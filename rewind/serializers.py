"""Serialization helpers for ReWind timeline node documents."""

import json
from typing import Dict, Any, List

from rewind.sentiment import parse_timestamp, sentiment_label


def _json_string(value: Any) -> str:
    """Serialize a value to a compact JSON string."""
    if value is None:
        value = []
    return json.dumps(value, ensure_ascii=False)


def _timestamp_millis(timestamp_value: Any) -> int:
    """Convert a timestamp-like value into Unix epoch milliseconds."""
    dt = parse_timestamp(timestamp_value)
    return int(dt.timestamp() * 1000)


def _safe_list(value: Any) -> List[Any]:
    """Normalize a list-like field."""
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def build_sentiment_node(
    analyzed_entry: Dict[str, Any],
    folder_id: str,
    order_index: int = 0,
) -> Dict[str, Any]:
    """Build a Room/Firestore SentimentNode document from an analyzed entry."""
    entry_id = analyzed_entry.get("entry_id", "")

    extracted_locations = _safe_list(analyzed_entry.get("extracted_locations"))
    extracted_events = _safe_list(analyzed_entry.get("extracted_events"))

    return {
        "id": f"sentiment_{entry_id}",
        "folderId": folder_id,
        "entryId": entry_id,
        "entryTitle": analyzed_entry.get("entry_title", ""),
        "generatedTitle": analyzed_entry.get("generated_title", ""),
        "timestamp": _timestamp_millis(analyzed_entry.get("timestamp")),
        "savedLocation": analyzed_entry.get("saved_location", ""),
        "sentimentScore": float(analyzed_entry.get("sentiment_score") or 0.0),
        "sentimentMagnitude": float(analyzed_entry.get("sentiment_magnitude") or 0.0),
        "emotionLabel": analyzed_entry.get("emotion_label", ""),
        "extractedLocations": _json_string(extracted_locations),
        "extractedEvents": _json_string(extracted_events),
        "orderIndex": int(order_index),
    }


def build_detailed_node(
    analyzed_entry: Dict[str, Any],
    folder_id: str,
) -> Dict[str, Any]:
    """Build a Room/Firestore DetailedNode document from an analyzed entry."""
    entry_id = analyzed_entry.get("entry_id", "")

    extracted_locations = _safe_list(analyzed_entry.get("extracted_locations"))
    extracted_events = _safe_list(analyzed_entry.get("extracted_events"))
    entity_records = _safe_list(analyzed_entry.get("entities"))

    score = float(analyzed_entry.get("sentiment_score") or 0.0)

    return {
        "id": f"detailed_{entry_id}",
        "folderId": folder_id,
        "entryId": entry_id,
        "entryTitle": analyzed_entry.get("entry_title", ""),
        "generatedTitle": analyzed_entry.get("generated_title", ""),
        "timestamp": _timestamp_millis(analyzed_entry.get("timestamp")),
        "savedLocation": analyzed_entry.get("saved_location", ""),
        "emotionLabel": analyzed_entry.get("emotion_label", ""),
        "sentimentLabel": analyzed_entry.get("sentiment_label", sentiment_label(score)),
        "sentimentScore": score,
        "sentimentMagnitude": float(analyzed_entry.get("sentiment_magnitude") or 0.0),
        "extractedLocations": _json_string(extracted_locations),
        "extractedEvents": _json_string(extracted_events),
        "entityRecords": _json_string(entity_records),
    }
