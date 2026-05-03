"""Cloud job for processing ReWind sentiment analysis.

Reads entries from Firestore, analyzes them, generates sentiment and detailed
timeline nodes, and writes results back to Firestore to match the Android
Room schema.
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional

from rewind.config import GCNL_API_KEY
from rewind.api import GCNLClient
from rewind.timeline import SentimentFolderTimeline, DetailedFolderTimeline
from rewind.database import FirestoreDB
from rewind.serializers import (
    build_sentiment_node,
    build_detailed_node,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_empty_folder_summary_payload() -> Dict[str, Any]:
    """Return an empty folder summary payload."""
    return {
        "entry_count": 0,
        "average_sentiment": 0.0,
        "sentiment_trend": "Unknown",
        "top_locations": [],
        "top_events": [],
        "summary_text": "",
        "start_timestamp": "",
        "end_timestamp": "",
        "very_positive_count": 0,
        "positive_count": 0,
        "neutral_count": 0,
        "negative_count": 0,
        "very_negative_count": 0,
    }


def build_folder_summary_payload(timeline) -> Dict[str, Any]:
    """Convert a timeline summary into a Firestore-friendly payload."""
    if not timeline.summary:
        return build_empty_folder_summary_payload()

    return {
        "entry_count": timeline.summary.entry_count,
        "average_sentiment": timeline.summary.average_sentiment,
        "sentiment_trend": timeline.summary.sentiment_trend,
        "top_locations": timeline.summary.top_locations,
        "top_events": timeline.summary.top_events,
        "summary_text": timeline.summary.summary_text,
        "start_timestamp": timeline.summary.start_timestamp,
        "end_timestamp": timeline.summary.end_timestamp,
        "very_positive_count": timeline.summary.very_positive_count,
        "positive_count": timeline.summary.positive_count,
        "neutral_count": timeline.summary.neutral_count,
        "negative_count": timeline.summary.negative_count,
        "very_negative_count": timeline.summary.very_negative_count,
    }


def process_folder_entries(
    user_id: str,
    folder_id: str,
    folder_name: str,
    entries: List[Dict[str, Any]],
    db: Optional[FirestoreDB] = None,
) -> Dict[str, Any]:
    """Process entries for a single folder and generate timeline data."""
    logger.info(f"Processing {len(entries)} entries for folder {folder_id}")

    filtered_entries = [
        entry
        for entry in entries
        if entry.get("folderId") == folder_id and entry.get("folderId") is not None
    ]

    if not filtered_entries:
        logger.warning(f"No entries found for folder {folder_id}")
        return {
            "user_id": user_id,
            "folder_id": folder_id,
            "folder_name": folder_name,
            "entry_count": 0,
            "sentiment_nodes": [],
            "detailed_nodes": [],
            "folder_summary": build_empty_folder_summary_payload(),
        }

    if not GCNL_API_KEY:
        raise ValueError("GCNL_API_KEY is missing.")

    client = GCNLClient(GCNL_API_KEY)

    saved_locations = {
        entry["id"]: db.get_saved_location_for_entry(entry) if db else ""
        for entry in filtered_entries
    }

    analyzed_entries = client.analyze_entries(
        entries=filtered_entries,
        saved_locations=saved_locations,
        folder_name=folder_name,
    )

    sentiment_timeline = SentimentFolderTimeline(folder_name)
    detailed_timeline = DetailedFolderTimeline(folder_name)

    sentiment_timeline.add_nodes_from_analyzed_entries(analyzed_entries)
    detailed_timeline.add_nodes_from_analyzed_entries(analyzed_entries)

    analyzed_by_entry_id = {entry["entry_id"]: entry for entry in analyzed_entries}

    sentiment_nodes = []
    detailed_nodes = []

    for order_index, node in enumerate(sentiment_timeline.nodes):
        analyzed_entry = analyzed_by_entry_id.get(node.entry_id, {})

        sentiment_nodes.append(
            build_sentiment_node(
                analyzed_entry=analyzed_entry,
                folder_id=folder_id,
                order_index=order_index,
            )
        )

        detailed_nodes.append(
            build_detailed_node(
                analyzed_entry=analyzed_entry,
                folder_id=folder_id,
            )
        )

    result = {
        "user_id": user_id,
        "folder_id": folder_id,
        "folder_name": folder_name,
        "entry_count": len(filtered_entries),
        "sentiment_nodes": sentiment_nodes,
        "detailed_nodes": detailed_nodes,
        "folder_summary": build_folder_summary_payload(sentiment_timeline),
    }

    if db:
        logger.info("Writing results to Firestore")
        db.write_sentiment_nodes(user_id, folder_id, sentiment_nodes)
        db.write_detailed_nodes(user_id, folder_id, detailed_nodes)
        db.update_folder_summary(user_id, folder_id, result["folder_summary"])

    return result


def main():
    """Main entry point for the cloud job."""
    user_id = os.getenv("REWIND_USER_ID", "").strip()
    folder_id = os.getenv("REWIND_FOLDER_ID", "").strip()
    folder_name = os.getenv("REWIND_FOLDER_NAME", "").strip()

    if not user_id or not folder_id:
        raise ValueError(
            "REWIND_USER_ID and REWIND_FOLDER_ID environment variables are required."
        )

    db = FirestoreDB()

    if not folder_name:
        folder = db.get_folder(user_id, folder_id)
        folder_name = folder.get("name", "") if folder else ""

    entries = db.get_folder_entries(user_id, folder_id)

    if not entries:
        logger.warning(f"No entries found for folder {folder_id}")
        return

    result = process_folder_entries(
        user_id=user_id,
        folder_id=folder_id,
        folder_name=folder_name,
        entries=entries,
        db=db,
    )

    logger.info(f"Job complete. Processed {result['entry_count']} entries")
    logger.info(f"Generated {len(result['sentiment_nodes'])} sentiment nodes")
    logger.info(f"Generated {len(result['detailed_nodes'])} detailed nodes")

    print(
        json.dumps(
            {
                "user_id": result["user_id"],
                "folder_id": result["folder_id"],
                "entry_count": result["entry_count"],
                "sentiment_nodes_count": len(result["sentiment_nodes"]),
                "detailed_nodes_count": len(result["detailed_nodes"]),
                "folder_summary": result["folder_summary"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
