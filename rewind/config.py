"""Configuration for ReWind.
Loads API keys and Firebase credentials from .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Google Cloud Natural Language API Key (required)
GCNL_API_KEY = os.getenv("GCNL_API_KEY")
if not GCNL_API_KEY:
    raise ValueError("GCNL_API_KEY not found in environment")

# Firebase Project ID (recommended for local development)
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Firebase service account as a single-line JSON string
# Example secret name: FIREBASE_SERVICE_ACCOUNT_JSON
FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
