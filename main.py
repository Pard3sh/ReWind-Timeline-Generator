"""Example script for ReWind sentiment analysis.

This script demonstrates analyzing sample journal entries
and generating sentiment timelines.
"""

import json
from rewind.config import GCNL_API_KEY
from rewind.api import GCNLClient
from rewind.timeline import SentimentFolderTimeline, DetailedFolderTimeline

# Sample journal entries for testing
entries = [
    {
        "entry_id": "e1",
        "title": "Internship Meeting Stress",
        "folder_name": "Career Reflections",
        "timestamp": "2026-05-01T08:30:00",
        "saved_location": "Boston, MA",
        "text": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
    },
    {
        "entry_id": "e2",
        "title": "Calm Evening with Friends",
        "folder_name": "Career Reflections",
        "timestamp": "2026-05-02T18:15:00",
        "saved_location": "Cambridge, MA",
        "text": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
    },
    {
        "entry_id": "e3",
        "title": "Booked Florence Train",
        "folder_name": "Career Reflections",
        "timestamp": "2026-05-03T10:45:00",
        "saved_location": "Florence, Italy",
        "text": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
    },
    {
        "entry_id": "e4",
        "title": "Burnout After Class",
        "folder_name": "Career Reflections",
        "timestamp": "2026-05-04T21:00:00",
        "saved_location": "Boston University",
        "text": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
    },
]


def main():
    """Run the example sentiment analysis."""
    # Initialize the GCNL client
    client = GCNLClient(GCNL_API_KEY)

    # Analyze the sample entries
    all_results = client.analyze_entries(entries)

    print("RAW ANALYZED RESULTS")
    print("=" * 60)
    print(json.dumps(all_results, indent=2))
    print()

    # Get the folder name (assuming all entries are in the same folder for this example)
    folder_name = entries[0]["folder_name"]

    # Create both timeline views
    sentiment_timeline = SentimentFolderTimeline(folder_name)
    detailed_timeline = DetailedFolderTimeline(folder_name)

    # Add the analyzed entries to the timelines
    sentiment_timeline.add_nodes_from_analyzed_entries(all_results)
    detailed_timeline.add_nodes_from_analyzed_entries(all_results)

    # Print the timelines
    print("SENTIMENT TIMELINE")
    print("=" * 60)
    print(sentiment_timeline)
    print()

    print("DETAILED TIMELINE")
    print("=" * 60)
    print(detailed_timeline)


if __name__ == "__main__":
    main()
