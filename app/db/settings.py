import sqlite3

from app.utils import utc_now_iso

from .connection import get_connection


def get_settings() -> sqlite3.Row:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()
        if row is None:
            now = utc_now_iso()
            conn.execute(
                """
                INSERT INTO settings (
                    id,
                    location_name,
                    location_address,
                    location_description,
                    updated_at,
                    updated_by
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    1,
                    "Welcome Home",
                    "",
                    "See Settings below to change this header.",
                    now,
                    "system",
                ),
            )
            row = conn.execute("SELECT * FROM settings WHERE id = 1").fetchone()

        if row is None:
            raise ValueError("Settings row could not be loaded")

        return row


def update_settings(
    location_name: str,
    location_address: str,
    location_description: str,
    updated_by: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO settings (
                id,
                location_name,
                location_address,
                location_description,
                updated_at,
                updated_by
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                1,
                "Welcome Home",
                "",
                "See Settings below to change this header.",
                utc_now_iso(),
                "system",
            ),
        )

        conn.execute(
            """
            UPDATE settings
            SET
                location_name = ?,
                location_address = ?,
                location_description = ?,
                updated_at = ?,
                updated_by = ?
            WHERE id = 1
            """,
            (
                location_name,
                location_address,
                location_description,
                utc_now_iso(),
                updated_by,
            ),
        )
