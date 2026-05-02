"""Sentiment analysis utilities for ReWind."""

from datetime import datetime


def parse_timestamp(ts: str) -> datetime:
    """Convert an ISO-8601 timestamp string into a datetime object."""
    return datetime.fromisoformat(ts)


def sentiment_label(score: float) -> str:
    """Return a human-readable sentiment label for a GCNL score."""
    if score >= 0.6:
        return "Very Positive"
    if score >= 0.2:
        return "Positive"
    if score > -0.2:
        return "Neutral"
    if score >= -0.6:
        return "Negative"
    return "Very Negative"


def sentiment_emoji(score: float) -> str:
    """Return an emoji that matches the sentiment score."""
    if score >= 0.6:
        return "😊"
    if score >= 0.2:
        return "🙂"
    if score > -0.2:
        return "😐"
    if score >= -0.6:
        return "☹️"
    return "😞"


def infer_emotion_label(text: str, score: float, magnitude: float) -> str:
    """Infer a more descriptive emotion label from text and sentiment values."""
    text_lower = text.lower()

    if any(
        word in text_lower for word in ["anxious", "overwhelmed", "nervous", "worried"]
    ):
        return "Anxious"

    if any(
        word in text_lower
        for word in [
            "frustrated",
            "burnout",
            "exhausting",
            "stuck",
            "deadline",
            "deadlines",
        ]
    ):
        return "Stressed"

    if any(word in text_lower for word in ["calm", "peaceful", "relaxed"]):
        return "Calm"

    if any(
        word in text_lower
        for word in ["excited", "thrilled", "looking forward", "trip"]
    ):
        return "Excited"

    if any(word in text_lower for word in ["hopeful", "optimistic", "proud"]):
        return "Hopeful"

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
