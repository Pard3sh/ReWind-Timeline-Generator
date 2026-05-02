"""Cloud job for processing ReWind sentiment analysis.

This script is designed to run as a cloud job that processes
folders with new journal entries and generates sentiment timelines.
"""

import json
import logging
from typing import List, Dict, Any
from rewind.config import GCNL_API_KEY
from rewind.api import GCNLClient
from rewind.timeline import SentimentFolderTimeline, DetailedFolderTimeline

# Set up logging for cloud environment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_folder_entries(
    folder_name: str, entries: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Process entries for a single folder and return timeline data.

    Args:
        folder_name: Name of the folder being processed
        entries: List of journal entry dictionaries

    Returns:
        Dictionary containing sentiment and detailed timeline strings
    """
    logger.info(f"Processing {len(entries)} entries for folder: {folder_name}")

    # Initialize the GCNL client
    client = GCNLClient(GCNL_API_KEY)

    # Analyze all entries
    analyzed_entries = client.analyze_entries(entries)

    # Create timeline views
    sentiment_timeline = SentimentFolderTimeline(folder_name)
    detailed_timeline = DetailedFolderTimeline(folder_name)

    # Add analyzed entries
    sentiment_timeline.add_nodes_from_analyzed_entries(analyzed_entries)
    detailed_timeline.add_nodes_from_analyzed_entries(analyzed_entries)

    # Return timeline data (could be saved to database here)
    return {
        "folder_name": folder_name,
        "entry_count": len(entries),
        "sentiment_timeline": str(sentiment_timeline),
        "detailed_timeline": str(detailed_timeline),
        "analyzed_entries": analyzed_entries,
    }


def main():
    """Main entry point for the cloud job.

    In a real cloud environment, this would:
    1. Read job parameters (folder_name, entry_ids)
    2. Fetch entries from database
    3. Process and generate timelines
    4. Save results back to database
    """
    # Example usage
    folder_name = "Career Reflections"
    entries = [
        {
            "entry_id": "e1",
            "title": "Internship Meeting Stress",
            "folder_name": folder_name,
            "timestamp": "2026-05-01T08:30:00",
            "saved_location": "Boston, MA",
            "text": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
        },
        {
            "entry_id": "e2",
            "title": "Calm Evening with Friends",
            "folder_name": folder_name,
            "timestamp": "2026-05-02T18:15:00",
            "saved_location": "Cambridge, MA",
            "text": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
        },
        {
            "entry_id": "e3",
            "title": "Booked Florence Train",
            "folder_name": folder_name,
            "timestamp": "2026-05-03T10:45:00",
            "saved_location": "Florence, Italy",
            "text": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
        },
        {
            "entry_id": "e4",
            "title": "Burnout After Class",
            "folder_name": folder_name,
            "timestamp": "2026-05-04T21:00:00",
            "saved_location": "Boston University",
            "text": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
        },
    ]

    result = process_folder_entries(folder_name, entries)

    # In cloud job, save to database instead of printing
    logger.info(f"Processed folder {folder_name} with {result['entry_count']} entries")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
