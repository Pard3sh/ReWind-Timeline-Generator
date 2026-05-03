"""Sentiment analysis utilities for ReWind."""

from datetime import datetime, timezone
from transformers import pipeline
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


_emotion_classifier: Optional[object] = None


def get_emotion_classifier():
    """Load the emotion classification model lazily on first use."""
    global _emotion_classifier
    if _emotion_classifier is None:
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=None,
        )
    return _emotion_classifier


def parse_timestamp(ts) -> datetime:
    """Convert supported timestamp values into a timezone-aware datetime object."""
    if ts is None:
        raise ValueError("Timestamp cannot be None")

    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)

    if isinstance(ts, (int, float)):
        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)

    if hasattr(ts, "isoformat") and not isinstance(ts, str):
        return ts

    ts = str(ts).strip()
    if not ts:
        raise ValueError("Timestamp cannot be empty")

    if ts.isdigit():
        return datetime.fromtimestamp(int(ts) / 1000.0, tz=timezone.utc)

    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")

    return datetime.fromisoformat(ts)


def sentiment_bucket(score: float) -> str:
    """Return a stable sentiment bucket key for summary counts."""
    if score >= 0.6:
        return "very_positive"
    if score >= 0.2:
        return "positive"
    if score > -0.2:
        return "neutral"
    if score >= -0.6:
        return "negative"
    return "very_negative"


def empty_sentiment_counts() -> Dict[str, int]:
    """Return an initialized sentiment bucket counter."""
    return {
        "very_positive": 0,
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "very_negative": 0,
    }


def sentiment_label(score: float) -> str:
    """Return a human-readable sentiment label for a GCNL score."""
    bucket = sentiment_bucket(score)
    labels = {
        "very_positive": "Very Positive",
        "positive": "Positive",
        "neutral": "Neutral",
        "negative": "Negative",
        "very_negative": "Very Negative",
    }
    return labels[bucket]


def sentiment_emoji(score: float) -> str:
    """Return an emoji that matches the sentiment score."""
    bucket = sentiment_bucket(score)
    emojis = {
        "very_positive": "😊",
        "positive": "🙂",
        "neutral": "😐",
        "negative": "☹️",
        "very_negative": "😞",
    }
    return emojis[bucket]


def infer_emotion_label(text: str, score: float = 0.0, magnitude: float = 0.0) -> str:
    """Infer emotion label using transformer-based emotion classifier."""
    try:
        classifier = get_emotion_classifier()
        predictions = classifier(text, truncation=True, max_length=512)

        if isinstance(predictions, list) and predictions:
            first_item = predictions[0]

            if isinstance(first_item, list) and first_item:
                top_emotion = max(first_item, key=lambda x: x.get("score", 0.0))
                return top_emotion.get("label", "Neutral").capitalize()

            if isinstance(first_item, dict):
                return first_item.get("label", "Neutral").capitalize()

    except Exception as e:
        logger.warning(f"Emotion classification failed, using fallback: {e}")

    if score >= 0.7:
        return "Happy"
    if score >= 0.3:
        return "Positive"
    if score > -0.2:
        return "Reflective"
    if score >= -0.6:
        return "Down"
    return "Upset"


def generate_timeline_title(
    entry_title: str, emotion_label: str, events: list, locations: list
) -> str:
    """Build a generated timeline title using events and location when available."""
    if events and locations:
        return f"{events[0].title()} in {locations[0]}"
    if events:
        return events[0].title()
    if locations:
        return f"{emotion_label} in {locations[0]}"
    return entry_title
