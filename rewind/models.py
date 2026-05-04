"""Data models for ReWind sentiment analysis.
Fields are made to exactly match Cloud database fields and the Room DB structure strictly.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class TimelineNode:
    """A single item in a folder timeline."""

    entry_id: str  # we have the timeline nodes store the entry ids specifically to allow for users being able to click on nodes and being redirected to the entry detail page
    entry_title: str = ""
    generated_title: str = ""
    folder_name: str = ""
    timestamp: str = ""
    saved_location: str = ""
    sentiment_score: float = (
        0.0  # 1 is max positive, -1 max negativity based of the ML model
    )
    sentiment_magnitude: float = 0.0
    emotion_label: str = ""
    extracted_locations: List[str] = field(default_factory=list)
    extracted_events: List[str] = field(default_factory=list)

    def dt(self) -> datetime:
        """Return the timestamp as a datetime object for sorting and display."""
        from rewind.sentiment import parse_timestamp

        return parse_timestamp(self.timestamp)

    def __str__(self) -> str:
        return (
            f"TimelineNode(entry_id={self.entry_id}, generated_title={self.generated_title}, "
            f"timestamp={self.timestamp}, sentiment={self.sentiment_score:+.2f}, "
            f"emotion={self.emotion_label})"
        )

    @classmethod
    def from_analyzed_entry(cls, entry: dict) -> "TimelineNode":
        """Create a TimelineNode from an analyzed entry dictionary."""
        return cls(
            entry_id=entry.get("entry_id", ""),
            entry_title=entry.get("entry_title", ""),
            generated_title=entry.get("generated_title", ""),
            folder_name=entry.get("folder_name", ""),
            timestamp=entry.get("timestamp", ""),
            saved_location=entry.get("saved_location", ""),
            sentiment_score=float(entry.get("sentiment_score") or 0.0),
            sentiment_magnitude=float(entry.get("sentiment_magnitude") or 0.0),
            emotion_label=entry.get("emotion_label", ""),
            extracted_locations=entry.get("extracted_locations", []),
            extracted_events=entry.get("extracted_events", []),
        )


@dataclass
class FolderSummary:
    """A compact summary of a folder timeline."""

    folder_name: str = ""
    start_timestamp: str = ""
    end_timestamp: str = ""
    entry_count: int = 0
    source_entry_ids: List[str] = field(default_factory=list)
    average_sentiment: float = 0.0
    sentiment_trend: str = ""
    top_locations: List[str] = field(default_factory=list)
    top_events: List[str] = field(default_factory=list)
    summary_text: str = ""

    very_positive_count: int = 0
    positive_count: int = 0
    neutral_count: int = 0
    negative_count: int = 0
    very_negative_count: int = 0

    def __str__(self) -> str:
        from rewind.sentiment import parse_timestamp, sentiment_label

        period_text = "Unknown"
        if self.start_timestamp and self.end_timestamp:
            start_dt = parse_timestamp(self.start_timestamp)
            end_dt = parse_timestamp(self.end_timestamp)
            period_text = (
                f"{start_dt.strftime('%B %d, %Y')} to {end_dt.strftime('%B %d, %Y')}"
            )

        lines = [
            "Summary",
            f"Folder: {self.folder_name}",
            f"Period: {period_text}",
            f"Entries: {self.entry_count}",
            f"Average Sentiment: {self.average_sentiment:+.2f} ({sentiment_label(self.average_sentiment)})",
            f"Trend: {self.sentiment_trend}",
            (
                "Distribution: "
                f"Very Positive={self.very_positive_count}, "
                f"Positive={self.positive_count}, "
                f"Neutral={self.neutral_count}, "
                f"Negative={self.negative_count}, "
                f"Very Negative={self.very_negative_count}"
            ),
        ]

        if self.top_locations:
            lines.append(f"Top Locations: {', '.join(self.top_locations)}")
        if self.top_events:
            lines.append(f"Top Events: {', '.join(self.top_events)}")

        lines.append(f"Source Entry IDs: {', '.join(self.source_entry_ids)}")
        lines.append(f"Reflection: {self.summary_text}")
        return "\n".join(lines)
