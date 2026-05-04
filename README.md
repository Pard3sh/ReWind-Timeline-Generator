# ReWind Sentiment Analysis

A Python package for analyzing journal entries using Google Cloud Natural Language API and transformer-based emotion classification to generate sentiment timelines and emotion insights for the ReWind Android mobile app. PLEASE REFER TO THE DOCKER_GITHUB_ACTIONS.md page (for graders). This backend service runs every 12 hours, but to facilitate faster testing, simply run the github action and see the generated timeline for any of your folders with multiple entries.

_Important!_ Need to read the other README for working with the Cloud aspects

## Features

- **Sentiment analysis** using Google Cloud Natural Language API
- **Emotion detection** using j-hartmann/emotion-english-distilroberta-base transformer model
- **Entity extraction** for locations and events
- **Timeline generation** with sentiment trends and folder summaries
- **Firestore** for cloud database operations
- **Batch processing** for all users and folders
- **Location conversion** from coordinates to human-readable addresses
- **Room-schema compatibility** for Android app integration

## Project Structure

(Ai generated)

```
rewind-sentiment-analysis/
├── rewind/                    # Main package
│   ├── __init__.py           # Package initialization
│   ├── api.py                # GCNL API client for sentiment analysis
│   ├── config.py             # Configuration and environment loading
│   ├── database.py           # Firestore database operations and location conversion
│   ├── models.py             # Data models (TimelineNode, FolderSummary)
│   ├── sentiment.py          # Sentiment analysis utilities and emotion classification
│   ├── serializers.py        # Room schema serialization for Android compatibility
│   └── timeline.py           # Timeline generation classes
├── main.py                   # Example script for testing
├── job.py                    # Cloud job entry point for batch processing
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker container configuration
├── .env                      # Environment variables (API keys)
└── .env.example              # Example environment file
```

## Setup

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your API keys -- only necessary for local sample run
# It is stored as a secret in the cloud environment
# Required: GCNL_API_KEY (Google Cloud Natural Language API key)
```

### 3. Run Example

```bash
python main.py
```

## Cloud Job Usage

The `job.py` script runs as a cloud job that processes **all users and their folders**, analyzing unanalyzed journal entries and generating sentiment timelines:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the sample
python main.py

# use for manual update -- cloud job uses are expensive and had to be descoped :(
python job.py
```

### What the Job Does

1. **Fetches all users** from Firestore
2. **Iterates through each user's folders**
3. **Identifies unanalyzed entries** (entries without sentiment nodes)
4. **Analyzes entries** using GCNL API + emotion classification
5. **Generates timeline nodes** (sentiment + detailed views)
6. **Converts locations** from coordinates to readable addresses
7. **Updates Firestore** with new nodes and folder summaries
8. **Returns processing statistics** (folders processed, entries analyzed)

This is clearly crude and not ready for scalability or real production deployment but such considerations had to be descoped for time.

### Environment Variables

- `GCNL_API_KEY`: Google Cloud Natural Language API key
- `FIREBASE_SERVICE_ACCOUNT_JSON`: Path to Firebase service account JSON (optional, uses default credentials)

## Key Components

### Database Layer (`rewind/database.py`)

- `FirestoreDB`: Handles all Firestore operations
- `LocationConverter`: Converts lat/lng coordinates to human-readable addresses using geopy
- Methods for fetching users, folders, entries, and writing timeline data

### API Client (`rewind/api.py`)

- `GCNLClient`: Handles Google Cloud Natural Language API calls
- Performs sentiment analysis, entity extraction, and emotion classification
- Processes entries in batches for efficiency

### Models (`rewind/models.py`)

- `TimelineNode`: Individual entry with sentiment data and metadata
- `FolderSummary`: Aggregated folder statistics and trends

### Timeline Generation (`rewind/timeline.py`)

- `BaseFolderTimeline`: Abstract base for timeline containers
- `SentimentFolderTimeline`: Compact sentiment-focused view
- `DetailedFolderTimeline`: Full detail view with all metadata

### Serializers (`rewind/serializers.py`)

- Converts timeline data to Room-compatible schema
- Handles Android database field naming conventions
- Serializes complex data types (lists, timestamps)

### Utilities (`rewind/sentiment.py`)

- Sentiment scoring and labeling functions
- Emotion inference using transformer model
- Timeline title generation from entities
- Timestamp parsing and formatting

## AI Models Used

### Google Cloud Natural Language API

- **Document-level sentiment**: Score (-1 to +1) and magnitude (0+)
- **Entity extraction**: Locations, events, people, organizations
- **Entity sentiment**: Individual sentiment for each extracted entity

### j-hartmann/emotion-english-distilroberta-base

- **Transformer model**: DistilRoBERTa-base for emotion classification
- **6 emotion categories**: Joy, Anger, Sadness, Fear, Disgust, Surprise
- **Fallback logic**: Keyword-based emotion detection if model unavailable

## Data Flow

1. **Entry Processing**: Raw journal entries with text, timestamps, coordinates
2. **Location Conversion**: Latitude/longitude -> "City, Town, Country"
3. **Sentiment Analysis**: GCNL API extracts sentiment score and entities
4. **Emotion Classification**: Transformer model determines emotion label
5. **Timeline Generation**: Entries organized chronologically with trends
6. **Schema Serialization**: Data formatted for Android Room database
7. **Firestore Storage**: Timeline nodes and summaries saved to cloud (when run as a cloud job)

## Development Notes

- **Modular Architecture**: Each component has clear responsibilities
- **Error Handling**: fallbacks for API failures
- **Batch Processing**: handling of multiple entries -- very crude and would need to be refined for scaling
- **Schema Compatibility**: Exact field mapping to Android Room entities -- exact one to one to avoid more processing later
- **Cloud Ready**: Containerizable

## AI Assistance

AI assisted in:

- Codebase structure and organization -- such as proper way to split up such a project structure. very useful for newcomers to python package creation
- Integration with Hugging Face library
- Batch job processing (had to reject suggestion to constantly)
- Firestore database operations
- Suggestions for ML processing. Rejected complex changes that would not be implemented in time -- such as a library that could detect most positive and most negative sentences per entry
- Error handling and logging
- Documentation, especially docstrings. Added more human readable notes on top of this
- Creating sample entries to test sentiment extraction and timeline generation

Design, setting up with cloud, editing placeholder code, testing, and majority of coding completed by team

## Example Output

Sample analysis of journal entries showing sentiment progression:

```
RAW ANALYZED RESULTS
============================================================
[
  {
    "entry_id": "e1",
    "entry_title": "Internship Meeting Stress",
    "generated_title": "Internship Meeting in Boston",
    "user_id": "test_user_1",
    "folder_id": "career_reflections",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-01T08:30:00",
    "saved_location": "Boston, MA",
    "latitude": 42.3601,
    "longitude": -71.0589,
    "body": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
    "sentiment_score": 0.6,
    "sentiment_magnitude": 0.6,
    "sentiment_label": "Very Positive",
    "emotion_label": "Surprise",
    "extracted_locations": [
      "Boston"
    ],
    "extracted_events": [
      "internship meeting",
      "dinner"
    ],
    "entities": [
      {
        "name": "internship meeting",
        "type": "EVENT",
        "salience": 0.3551437,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "proposal",
        "type": "WORK_OF_ART",
        "salience": 0.2522681,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "Boston",
        "type": "LOCATION",
        "salience": 0.21418664,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "dinner",
        "type": "EVENT",
        "salience": 0.17840157,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      }
    ]
  },
  {
    "entry_id": "e2",
    "entry_title": "Calm Evening with Friends",
    "generated_title": "Joy in Cambridge Common",
    "user_id": "test_user_1",
    "folder_id": "career_reflections",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-02T18:15:00",
    "saved_location": "Cambridge, MA",
    "latitude": 42.3736,
    "longitude": -71.1097,
    "body": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
    "sentiment_score": 0.9,
    "sentiment_magnitude": 0.9,
    "sentiment_label": "Very Positive",
    "emotion_label": "Joy",
    "extracted_locations": [
      "Cambridge Common"
    ],
    "extracted_events": [],
    "entities": [
      {
        "name": "friends",
        "type": "PERSON",
        "salience": 0.42635244,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "time",
        "type": "OTHER",
        "salience": 0.30774072,
        "sentiment_score": 0.4,
        "sentiment_magnitude": 0.4
      },
      {
        "name": "Cambridge Common",
        "type": "LOCATION",
        "salience": 0.2659068,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      }
    ]
  },
  {
    "entry_id": "e3",
    "entry_title": "Booked Florence Train",
    "generated_title": "Trip in Florence",
    "user_id": "test_user_1",
    "folder_id": "career_reflections",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-03T10:45:00",
    "saved_location": "Florence, Italy",
    "latitude": 43.7696,
    "longitude": 11.2558,
    "body": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
    "sentiment_score": 0.7,
    "sentiment_magnitude": 1.4,
    "sentiment_label": "Very Positive",
    "emotion_label": "Joy",
    "extracted_locations": [
      "Florence"
    ],
    "extracted_events": [
      "trip"
    ],
    "entities": [
      {
        "name": "train",
        "type": "OTHER",
        "salience": 0.56501836,
        "sentiment_score": 0.6,
        "sentiment_magnitude": 0.6
      },
      {
        "name": "trip",
        "type": "EVENT",
        "salience": 0.18676172,
        "sentiment_score": 0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "Florence",
        "type": "LOCATION",
        "salience": 0.16302916,
        "sentiment_score": 0.6,
        "sentiment_magnitude": 0.6
      },
      {
        "name": "everything",
        "type": "OTHER",
        "salience": 0.085190766,
        "sentiment_score": 0.3,
        "sentiment_magnitude": 0.3
      }
    ]
  },
  {
    "entry_id": "e4",
    "entry_title": "Burnout After Class",
    "generated_title": "Anger in gym",
    "user_id": "test_user_1",
    "folder_id": "career_reflections",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-04T21:00:00",
    "saved_location": "Boston University",
    "latitude": 42.3505,
    "longitude": -71.1054,
    "body": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
    "sentiment_score": -0.6,
    "sentiment_magnitude": 1.3,
    "sentiment_label": "Negative",
    "emotion_label": "Anger",
    "extracted_locations": [
      "gym",
      "campus"
    ],
    "extracted_events": [],
    "entities": [
      {
        "name": "Classes",
        "type": "OTHER",
        "salience": 0.7203275,
        "sentiment_score": -0.7,
        "sentiment_magnitude": 0.7
      },
      {
        "name": "gym",
        "type": "LOCATION",
        "salience": 0.11499833,
        "sentiment_score": -0.4,
        "sentiment_magnitude": 0.4
      },
      {
        "name": "deadlines",
        "type": "OTHER",
        "salience": 0.10713159,
        "sentiment_score": -0.5,
        "sentiment_magnitude": 0.5
      },
      {
        "name": "campus",
        "type": "LOCATION",
        "salience": 0.057542562,
        "sentiment_score": -0.5,
        "sentiment_magnitude": 0.5
      }
    ]
  }
]

SENTIMENT TIMELINE
============================================================
Folder Timeline: Career Reflections
------------------------------------------------------------
Summary
Folder: Career Reflections
Period: May 01, 2026 to May 04, 2026
Entries: 4
Average Sentiment: +0.40 (Positive)
Trend: Declining
Distribution: Very Positive=3, Positive=0, Neutral=0, Negative=1, Very Negative=0
Top Locations: Boston, Cambridge Common, Florence
Top Events: internship meeting, dinner, trip
Source Entry IDs: e1, e2, e3, e4
Reflection: This folder shows a mixed but generally positive overall mood. Sentiment became more negative over time. Key moments included internship meeting, dinner, trip. The most referenced locations were Boston, Cambridge Common.
------------------------------------------------------------
Nodes
[May 01, 2026 at 08:30 AM]
Title: Internship Meeting in Boston
Mood: 😊 Surprise (+0.60)
Entry ID: e1
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Title: Joy in Cambridge Common
Mood: 😊 Joy (+0.90)
Entry ID: e2
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Title: Trip in Florence
Mood: 😊 Joy (+0.70)
Entry ID: e3
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Title: Anger in gym
Mood: ☹️ Anger (-0.60)
Entry ID: e4
------------------------------------------------------------

DETAILED TIMELINE
============================================================
Folder Timeline: Career Reflections
------------------------------------------------------------
Summary
Folder: Career Reflections
Period: May 01, 2026 to May 04, 2026
Entries: 4
Average Sentiment: +0.40 (Positive)
Trend: Declining
Distribution: Very Positive=3, Positive=0, Neutral=0, Negative=1, Very Negative=0
Top Locations: Boston, Cambridge Common, Florence
Top Events: internship meeting, dinner, trip
Source Entry IDs: e1, e2, e3, e4
Reflection: This folder shows a mixed but generally positive overall mood. Sentiment became more negative over time. Key moments included internship meeting, dinner, trip. The most referenced locations were Boston, Cambridge Common.
------------------------------------------------------------
Nodes
[May 01, 2026 at 08:30 AM]
Generated Title: Internship Meeting in Boston
Original Entry Title: Internship Meeting Stress
Saved Location: Boston, MA
Emotion: Surprise
Sentiment: Very Positive (+0.60)
Entry ID: e1
Events: internship meeting, dinner
Mentioned Locations: Boston
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Generated Title: Joy in Cambridge Common
Original Entry Title: Calm Evening with Friends
Saved Location: Cambridge, MA
Emotion: Joy
Sentiment: Very Positive (+0.90)
Entry ID: e2
Mentioned Locations: Cambridge Common
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Generated Title: Trip in Florence
Original Entry Title: Booked Florence Train
Saved Location: Florence, Italy
Emotion: Joy
Sentiment: Very Positive (+0.70)
Entry ID: e3
Events: trip
Mentioned Locations: Florence
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Generated Title: Anger in gym
Original Entry Title: Burnout After Class
Saved Location: Boston University
Emotion: Anger
Sentiment: Negative (-0.60)
Entry ID: e4
Mentioned Locations: gym, campus
------------------------------------------------------------

FOLDER SUMMARY PAYLOAD
============================================================
{
  "entry_count": 4,
  "average_sentiment": 0.4,
  "sentiment_trend": "Declining",
  "top_locations": [
    "Boston",
    "Cambridge Common",
    "Florence"
  ],
  "top_events": [
    "internship meeting",
    "dinner",
    "trip"
  ],
  "summary_text": "This folder shows a mixed but generally positive overall mood. Sentiment became more negative over time. Key moments included internship meeting, dinner, trip. The most referenced locations were Boston, Cambridge Common.",
  "start_timestamp": "2026-05-01T08:30:00",
  "end_timestamp": "2026-05-04T21:00:00",
  "very_positive_count": 3,
  "positive_count": 0,
  "neutral_count": 0,
  "negative_count": 1,
  "very_negative_count": 0
}
```
