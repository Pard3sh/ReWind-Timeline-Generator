"""Sentiment analysis utilities for ReWind."""

from datetime import datetime, timezone
from transformers import pipeline
from typing import Optional, Dict, List
from openai import OpenAI
import logging
import json

from rewind.config import OPENAI_API_KEY, OPENAI_ACTIVITY_MODEL

logger = logging.getLogger(__name__)

_emotion_classifier: Optional[object] = None
_openai_client: Optional[OpenAI] = None


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


def get_openai_client() -> Optional[OpenAI]:
    """Load the OpenAI client lazily if configured."""
    global _openai_client
    if not OPENAI_API_KEY:
        return None
    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client


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


def extract_activities(text: str) -> List[str]:
    """Extract 1-3 concise human activities from journal text using structured LLM output."""
    text = (text or "").strip()
    if not text:
        return []

    client = get_openai_client()
    if client is None:
        return []

    schema = {
        "name": "activity_extraction",
        "schema": {
            "type": "object",
            "properties": {
                "activities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 3,
                }
            },
            "required": ["activities"],
            "additionalProperties": False,
        },
        "strict": True,
    }

    prompt = (
        "Extract up to 3 concrete human activities from this journal entry. "
        "Return short noun-phrase style activities only. "
        "Good examples: 'internship meeting', 'walking back from campus', "
        "'planning a trip', 'dinner with friends', 'studying for class'. "
        "Do not return emotions, vague themes, locations alone,full sentences or anything at all except the requested phrase style activities."
    )

    try:
        response = client.responses.create(
            model=OPENAI_ACTIVITY_MODEL,
            input=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": text},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema["name"],
                    "schema": schema["schema"],
                    "strict": True,
                }
            },
        )

        raw_text = response.output_text
        parsed = json.loads(raw_text)
        activities = parsed.get("activities", [])
        cleaned = []
        seen = set()

        for activity in activities:
            value = (activity or "").strip()
            lowered = value.lower()
            if value and lowered not in seen:
                seen.add(lowered)
                cleaned.append(value)

        return cleaned[:3]

    except Exception as e:
        logger.warning(
            f"Activity extraction failed, continuing without activities: {e}"
        )
        return []


def _time_of_day_label(timestamp) -> str:
    """Return a soft day-part label from a timestamp, or empty string if unavailable."""
    try:
        hour = parse_timestamp(timestamp).hour
    except Exception:
        return ""

    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def _title_case_phrase(value: str) -> str:
    """Normalize a phrase for title display without overcomplicating capitalization."""
    return (value or "").strip().title()


def generate_timeline_title(
    entry_title: str,
    emotion_label: str,
    events: list,
    locations: list,
    timestamp=None,
    sentiment_magnitude: float = 0.0,
    activities: Optional[List[str]] = None,
) -> str:
    """
    Build a generated timeline title using activities, event, emotion, location,
    and time-of-day cues.
    """
    primary_activity = (activities[0] if activities else "").strip()
    primary_event = (events[0] if events else "").strip()
    primary_location = (locations[0] if locations else "").strip()
    day_part = _time_of_day_label(timestamp)

    activity_text = _title_case_phrase(primary_activity)
    event_text = _title_case_phrase(primary_event)
    location_text = primary_location.strip()
    emotion_text = (emotion_label or "").strip().title()

    strong_emotion = sentiment_magnitude >= 1.2

    # Strong emotion + location: "Joy in Boston (evening)"
    if strong_emotion and location_text:
        if day_part:
            return f"{emotion_text} in {location_text} ({day_part})"
        return f"{emotion_text} in {location_text}"

    # Activity + location (+ optional day-part)
    if activity_text and location_text:
        if day_part:
            return f"{activity_text} in {location_text} ({day_part})"
        return f"{activity_text} in {location_text}"

    # Activity + day-part
    if activity_text and day_part:
        return f"{activity_text} ({day_part})"

    # Activity only
    if activity_text:
        return activity_text

    # Event + location (+ optional day-part)
    if event_text and location_text:
        if day_part:
            return f"{event_text} in {location_text} ({day_part})"
        return f"{event_text} in {location_text}"

    # Event + day-part
    if event_text and day_part:
        return f"{event_text} ({day_part})"

    # Event only
    if event_text:
        return event_text

    # Location + emotion + day-part
    if location_text and day_part:
        return f"{emotion_text} that {day_part} in {location_text}"

    # Location + emotion
    if location_text:
        return f"{emotion_text} in {location_text}"

    # Fall back to original entry title
    return entry_title
