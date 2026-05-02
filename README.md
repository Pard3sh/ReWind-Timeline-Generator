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
