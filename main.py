"""Example script for ReWind sentiment analysis.

This script demonstrates analyzing sample journal entries
and generating sentiment timelines using the real Room/Firestore schema.
"""

import json

from rewind.config import GCNL_API_KEY
from rewind.api import GCNLClient
from rewind.timeline import SentimentFolderTimeline, DetailedFolderTimeline

TEST_USER_ID = "test_user_1"  # the user ids will not resemble this in practice
TEST_FOLDER_ID = "career_reflections"  # folder id will not resemble this in practice
# when this is run as a cloud job, we allow the firestore database to populate the user id and folder id fields so
# the example values above are not an issue
TEST_FOLDER_NAME = "Career Reflections"

# AI generated example entries
entries = [
    {
        "id": "e1",
        "userId": TEST_USER_ID,
        "folderId": TEST_FOLDER_ID,
        "title": "Internship Meeting Stress",
        "body": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
        "timestamp": "2026-05-01T08:30:00",
        "latitude": 42.3601,
        "longitude": -71.0589,
    },
    {
        "id": "e2",
        "userId": TEST_USER_ID,
        "folderId": TEST_FOLDER_ID,
        "title": "Calm Evening with Friends",
        "body": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
        "timestamp": "2026-05-02T18:15:00",
        "latitude": 42.3736,
        "longitude": -71.1097,
    },
    {
        "id": "e3",
        "userId": TEST_USER_ID,
        "folderId": TEST_FOLDER_ID,
        "title": "Booked Florence Train",
        "body": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
        "timestamp": "2026-05-03T10:45:00",
        "latitude": 43.7696,
        "longitude": 11.2558,
    },
    {
        "id": "e4",
        "userId": TEST_USER_ID,
        "folderId": TEST_FOLDER_ID,
        "title": "Burnout After Class",
        "body": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
        "timestamp": "2026-05-04T21:00:00",
        "latitude": 42.3505,
        "longitude": -71.1054,
    },
]


def main():
    """Run the example sentiment analysis."""
    if not GCNL_API_KEY:
        raise ValueError("GCNL_API_KEY is missing.")

    client = GCNLClient(GCNL_API_KEY)
    # saved locations to avoid having to generate coordinate data -- the coordinate value functionality tested seperately
    saved_locations = {
        "e1": "Boston, MA",
        "e2": "Cambridge, MA",
        "e3": "Florence, Italy",
        "e4": "Boston University",
    }

    # save all results to represent as a sample timeline
    all_results = client.analyze_entries(
        entries=entries,
        saved_locations=saved_locations,
        folder_name=TEST_FOLDER_NAME,
    )

    # below is just printing to have a textual representation of the raw analysis and the generated timeline data
    print("RAW ANALYZED RESULTS")
    print("=" * 60)
    print(json.dumps(all_results, indent=2, default=str))
    print()

    sentiment_timeline = SentimentFolderTimeline(TEST_FOLDER_NAME)
    detailed_timeline = DetailedFolderTimeline(TEST_FOLDER_NAME)

    sentiment_timeline.add_nodes_from_analyzed_entries(all_results)
    detailed_timeline.add_nodes_from_analyzed_entries(all_results)

    print("SENTIMENT TIMELINE")
    print("=" * 60)
    print(sentiment_timeline)
    print()

    print("DETAILED TIMELINE")
    print("=" * 60)
    print(detailed_timeline)
    print()

    if sentiment_timeline.summary:
        print("FOLDER SUMMARY PAYLOAD")
        print("=" * 60)
        print(
            json.dumps(
                {
                    "entry_count": sentiment_timeline.summary.entry_count,
                    "average_sentiment": sentiment_timeline.summary.average_sentiment,
                    "sentiment_trend": sentiment_timeline.summary.sentiment_trend,
                    "top_locations": sentiment_timeline.summary.top_locations,
                    "top_events": sentiment_timeline.summary.top_events,
                    "summary_text": sentiment_timeline.summary.summary_text,
                    "start_timestamp": sentiment_timeline.summary.start_timestamp,
                    "end_timestamp": sentiment_timeline.summary.end_timestamp,
                    "very_positive_count": sentiment_timeline.summary.very_positive_count,
                    "positive_count": sentiment_timeline.summary.positive_count,
                    "neutral_count": sentiment_timeline.summary.neutral_count,
                    "negative_count": sentiment_timeline.summary.negative_count,
                    "very_negative_count": sentiment_timeline.summary.very_negative_count,
                },
                indent=2,
                default=str,
            )
        )


if __name__ == "__main__":
    main()
