"""GCNL API client for ReWind sentiment analysis."""

import os
import json
import requests
from typing import Dict, List, Any
from rewind.sentiment import infer_emotion_label, generate_timeline_title


class GCNLClient:
    """Client for Google Cloud Natural Language API."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.sentiment_url = f"https://language.googleapis.com/v1/documents:analyzeSentiment?key={api_key}"
        self.entity_url = f"https://language.googleapis.com/v1/documents:analyzeEntitySentiment?key={api_key}"
        self.headers = {"Content-Type": "application/json"}

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a single text entry for sentiment and entities."""
        payload = {
            "document": {
                "type": "PLAIN_TEXT",
                "content": text,
                "language": "en",
            },
            "encodingType": "UTF8",
        }

        sentiment_res = requests.post(
            self.sentiment_url, headers=self.headers, json=payload, timeout=20
        )
        entity_res = requests.post(
            self.entity_url, headers=self.headers, json=payload, timeout=20
        )

        if sentiment_res.status_code != 200:
            raise RuntimeError(
                f"Sentiment API error: {sentiment_res.status_code} - {sentiment_res.text}"
            )

        if entity_res.status_code != 200:
            raise RuntimeError(
                f"Entity API error: {entity_res.status_code} - {entity_res.text}"
            )

        sentiment_data = sentiment_res.json()
        entity_data = entity_res.json()

        sentiment_score = sentiment_data.get("documentSentiment", {}).get("score")
        sentiment_magnitude = sentiment_data.get("documentSentiment", {}).get(
            "magnitude"
        )

        entities = []
        extracted_locations = []
        extracted_events = []

        for entity in entity_data.get("entities", []):
            entity_name = entity.get("name")
            entity_type = entity.get("type")
            salience = entity.get("salience")
            entity_sentiment = entity.get("sentiment", {})

            entity_record = {
                "name": entity_name,
                "type": entity_type,
                "salience": entity.get("salience"),
                "sentiment_score": entity_sentiment.get("score"),
                "sentiment_magnitude": entity_sentiment.get("magnitude"),
            }
            entities.append(entity_record)

            if entity_type == "LOCATION":
                extracted_locations.append(entity_name)
            if entity_type == "EVENT":
                extracted_events.append(entity_name)

        emotion_label = infer_emotion_label(
            text,
            sentiment_score if sentiment_score is not None else 0.0,
            sentiment_magnitude if sentiment_magnitude is not None else 0.0,
        )

        return {
            "sentiment_score": sentiment_score,
            "sentiment_magnitude": sentiment_magnitude,
            "emotion_label": emotion_label,
            "extracted_locations": extracted_locations,
            "extracted_events": extracted_events,
            "entities": entities,
        }

    def analyze_entries(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a list of journal entries."""
        results = []
        for entry in entries:
            analysis = self.analyze_text(entry["text"])

            # Build a more readable title for this timeline node.
            generated_title = generate_timeline_title(
                entry["title"],
                analysis["emotion_label"],
                analysis["extracted_events"],
                analysis["extracted_locations"],
            )

            result = {
                "entry_id": entry["entry_id"],
                "entry_title": entry["title"],
                "generated_title": generated_title,
                "folder_name": entry["folder_name"],
                "timestamp": entry["timestamp"],
                "saved_location": entry["saved_location"],
                "text": entry["text"],
                **analysis,
            }
            results.append(result)

        return results
