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

    # in our Android application, location is saved as lat and long. To generate a human readable timestamp, the package handles conversion

    def __init__(self):
        """Initialize the geocoder with a user agent."""
        self.geocoder = Nominatim(user_agent="rewind_sentiment_analysis")

    def coords_to_location_string(
        self, latitude: Optional[float], longitude: Optional[float]
    ) -> str:
        """Convert lat/lng to a location string like 'Boston, MA, USA'."""
        # lat and long are nullable as users may not give permission
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

    # IMPORTANT -- this will only work properly in the cloud environment which has access to the firebase admin credentials
    def __init__(self, firestore_client=None):
        """Initialize Firestore client."""
        if firestore_client is None:
            try:
                import firebase_admin
                from firebase_admin import firestore

                logger.info("Initializing Firebase Admin SDK...")
                logger.info(
                    f"Firebase apps already initialized: {len(firebase_admin._apps)}"
                )

                if not firebase_admin._apps:
                    logger.info("No Firebase apps found, initializing new app...")

                    # Try to get project ID from environment
                    import os

                    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv(
                        "FIREBASE_PROJECT_ID"
                    )
                    if project_id:
                        logger.info(
                            f"Initializing Firebase with project ID: {project_id}"
                        )
                        firebase_admin.initialize_app(options={"projectId": project_id})
                    else:
                        logger.info(
                            "No project ID specified, using default credentials"
                        )
                        firebase_admin.initialize_app()

                    logger.info("Firebase app initialized successfully")
                else:
                    logger.info("Using existing Firebase app")

                logger.info("Creating Firestore client...")
                firestore_client = firestore.client()
                logger.info("Firestore client created successfully")

                # Log the project ID that Firestore is configured for
                try:
                    project_id = firestore_client.project
                    logger.info(
                        f"Firestore client configured for project: {project_id}"
                    )
                except Exception as proj_error:
                    logger.warning(
                        f"Could not determine Firestore project: {proj_error}"
                    )

            except ImportError as ie:
                logger.warning(
                    f"firebase-admin not installed. DB operations will fail: {ie}"
                )
                firestore_client = None
            except Exception as e:
                logger.error(
                    f"Failed to initialize Firestore client: {e}", exc_info=True
                )
                firestore_client = None

        self.db = firestore_client
        if self.db:
            logger.info("FirestoreDB initialized successfully")
        else:
            logger.error("FirestoreDB initialized with None client")
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

    def get_all_users(self) -> List[str]:
        """Fetch all user IDs from Firestore.

        Returns:
            List of user IDs
        """
        try:
            self._ensure_db()
            logger.info("Attempting to fetch users from Firestore collection 'users'")

            # First, let's check if we can access Firestore at all by listing collections
            try:
                collections = self.db.collections()
                collection_names = [col.id for col in collections]
                logger.info(f"Available Firestore collections: {collection_names}")

                if "users" not in collection_names:
                    logger.warning("No 'users' collection found in Firestore")
                    return []

            except Exception as col_error:
                logger.error(
                    f"Error listing Firestore collections: {col_error}", exc_info=True
                )
                return []

            # Now try to get users
            users_ref = self.db.collection("users")
            logger.info(f"Users collection reference created: {users_ref}")

            # Try to get collection info
            try:
                # This will fail if we don't have permissions, but let's see what happens
                users = users_ref.stream()
                user_ids = []

                # Convert generator to list and log each user found
                user_count = 0
                for doc in users:
                    user_ids.append(doc.id)
                    user_count += 1
                    if user_count <= 5:  # Log first 5 users
                        logger.info(f"Found user: {doc.id}")

                if user_count > 5:
                    logger.info(f"... and {user_count - 5} more users")

                logger.info(
                    f"Successfully fetched {len(user_ids)} users from Firestore"
                )
                return user_ids

            except Exception as stream_error:
                logger.error(
                    f"Error streaming users collection: {stream_error}", exc_info=True
                )
                return []

        except Exception as e:
            logger.error(f"Error fetching users from Firestore: {e}", exc_info=True)
            return []

    def get_all_folders(self, user_id: str) -> List[Dict[str, Any]]:
        """Fetch all folders for a specific user.

        Args:
            user_id: The user ID

        Returns:
            List of folder documents with their IDs
        """
        try:
            self._ensure_db()
            folders_query = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .stream()
            )

            folders = []
            for doc in folders_query:
                folder_data = doc.to_dict()
                folder_data["id"] = doc.id
                folders.append(folder_data)

            logger.info(f"Fetched {len(folders)} folders for user {user_id}")
            return folders
        except Exception as e:
            logger.error(f"Error fetching folders for user {user_id}: {e}")
            return []

    def get_unanalyzed_entries(
        self, user_id: str, folder_id: str
    ) -> List[Dict[str, Any]]:
        """Fetch all unanalyzed entries for a specific folder.

        An entry is considered unanalyzed if it doesn't have a corresponding
        sentiment node yet (or if analyzed=false field exists).

        Args:
            user_id: The user ID
            folder_id: The folder ID

        Returns:
            List of unanalyzed entry documents with their IDs
        """
        try:
            self._ensure_db()

            # Fetch all entries for this folder
            entries_query = (
                self.db.collection("users")
                .document(user_id)
                .collection("entries")
                .where("folderId", "==", folder_id)
                .stream()
            )

            unanalyzed_entries = []
            for doc in entries_query:
                entry_data = doc.to_dict()
                entry_data["id"] = doc.id

                # Check if entry has been analyzed by looking for sentiment nodes
                has_sentiment_node = self._entry_has_sentiment_node(
                    user_id, folder_id, doc.id
                )

                if not has_sentiment_node:
                    unanalyzed_entries.append(entry_data)

            logger.info(
                f"Fetched {len(unanalyzed_entries)} unanalyzed entries for folder {folder_id}"
            )
            return unanalyzed_entries
        except Exception as e:
            logger.error(f"Error fetching unanalyzed entries: {e}")
            return []

    def _entry_has_sentiment_node(
        self, user_id: str, folder_id: str, entry_id: str
    ) -> bool:
        """Check if an entry already has a sentiment node.

        Args:
            user_id: The user ID
            folder_id: The folder ID
            entry_id: The entry ID

        Returns:
            True if sentiment node exists, False otherwise
        """
        try:
            nodes_query = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
                .collection("sentiment_nodes")
                .where("entryId", "==", entry_id)
                .limit(1)
                .stream()
            )

            return any(nodes_query)
        except Exception as e:
            logger.warning(f"Error checking for sentiment node: {e}")
            return False

    def get_saved_location_for_entry(self, entry: Dict[str, Any]) -> str:
        """Convert entry location (lat/lng) to a human-readable string.

        Args:
            entry: The entry document

        Returns:
            Human-readable location string
        """
        saved_location = entry.get("savedLocation", "")
        if saved_location:
            return saved_location

        # Try converting from lat/lng if available
        latitude = entry.get("latitude")
        longitude = entry.get("longitude")

        if latitude is not None and longitude is not None:
            return self.location_converter.coords_to_location_string(
                latitude, longitude
            )

        return ""

    def get_folder(self, user_id: str, folder_id: str) -> Dict[str, Any]:
        """Fetch a specific folder document.

        Args:
            user_id: The user ID
            folder_id: The folder ID

        Returns:
            Folder document data
        """
        try:
            self._ensure_db()
            folder_ref = (
                self.db.collection("users")
                .document(user_id)
                .collection("folders")
                .document(folder_id)
            )

            folder_doc = folder_ref.get()
            if folder_doc.exists:
                return folder_doc.to_dict()
            return {}
        except Exception as e:
            logger.error(f"Error fetching folder {folder_id}: {e}")
            return {}
