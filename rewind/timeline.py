"""Timeline management for ReWind sentiment analysis."""

from typing import List, Optional
from rewind.models import TimelineNode, FolderSummary
from rewind.sentiment import sentiment_label, sentiment_bucket, empty_sentiment_counts


class BaseFolderTimeline:
    """Base container for folder timelines."""

    def __init__(self, folder_name: str = ""):
        self.folder_name = folder_name
        self.nodes: List[TimelineNode] = []
        self.summary: Optional[FolderSummary] = None

    def add_node(self, node: TimelineNode) -> None:
        """Insert a node and avoid duplicate IDs."""
        if (
            self.folder_name
            and node.folder_name
            and node.folder_name != self.folder_name
        ):
            raise ValueError(
                f"Node folder '{node.folder_name}' does not match timeline folder '{self.folder_name}'"
            )

        if any(existing.entry_id == node.entry_id for existing in self.nodes):
            return

        self.nodes.append(node)
        self.nodes.sort(key=lambda n: n.dt())
        self._refresh_summary()

    def add_nodes_from_analyzed_entries(self, entries: List[dict]) -> None:
        """Build nodes from analyzed entry dicts and add them to this timeline."""
        for entry in entries:
            node = TimelineNode.from_analyzed_entry(entry)
            self.add_node(node)

    def _refresh_summary(self) -> None:
        """Recompute the folder summary from current timeline nodes."""
        if len(self.nodes) < 3:
            self.summary = None
            return

        scores = [n.sentiment_score for n in self.nodes]
        avg_sentiment = sum(scores) / len(scores)

        half = len(scores) // 2
        first_half = scores[:half] if half > 0 else scores
        second_half = scores[half:] if half > 0 else scores

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        if second_avg > first_avg + 0.2:
            trend = "Improving"
        elif second_avg < first_avg - 0.2:
            trend = "Declining"
        else:
            trend = "Stable"

        location_counts = {}
        event_counts = {}
        bucket_counts = empty_sentiment_counts()

        for node in self.nodes:
            for loc in node.extracted_locations:
                location_counts[loc] = location_counts.get(loc, 0) + 1
            for evt in node.extracted_events:
                event_counts[evt] = event_counts.get(evt, 0) + 1

            bucket = sentiment_bucket(node.sentiment_score)
            bucket_counts[bucket] += 1

        top_locations = sorted(location_counts, key=location_counts.get, reverse=True)[
            :3
        ]
        top_events = sorted(event_counts, key=event_counts.get, reverse=True)[:5]

        start_ts = self.nodes[0].timestamp
        end_ts = self.nodes[-1].timestamp
        source_ids = [n.entry_id for n in self.nodes]

        mood_desc = self._summary_mood_text(avg_sentiment)
        summary_text = f"This folder shows a {mood_desc} overall mood."
        if trend == "Improving":
            summary_text += " Sentiment improved over time."
        elif trend == "Declining":
            summary_text += " Sentiment became more negative over time."
        if top_events:
            summary_text += f" Key moments included {', '.join(top_events[:3])}."
        if top_locations:
            summary_text += (
                f" The most referenced locations were {', '.join(top_locations[:2])}."
            )

        self.summary = FolderSummary(
            folder_name=self.folder_name,
            start_timestamp=start_ts,
            end_timestamp=end_ts,
            entry_count=len(self.nodes),
            source_entry_ids=source_ids,
            average_sentiment=round(avg_sentiment, 2),
            sentiment_trend=trend,
            top_locations=top_locations,
            top_events=top_events,
            summary_text=summary_text,
            very_positive_count=bucket_counts["very_positive"],
            positive_count=bucket_counts["positive"],
            neutral_count=bucket_counts["neutral"],
            negative_count=bucket_counts["negative"],
            very_negative_count=bucket_counts["very_negative"],
        )

    def _summary_mood_text(self, avg_sentiment: float) -> str:
        """Map average sentiment to a short mood description."""
        if avg_sentiment >= 0.5:
            return "positive and hopeful"
        if avg_sentiment >= 0.0:
            return "mixed but generally positive"
        if avg_sentiment >= -0.3:
            return "slightly stressed"
        return "difficult and stressful"

    def _format_node_string(self, node: TimelineNode) -> str:
        raise NotImplementedError

    def to_string(self) -> str:
        lines = [f"Folder Timeline: {self.folder_name or 'Unknown'}", "-" * 60]

        if self.summary is not None:
            lines.append(str(self.summary))
        else:
            lines.append("Summary")
            lines.append(f"Folder: {self.folder_name or 'Unknown'}")
            lines.append("Summary not available yet (minimum 3 entries required).")

        lines.append("-" * 60)
        lines.append("Nodes")

        if not self.nodes:
            lines.append("No nodes available.")
        else:
            for node in self.nodes:
                lines.append(self._format_node_string(node))
                lines.append("-" * 60)

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_string()


class SentimentFolderTimeline(BaseFolderTimeline):
    """Timeline view focused on a compact sentiment summary."""

    def _format_node_string(self, node: TimelineNode) -> str:
        from rewind.sentiment import sentiment_emoji

        dt = node.dt()
        return (
            f"[{dt.strftime('%B %d, %Y at %I:%M %p')}]\n"
            f"Title: {node.generated_title}\n"
            f"Mood: {sentiment_emoji(node.sentiment_score)} {node.emotion_label} ({node.sentiment_score:+.2f})\n"
            f"Entry ID: {node.entry_id}"
        )


class DetailedFolderTimeline(BaseFolderTimeline):
    """Timeline view that exposes more node detail for review."""

    def _format_node_string(self, node: TimelineNode) -> str:
        dt = node.dt()
        lines = [
            f"[{dt.strftime('%B %d, %Y at %I:%M %p')}]",
            f"Generated Title: {node.generated_title}",
            f"Original Entry Title: {node.entry_title}",
            f"Saved Location: {node.saved_location}",
            f"Emotion: {node.emotion_label}",
            f"Sentiment: {sentiment_label(node.sentiment_score)} ({node.sentiment_score:+.2f})",
            f"Entry ID: {node.entry_id}",
        ]

        if node.extracted_events:
            lines.append(f"Events: {', '.join(node.extracted_events)}")
        if node.extracted_locations:
            lines.append(f"Mentioned Locations: {', '.join(node.extracted_locations)}")

        return "\n".join(lines)
