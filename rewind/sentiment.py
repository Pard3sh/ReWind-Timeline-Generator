"""Sentiment analysis utilities for ReWind."""

from datetime import datetime
from transformers import pipeline
from typing import Optional

# Initialize emotion classifier (loads on first use)
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


def infer_emotion_label(text: str, score: float = 0.0, magnitude: float = 0.0) -> str:
    """Infer emotion label using transformer-based emotion classifier.

    Uses the j-hartmann/emotion-english-distilroberta-base model for accurate
    emotion classification. Falls back gracefully to keyword heuristics if model fails.

    Args:
        text: The journal entry text to classify
        score: GCNL sentiment score (for fallback)
        magnitude: GCNL sentiment magnitude (for fallback)

    Returns:
        The top emotion label predicted by the model
    """
    try:
        classifier = get_emotion_classifier()
        # Truncate text to 512 tokens (model max length)
        text_truncated = text[:500]
        predictions = classifier(text_truncated)
        # Get the top emotion (highest confidence)
        if predictions and predictions[0]:
            top_emotion = predictions[0][0]
            emotion = top_emotion["label"].capitalize()
            return emotion
    except Exception as e:
        # Fallback to simple heuristics if model fails
        pass

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
