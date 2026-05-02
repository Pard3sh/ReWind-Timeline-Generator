"""Data models for ReWind sentiment analysis."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class TimelineNode:
    """A single item in the sentiment timeline.

    Stores raw entry metadata, generated timeline text, and the final sentiment
    and emotion details shown in the folder view.
    """

    entry_id: str
    entry_title: str
    generated_title: str
    folder_name: str
    timestamp: str
    saved_location: str
    sentiment_score: float
    sentiment_magnitude: float
    emotion_label: str
    extracted_locations: List[str] = field(default_factory=list)
    extracted_events: List[str] = field(default_factory=list)

    def dt(self) -> datetime:
        """Return the timestamp as a datetime object for sorting and display."""
        from rewind.sentiment import parse_timestamp  # Avoid circular import

        return parse_timestamp(self.timestamp)

    def __str__(self) -> str:
        return (
            f"TimelineNode(entry_id={self.entry_id}, generated_title={self.generated_title}, "
            f"timestamp={self.timestamp}, sentiment={self.sentiment_score:+.2f}, "
            f"emotion={self.emotion_label})"
        )

    @classmethod
    def from_analyzed_entry(cls, entry: dict) -> "TimelineNode":
        """Create a TimelineNode from a GCNL-analyzed entry dict."""
        return cls(
            entry_id=entry["entry_id"],
            entry_title=entry["entry_title"],
            generated_title=entry["generated_title"],
            folder_name=entry["folder_name"],
            timestamp=entry["timestamp"],
            saved_location=entry["saved_location"],
            sentiment_score=entry["sentiment_score"],
            sentiment_magnitude=entry["sentiment_magnitude"],
            emotion_label=entry["emotion_label"],
            extracted_locations=entry.get("extracted_locations", []),
            extracted_events=entry.get("extracted_events", []),
        )


@dataclass
class FolderSummary:
    """A compact summary of a folder timeline.

    Includes aggregated sentiment, trend information, and the top events/locations
    for a group of related entries.
    """

    folder_name: str
    start_timestamp: str
    end_timestamp: str
    entry_count: int
    source_entry_ids: List[str]
    average_sentiment: float
    sentiment_trend: str
    top_locations: List[str]
    top_events: List[str]
    summary_text: str

    def __str__(self) -> str:
        from rewind.sentiment import parse_timestamp

        start_dt = parse_timestamp(self.start_timestamp)
        end_dt = parse_timestamp(self.end_timestamp)

        lines = [
            "Summary",
            f"Folder: {self.folder_name}",
            f"Period: {start_dt.strftime('%B %d, %Y')} to {end_dt.strftime('%B %d, %Y')}",
            f"Entries: {self.entry_count}",
            f"Average Sentiment: {self.average_sentiment:+.2f} ({self.sentiment_label(self.average_sentiment)})",
            f"Trend: {self.sentiment_trend}",
        ]
        if self.top_locations:
            lines.append(f"Top Locations: {', '.join(self.top_locations)}")
        if self.top_events:
            lines.append(f"Top Events: {', '.join(self.top_events)}")
        lines.append(f"Source Entry IDs: {', '.join(self.source_entry_ids)}")
        lines.append(f"Reflection: {self.summary_text}")
        return "\n".join(lines)

    @staticmethod
    def sentiment_label(score: float) -> str:
        """Helper to get sentiment label."""
        from rewind.sentiment import sentiment_label

        return sentiment_label(score)
