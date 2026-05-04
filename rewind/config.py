"""Configuration for ReWind.
access api key
"""

import os
from dotenv import load_dotenv

load_dotenv()

GCNL_API_KEY = os.getenv("GCNL_API_KEY")
if not GCNL_API_KEY:
    raise ValueError("GCNL_API_KEY not found in .env")
