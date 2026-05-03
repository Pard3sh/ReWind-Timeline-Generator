"""Database operations for ReWind sentiment analysis.

Handles reading from and writing to Firestore with the Room schema structure.
Includes location conversion from lat/lng to human-readable strings.
"""

import json
import logging
from typing import List, Dict, Any, Optional

from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


class LocationConverter:
    """Convert latitude/longitude coordinates to human-readable location strings."""

    def __init__(self):
        """Initialize the geocoder with a user agent."""
        self.geocoder = Nominatim(user_agent="rewind_sentiment_analysis")

    def coords_to_location_string(
        self, latitude: Optional[float], longitude: Optional[float]
    ) -> str:
        """Convert lat/lng to a location string like 'Boston, MA, USA'."""
        if latitude is None or longitude is None:
            return ""

        try:
            location = self.geocoder.reverse(f"{latitude}, {longitude}")
            if location:
                address = location.address
                parts = [p.strip() for p in address.split(",")]
                if len(parts) >= 3:
                    return f"{parts[-3]}, {parts[-2]}, {parts[-1]}"
                return address
            return ""
        except Exception as e:
            logger.warning(f"Failed to reverse geocode ({latitude}, {longitude}): {e}")
            return ""


class FirestoreDB:
    """Firestore database operations for ReWind."""

    def __init__(self, firestore_client=None):
        """Initialize Firestore client."""
        if firestore_client is None:
            try:
                import firebase_admin
                from firebase_admin import firestore

                if not firebase_admin._apps:
                    firebase_admin.initialize_app()

                firestore_client = firestore.client()
            except ImportError:
                logger.warning("firebase-admin not installed. DB operations will fail.")
                firestore_client = None
            except Exception as e:
                logger.error(f"Failed to initialize Firestore client: {e}")
                firestore_client = None

        self.db = firestore_client
        self.location_converter = LocationConverter()

    def _ensure_db(self):
        if self.db is None:
            raise RuntimeError("Firestore client is not initialized.")

    def _to_iso_timestamp(self, value: Any) -> str:
        """Convert Firestore/Python timestamp-like values to ISO strings."""
        if value is None:
            return ""
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    def _write_nodes_in_batches(
        self,
        collection_ref,
        nodes: List[Dict[str, Any]],
        batch_size: int = 500,
    ) -> None:
        """Write node documents in Firestore-sized batches."""
        for start in range(0, len(nodes), batch_size):
            chunk = nodes[start : start + batch_size]
            batch = self.db.batch()

            for node in chunk:
                node_ref = collection_ref.document(node["id"])
                batch.set(node_ref, node)

            batch.commit()

    def get_folder(self, user_id: str, folder_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a folder document."""
        try:
            self._ensure_db()
            doc = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
                .get()
            )

            if not doc.exists:
                return None

            data = doc.to_dict()
            data["id"] = doc.id
            return data
        except Exception as e:
            logger.error(f"Error fetching folder {folder_id}: {e}")
            return None

    def get_folder_entries(self, user_id: str, folder_id: str) -> List[Dict[str, Any]]:
        """Fetch all entries for a specific folder."""
        try:
            self._ensure_db()

            query = (
                self.db.collection("users")
                .document(user_id)
                .collection("entries")
                .where("folderId", "==", folder_id)
                .stream()
            )

            entries = []
            for doc in query:
                entry_data = doc.to_dict()
                entry_data["id"] = doc.id

                if "timestamp" in entry_data:
                    entry_data["timestamp"] = self._to_iso_timestamp(
                        entry_data["timestamp"]
                    )

                entries.append(entry_data)

            logger.info(f"Fetched {len(entries)} entries for folder {folder_id}")
            return entries

        except Exception as e:
            logger.error(f"Error fetching entries: {e}")
            return []

    def get_saved_location_for_entry(self, entry: Dict[str, Any]) -> str:
        """Build a display location string from an entry's latitude/longitude."""
        return self.location_converter.coords_to_location_string(
            entry.get("latitude"),
            entry.get("longitude"),
        )

    def write_sentiment_nodes(
        self, user_id: str, folder_id: str, nodes: List[Dict[str, Any]]
    ) -> bool:
        """Write sentiment nodes to Firestore."""
        try:
            self._ensure_db()

            collection_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
                .collection("sentiment_nodes")
            )

            self._write_nodes_in_batches(collection_ref, nodes)
            logger.info(f"Wrote {len(nodes)} sentiment nodes for folder {folder_id}")
            return True

        except Exception as e:
            logger.error(f"Error writing sentiment nodes: {e}")
            return False

    def write_detailed_nodes(
        self, user_id: str, folder_id: str, nodes: List[Dict[str, Any]]
    ) -> bool:
        """Write detailed nodes to Firestore."""
        try:
            self._ensure_db()

            collection_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
                .collection("detailed_nodes")
            )

            self._write_nodes_in_batches(collection_ref, nodes)
            logger.info(f"Wrote {len(nodes)} detailed nodes for folder {folder_id}")
            return True

        except Exception as e:
            logger.error(f"Error writing detailed nodes: {e}")
            return False

    def update_folder_summary(
        self, user_id: str, folder_id: str, summary: Dict[str, Any]
    ) -> bool:
        """Update folder document with summary statistics."""
        try:
            self._ensure_db()

            folder_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
            )

            update_data = {
                "entryCount": summary.get("entry_count", 0),
                "averageSentiment": summary.get("average_sentiment", 0.0),
                "sentimentTrend": summary.get("sentiment_trend", ""),
                "topLocations": json.dumps(summary.get("top_locations", [])),
                "topEvents": json.dumps(summary.get("top_events", [])),
                "summaryText": summary.get("summary_text", ""),
                "startTimestamp": summary.get("start_timestamp"),
                "endTimestamp": summary.get("end_timestamp"),
                "veryPositiveCount": summary.get("very_positive_count", 0),
                "positiveCount": summary.get("positive_count", 0),
                "neutralCount": summary.get("neutral_count", 0),
                "negativeCount": summary.get("negative_count", 0),
                "veryNegativeCount": summary.get("very_negative_count", 0),
            }

            folder_ref.set(update_data, merge=True)
            logger.info(f"Updated folder {folder_id} summary")
            return True

        except Exception as e:
            logger.error(f"Error updating folder summary: {e}")
            return False
