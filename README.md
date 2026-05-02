# ReWind Sentiment Analysis

A Python package for analyzing journal entries using Google Cloud Natural Language API to generate sentiment timelines and emotion insights for the ReWind android mobile app.

## Project Structure

```
rewind-sentiment-analysis/
├── rewind/                    # Main package
│   ├── __init__.py           # Package initialization
│   ├── api.py                # GCNL API client
│   ├── config.py             # Configuration and environment loading
│   ├── models.py             # Data models (TimelineNode, FolderSummary)
│   ├── sentiment.py          # Sentiment analysis utilities
│   └── timeline.py           # Timeline generation classes
├── main.py                   # Example script for testing
├── job.py                    # Cloud job entry point
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (API keys)
└── .env.example              # Example environment file
```

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**

   ```bash
   cp .env.example .env
   # Edit .env with your GCNL API key
   ```

3. **Run example:**
   ```bash
   python main.py
   ```

## Cloud Job Usage

The `job.py` script is designed to run as a cloud job that processes folders with new journal entries:

```bash
python job.py
```

In our cloud environment, this would:

- Accept job parameters (folder_name, entry_ids)
- Fetch entries from your database
- Process and generate timelines
- Save results back to the database

## Key Components

### Models (`rewind/models.py`)

- `TimelineNode`: Individual entry with sentiment data
- `FolderSummary`: Aggregated folder statistics

### API Client (`rewind/api.py`)

- `GCNLClient`: Handles GCNL sentiment and entity analysis

### Timeline Generation (`rewind/timeline.py`)

- `BaseFolderTimeline`: Abstract base for timeline containers
- `SentimentFolderTimeline`: Compact sentiment view
- `DetailedFolderTimeline`: Full detail view

### Utilities (`rewind/sentiment.py`)

- Sentiment scoring and labeling
- Emotion inference from text
- Timeline title generation

## Development

The codebase is modular and ready for cloud deployment, but will need to change according to the Cloud database structure.

## AI Reflection

AI assisted team in tools we were not too familiar with, the structure of the codebase, docstrings, template/starter code, and for understanding how to use this repo as a Cloud Job. Instrumental in developing this portion of the project for our application, but was not used to create everything. Had to reject changes that were not applicable to our project, too large for the scope -- such as sentiment and timeline anaylsis for the entire project-- and more.

## Example Output 

Using sample entries, these sample timelines and summaries were generated:

```bash
python3 main.py 
RAW ANALYZED RESULTS
============================================================
[
  {
    "entry_id": "e1",
    "entry_title": "Internship Meeting Stress",
    "generated_title": "Internship Meeting in Boston",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-01T08:30:00",
    "saved_location": "Boston, MA",
    "text": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
    "sentiment_score": 0.6,
    "sentiment_magnitude": 0.6,
    "emotion_label": "Anxious",
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
    "generated_title": "Calm in Cambridge Common",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-02T18:15:00",
    "saved_location": "Cambridge, MA",
    "text": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
    "sentiment_score": 0.9,
    "sentiment_magnitude": 0.9,
    "emotion_label": "Calm",
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
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-03T10:45:00",
    "saved_location": "Florence, Italy",
    "text": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
    "sentiment_score": 0.7,
    "sentiment_magnitude": 1.4,
    "emotion_label": "Anxious",
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
    "generated_title": "Stressed in gym",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-04T21:00:00",
    "saved_location": "Boston University",
    "text": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
    "sentiment_score": -0.6,
    "sentiment_magnitude": 1.3,
    "emotion_label": "Stressed",
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
Top Locations: Boston, Cambridge Common, Florence
Top Events: internship meeting, dinner, trip
Source Entry IDs: e1, e2, e3, e4
Reflection: This folder shows a mixed but generally positive overall mood. Sentiment became more negative over time. Key moments included internship meeting, dinner, trip. The most referenced locations were Boston, Cambridge Common.
------------------------------------------------------------
Nodes
[May 01, 2026 at 08:30 AM]
Title: Internship Meeting in Boston
Mood: 😊 Anxious (+0.60)
Entry ID: e1
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Title: Calm in Cambridge Common
Mood: 😊 Calm (+0.90)
Entry ID: e2
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Title: Trip in Florence
Mood: 😊 Anxious (+0.70)
Entry ID: e3
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Title: Stressed in gym
Mood: ☹️ Stressed (-0.60)
Entry ID: e4
------------------------------------------------------------

DETAILED TIMELINE
============================================================
Folder Timeline: Career Reflections
------------------------------------------------------------
Summary
Folder: Career Reflectionspython3 main.py 
RAW ANALYZED RESULTS
============================================================
[
  {
    "entry_id": "e1",
    "entry_title": "Internship Meeting Stress",
    "generated_title": "Internship Meeting in Boston",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-01T08:30:00",
    "saved_location": "Boston, MA",
    "text": "I felt overwhelmed after my internship meeting in Boston today, but I was proud that I finished my proposal before dinner.",
    "sentiment_score": 0.6,
    "sentiment_magnitude": 0.6,
    "emotion_label": "Anxious",
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
    "generated_title": "Calm in Cambridge Common",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-02T18:15:00",
    "saved_location": "Cambridge, MA",
    "text": "I spent the evening with friends near Cambridge Common and felt calm for the first time all week.",
    "sentiment_score": 0.9,
    "sentiment_magnitude": 0.9,
    "emotion_label": "Calm",
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
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-03T10:45:00",
    "saved_location": "Florence, Italy",
    "text": "I booked my train to Florence and started feeling genuinely excited about the trip. Planning everything made me a little anxious, but mostly hopeful.",
    "sentiment_score": 0.7,
    "sentiment_magnitude": 1.4,
    "emotion_label": "Anxious",
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
    "generated_title": "Stressed in gym",
    "folder_name": "Career Reflections",
    "timestamp": "2026-05-04T21:00:00",
    "saved_location": "Boston University",
    "text": "Classes were exhausting today. I missed the gym, got stuck thinking about deadlines, and felt frustrated walking back from campus.",
    "sentiment_score": -0.6,
    "sentiment_magnitude": 1.3,
    "emotion_label": "Stressed",
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
Top Locations: Boston, Cambridge Common, Florence
Top Events: internship meeting, dinner, trip
Source Entry IDs: e1, e2, e3, e4
Reflection: This folder shows a mixed but generally positive overall mood. Sentiment became more negative over time. Key moments included internship meeting, dinner, trip. The most referenced locations were Boston, Cambridge Common.
------------------------------------------------------------
Nodes
[May 01, 2026 at 08:30 AM]
Title: Internship Meeting in Boston
Mood: 😊 Anxious (+0.60)
Entry ID: e1
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Title: Calm in Cambridge Common
Mood: 😊 Calm (+0.90)
Entry ID: e2
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Title: Trip in Florence
Mood: 😊 Anxious (+0.70)
Entry ID: e3
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Title: Stressed in gym
Mood: ☹️ Stressed (-0.60)
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
Emotion: Anxious
Sentiment: Very Positive (+0.60)
Entry ID: e1
Events: internship meeting, dinner
Mentioned Locations: Boston
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Generated Title: Calm in Cambridge Common
Original Entry Title: Calm Evening with Friends
Saved Location: Cambridge, MA
Emotion: Calm
Sentiment: Very Positive (+0.90)
Entry ID: e2
Mentioned Locations: Cambridge Common
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Generated Title: Trip in Florence
Original Entry Title: Booked Florence Train
Saved Location: Florence, Italy
Emotion: Anxious
Sentiment: Very Positive (+0.70)
Entry ID: e3
Events: trip
Mentioned Locations: Florence
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Generated Title: Stressed in gym
Original Entry Title: Burnout After Class
Saved Location: Boston University
Emotion: Stressed
Sentiment: Negative (-0.60)
Entry ID: e4
Mentioned Locations: gym, campus
------------------------------------------------------------
Period: May 01, 2026 to May 04, 2026
Entries: 4
Average Sentiment: +0.40 (Positive)
Trend: Declining
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
Emotion: Anxious
Sentiment: Very Positive (+0.60)
Entry ID: e1
Events: internship meeting, dinner
Mentioned Locations: Boston
------------------------------------------------------------
[May 02, 2026 at 06:15 PM]
Generated Title: Calm in Cambridge Common
Original Entry Title: Calm Evening with Friends
Saved Location: Cambridge, MA
Emotion: Calm
Sentiment: Very Positive (+0.90)
Entry ID: e2
Mentioned Locations: Cambridge Common
------------------------------------------------------------
[May 03, 2026 at 10:45 AM]
Generated Title: Trip in Florence
Original Entry Title: Booked Florence Train
Saved Location: Florence, Italy
Emotion: Anxious
Sentiment: Very Positive (+0.70)
Entry ID: e3
Events: trip
Mentioned Locations: Florence
------------------------------------------------------------
[May 04, 2026 at 09:00 PM]
Generated Title: Stressed in gym
Original Entry Title: Burnout After Class
Saved Location: Boston University
Emotion: Stressed
Sentiment: Negative (-0.60)
Entry ID: e4
Mentioned Locations: gym, campus
------------------------------------------------------------
```
