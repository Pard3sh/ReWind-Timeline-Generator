"""GCNL API client for ReWind sentiment analysis."""

from typing import Dict, List, Any, Optional
import requests

from rewind.sentiment import (
    infer_emotion_label,
    extract_activities,
    generate_timeline_title,
    sentiment_label,
)


class GCNLClient:
    """Client for Google Cloud Natural Language API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sentiment_url = f"https://language.googleapis.com/v1/documents:analyzeSentiment?key={api_key}"
        self.entity_url = f"https://language.googleapis.com/v1/documents:analyzeEntitySentiment?key={api_key}"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    @staticmethod
    def _dedupe_preserve_order(items: List[str]) -> List[str]:
        """Ensures that the timeline order, manifesting as nodes with timestamp, maintain their order for later UI reconstruction."""
        seen = set()
        result = []
        for item in items:
            cleaned = (item or "").strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                result.append(cleaned)
        return result

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a single text entry for sentiment and entities."""
        text = (text or "").strip()

        if not text:
            return {
                "sentiment_score": 0.0,
                "sentiment_magnitude": 0.0,
                "sentiment_label": sentiment_label(0.0),
                "emotion_label": "Reflective",
                "extracted_locations": [],
                "extracted_events": [],
                "entities": [],
            }

        payload = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": text,
                "language": "en",
            },
            "encodingType": "UTF8",
        }

        try:
            sentiment_res = self.session.post(
                self.sentiment_url,
                json=payload,
                timeout=(5, 20),
            )
            sentiment_res.raise_for_status()

            entity_res = self.session.post(
                self.entity_url,
                json=payload,
                timeout=(5, 20),
            )
            entity_res.raise_for_status()

        except requests.RequestException as e:
            raise RuntimeError(f"GCNL request failed: {e}") from e

        sentiment_data = sentiment_res.json()
        entity_data = entity_res.json()

        sentiment_score = sentiment_data.get("documentSentiment", {}).get("score", 0.0)
        sentiment_magnitude = sentiment_data.get("documentSentiment", {}).get(
            "magnitude", 0.0
        )

        entities: List[Dict[str, Any]] = []
        extracted_locations: List[str] = []
        extracted_events: List[str] = []

        for entity in entity_data.get("entities", []):
            entity_name = (entity.get("name") or "").strip()
            entity_type = entity.get("type", "")
            entity_sentiment = entity.get("sentiment", {})

            entity_record = {
                "name": entity_name,
                "type": entity_type,
                "salience": float(entity.get("salience", 0.0) or 0.0),
                "sentiment_score": float(entity_sentiment.get("score", 0.0) or 0.0),
                "sentiment_magnitude": float(
                    entity_sentiment.get("magnitude", 0.0) or 0.0
                ),
            }
            entities.append(entity_record)

            if entity_type == "LOCATION" and entity_name:
                extracted_locations.append(entity_name)

            if entity_type == "EVENT" and entity_name:
                extracted_events.append(entity_name)

        extracted_locations = self._dedupe_preserve_order(extracted_locations)
        extracted_events = self._dedupe_preserve_order(extracted_events)

        emotion_label = infer_emotion_label(
            text,
            float(sentiment_score or 0.0),
            float(sentiment_magnitude or 0.0),
        )

        return {
            "sentiment_score": float(sentiment_score or 0.0),
            "sentiment_magnitude": float(sentiment_magnitude or 0.0),
            "sentiment_label": sentiment_label(float(sentiment_score or 0.0)),
            "emotion_label": emotion_label,
            "extracted_locations": extracted_locations,
            "extracted_events": extracted_events,
            "entities": entities,
        }

    def analyze_entry(
        self,
        entry: Dict[str, Any],
        saved_location: str = "",
        folder_name: str = "",
    ) -> Dict[str, Any]:
        """Analyze one Room/Firestore journal entry. Each entry generates a sentiment node and a detail node."""
        body = (entry.get("body", "") or "").strip()
        title = (entry.get("title", "") or "").strip()

        analysis = self.analyze_text(body)
        timestamp = entry.get("timestamp")

        # only call activity extraction when GCNL found no events
        activities: List[str] = []
        if not analysis["extracted_events"]:
            activities = extract_activities(body)
            activities = self._dedupe_preserve_order(activities)

        generated_title = generate_timeline_title(
            entry_title=title or "Untitled Entry",
            emotion_label=analysis["emotion_label"],
            events=analysis["extracted_events"],
            locations=analysis["extracted_locations"],
            timestamp=timestamp,
            sentiment_magnitude=analysis["sentiment_magnitude"],
            activities=activities,
        )

        if hasattr(timestamp, "isoformat"):
            timestamp = timestamp.isoformat()
        elif timestamp is None:
            timestamp = ""

        return {
            "entry_id": entry.get("id", ""),
            "entry_title": title,
            "generated_title": generated_title,
            "user_id": entry.get("userId", ""),
            "folder_id": entry.get("folderId"),
            "folder_name": folder_name,
            "timestamp": timestamp,
            "saved_location": saved_location or "",
            "latitude": entry.get("latitude"),
            "longitude": entry.get("longitude"),
            "body": body,
            **analysis,
        }

    def analyze_entries(
        self,
        entries: List[Dict[str, Any]],
        saved_locations: Optional[Dict[str, str]] = None,
        folder_name: str = "",
    ) -> List[Dict[str, Any]]:
        """Analyze a list of Room/Firestore journal entries."""
        results: List[Dict[str, Any]] = []
        saved_locations = saved_locations or {}

        for entry in entries:
            entry_id = entry.get("id", "")
            analyzed = self.analyze_entry(
                entry=entry,
                saved_location=saved_locations.get(entry_id, ""),
                folder_name=folder_name,
            )
            results.append(analyzed)

        return results
