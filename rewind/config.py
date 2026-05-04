"""Configuration for ReWind.
Loads API keys and Firebase credentials from .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Natural Language API Key (required)
GCNL_API_KEY = os.getenv("GCNL_API_KEY")
if not GCNL_API_KEY:
    raise ValueError("GCNL_API_KEY not found in .env")

# Firebase Project ID (required for local development)
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Firebase Service Account Key Path (required for local development)
# This file is downloaded from Google Cloud Console and contains credentials
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")

# If service account key is specified, resolve the path
if FIREBASE_SERVICE_ACCOUNT_KEY:
    FIREBASE_SERVICE_ACCOUNT_KEY = str(Path(FIREBASE_SERVICE_ACCOUNT_KEY).expanduser())
