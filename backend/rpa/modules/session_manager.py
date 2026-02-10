"""
Session Manager - Handle session persistence with encryption
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

import aiosqlite
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class SessionManager:
    """Manage session encryption and persistence"""

    def __init__(self):
        self.cipher = self._get_cipher()
        self.session_expiry_days = 30

    def _get_cipher(self) -> Fernet:
        """Get Fernet cipher from environment variable"""
        key = os.getenv("SESSION_ENCRYPTION_KEY")

        if not key:
            # Generate a warning and use a default key (NOT SECURE for production)
            logger.warning("SESSION_ENCRYPTION_KEY not set, using default key (not secure)")
            key = Fernet.generate_key()

        # Ensure key is bytes
        if isinstance(key, str):
            key = key.encode()

        return Fernet(key)

    async def _get_db(self):
        """Get async database connection"""
        db_path = Path(__file__).parent.parent.parent / "data" / "rpa.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return await aiosqlite.connect(db_path)

    async def save_session(self, cookies: list[dict], user_info: Optional[dict] = None) -> bool:
        """
        Save session with encryption

        Args:
            cookies: List of cookie dictionaries
            user_info: User information dictionary

        Returns:
            bool: True if successful
        """
        try:
            # Serialize and encrypt cookies
            cookies_json = json.dumps(cookies)
            encrypted_cookies = self.cipher.encrypt(cookies_json.encode())

            # Serialize user info
            user_info_json = json.dumps(user_info) if user_info else None

            # Calculate expiry date
            expires_at = datetime.now() + timedelta(days=self.session_expiry_days)

            # Save to database
            conn = await self._get_db()
            try:
                # Delete existing sessions (singleton pattern)
                await conn.execute("DELETE FROM sessions")

                # Insert new session
                await conn.execute(
                    """
                    INSERT INTO sessions (cookies, user_info, created_at, expires_at)
                    VALUES (?, ?, ?, ?)
                """,
                    (encrypted_cookies, user_info_json, datetime.now(), expires_at),
                )

                await conn.commit()
                logger.info("Session saved successfully")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    async def load_session(self) -> Optional[dict[str, Any]]:
        """
        Load and decrypt session

        Returns:
            dict with cookies and user_info, or None if no valid session
        """
        try:
            conn = await self._get_db()

            # Get most recent session
            async with conn.execute("""
                SELECT cookies, user_info, expires_at
                FROM sessions
                ORDER BY created_at DESC
                LIMIT 1
            """) as cursor:
                row = await cursor.fetchone()

                if not row:
                    logger.debug("No session found in database")
                    return None

                encrypted_cookies, user_info_json, expires_at = row

                # Check expiry
                if expires_at and datetime.fromisoformat(expires_at) < datetime.now():
                    logger.info("Session expired, deleting")
                    await self.delete_session()
                    return None

                # Decrypt cookies
                decrypted_cookies = self.cipher.decrypt(encrypted_cookies)
                cookies = json.loads(decrypted_cookies)

                # Parse user info
                user_info = json.loads(user_info_json) if user_info_json else None

                logger.info("Session loaded successfully")
                return {"cookies": cookies, "user_info": user_info}

        except Exception as e:
            logger.error(f"Failed to load session: {e}")
            # Delete corrupted session
            await self.delete_session()
            return None

    async def delete_session(self) -> bool:
        """
        Delete current session

        Returns:
            bool: True if successful
        """
        try:
            conn = await self._get_db()
            try:
                await conn.execute("DELETE FROM sessions")
                await conn.commit()
                logger.info("Session deleted successfully")
                return True
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    async def is_valid_session(self) -> bool:
        """
        Check if a valid session exists

        Returns:
            bool: True if valid session exists
        """
        try:
            session = await self.load_session()
            return session is not None

        except Exception as e:
            logger.error(f"Failed to check session validity: {e}")
            return False

    async def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Clean up sessions older than specified days

        Args:
            days: Number of days to keep

        Returns:
            int: Number of sessions deleted
        """
        try:
            conn = await self._get_db()
            try:
                cutoff_date = datetime.now() - timedelta(days=days)

                cursor = await conn.execute(
                    """
                    DELETE FROM sessions
                    WHERE created_at < ?
                """,
                    (cutoff_date,),
                )

                deleted_count = cursor.rowcount
                await conn.commit()

                logger.info(f"Cleaned up {deleted_count} old sessions")
                return deleted_count
            finally:
                await conn.close()

        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
