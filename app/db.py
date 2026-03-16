import sqlite3
from pathlib import Path

from app.utils import is_valid_hex_color, make_uid, normalize_label_name

DB_PATH = Path(__file__).parent.parent / "data" / "logbook.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        # Dev mode: schema changes are applied by recreating data/logbook.db.
        # Do not add migration/backfill logic here.
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS vendors (
                id                     INTEGER PRIMARY KEY,
                vendor_uid             TEXT UNIQUE NOT NULL,
                vendor_name            TEXT NOT NULL,
                vendor_account_number  TEXT,
                vendor_portal_url      TEXT,
                vendor_portal_username TEXT,
                vendor_phone_number    TEXT,
                vendor_address         TEXT,
                vendor_notes           TEXT,
                vendor_details_json    TEXT,
                vendor_created_at      TEXT NOT NULL,
                vendor_created_by      TEXT,
                vendor_updated_at      TEXT,
                vendor_updated_by      TEXT,
                vendor_archived_at     TEXT
            );

            CREATE TABLE IF NOT EXISTS entries (
                id                   INTEGER PRIMARY KEY,
                entry_uid            TEXT UNIQUE NOT NULL,
                vendor_id            INTEGER NOT NULL,
                entry_title          TEXT,
                entry_interaction_at TEXT,
                entry_body_text      TEXT,
                entry_rep_name       TEXT,
                entry_extra_json     TEXT,
                entry_created_at     TEXT NOT NULL,
                entry_created_by     TEXT,
                entry_updated_at     TEXT,
                entry_updated_by     TEXT,
                entry_archived_at    TEXT,
                FOREIGN KEY (vendor_id) REFERENCES vendors(id)
            );

            CREATE TABLE IF NOT EXISTS attachments (
                id                            INTEGER PRIMARY KEY,
                attachment_uid                TEXT NOT NULL UNIQUE,
                entry_id                      INTEGER NOT NULL,
                attachment_original_filename  TEXT NOT NULL,
                attachment_stored_filename    TEXT NOT NULL,
                attachment_relative_path      TEXT NOT NULL,
                attachment_mime_type          TEXT,
                attachment_file_size          INTEGER,
                attachment_checksum_sha256    TEXT,
                attachment_created_at         TEXT NOT NULL,
                attachment_created_by         TEXT,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            );

            CREATE TABLE IF NOT EXISTS labels (
                id          INTEGER PRIMARY KEY,
                label_uid   TEXT UNIQUE NOT NULL,
                label_name        TEXT NOT NULL UNIQUE COLLATE NOCASE,
                label_color       TEXT,
                label_created_at  TEXT NOT NULL,
                label_created_by  TEXT,
                label_updated_at  TEXT,
                label_updated_by  TEXT
            );

            CREATE TABLE IF NOT EXISTS vendor_labels (
                vendor_id INTEGER NOT NULL,
                label_id  INTEGER NOT NULL,
                PRIMARY KEY (vendor_id, label_id),
                FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE CASCADE,
                FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS entry_labels (
                entry_id INTEGER NOT NULL,
                label_id INTEGER NOT NULL,
                PRIMARY KEY (entry_id, label_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                FOREIGN KEY (label_id) REFERENCES labels(id) ON DELETE CASCADE
            );

            CREATE UNIQUE INDEX IF NOT EXISTS idx_vendors_vendor_uid
                ON vendors (vendor_uid);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_entries_entry_uid
                ON entries (entry_uid);

            CREATE INDEX IF NOT EXISTS idx_entries_vendor_created_at
                ON entries (vendor_id, entry_created_at DESC);

            CREATE INDEX IF NOT EXISTS idx_attachments_entry_id
                ON attachments (entry_id);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_attachments_attachment_uid
                ON attachments (attachment_uid);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_labels_label_uid
                ON labels (label_uid);

            CREATE UNIQUE INDEX IF NOT EXISTS idx_labels_name_nocase
                ON labels (label_name COLLATE NOCASE);

            CREATE INDEX IF NOT EXISTS idx_vendor_labels_label_id
                ON vendor_labels (label_id);

            CREATE INDEX IF NOT EXISTS idx_entry_labels_label_id
                ON entry_labels (label_id);
        """)


# ---------------------------------------------------------------------------
# Vendor helpers
# ---------------------------------------------------------------------------

def get_vendor_by_uid(vendor_uid: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM vendors WHERE vendor_uid = ?",
            (vendor_uid,),
        ).fetchone()


def list_vendors(include_archived: bool = False) -> list[sqlite3.Row]:
    with get_connection() as conn:
        if include_archived:
            return conn.execute(
                "SELECT * FROM vendors ORDER BY vendor_archived_at IS NOT NULL, vendor_name"
            ).fetchall()
        return conn.execute(
            "SELECT * FROM vendors WHERE vendor_archived_at IS NULL ORDER BY vendor_name"
        ).fetchall()


def create_vendor(
    vendor_uid: str,
    vendor_name: str,
    vendor_account_number: str | None,
    vendor_portal_url: str | None,
    vendor_portal_username: str | None,
    vendor_phone_number: str | None,
    vendor_address: str | None,
    vendor_notes: str | None,
    vendor_created_at: str,
    vendor_created_by: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO vendors (
                vendor_uid, vendor_name, vendor_account_number,
                vendor_portal_url, vendor_portal_username,
                vendor_phone_number, vendor_address,
                vendor_notes, vendor_created_at, vendor_created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                vendor_uid,
                vendor_name,
                vendor_account_number,
                vendor_portal_url,
                vendor_portal_username,
                vendor_phone_number,
                vendor_address,
                vendor_notes,
                vendor_created_at,
                vendor_created_by,
            ),
        )


def update_vendor_by_uid(
    vendor_uid: str,
    vendor_name: str,
    vendor_account_number: str | None,
    vendor_portal_url: str | None,
    vendor_portal_username: str | None,
    vendor_phone_number: str | None,
    vendor_address: str | None,
    vendor_notes: str | None,
    vendor_updated_at: str,
    vendor_updated_by: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE vendors
            SET
                vendor_name = ?,
                vendor_account_number = ?,
                vendor_portal_url = ?,
                vendor_portal_username = ?,
                vendor_phone_number = ?,
                vendor_address = ?,
                vendor_notes = ?,
                vendor_updated_at = ?,
                vendor_updated_by = ?
            WHERE vendor_uid = ?
            """,
            (
                vendor_name,
                vendor_account_number,
                vendor_portal_url,
                vendor_portal_username,
                vendor_phone_number,
                vendor_address,
                vendor_notes,
                vendor_updated_at,
                vendor_updated_by,
                vendor_uid,
            ),
        )


def archive_vendor_by_uid(vendor_uid: str, vendor_archived_at: str, vendor_updated_by: str) -> bool:
    """Returns False if the vendor does not exist."""
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT id FROM vendors WHERE vendor_uid = ?",
            (vendor_uid,),
        ).fetchone()
        if exists is None:
            return False
        conn.execute(
            """
            UPDATE vendors
            SET vendor_archived_at = ?, vendor_updated_at = ?, vendor_updated_by = ?
            WHERE vendor_uid = ?
            """,
            (vendor_archived_at, vendor_archived_at, vendor_updated_by, vendor_uid),
        )
        return True


def unarchive_vendor_by_uid(vendor_uid: str, vendor_updated_at: str, vendor_updated_by: str) -> bool:
    """Returns False if the vendor does not exist."""
    with get_connection() as conn:
        exists = conn.execute(
            "SELECT id FROM vendors WHERE vendor_uid = ?",
            (vendor_uid,),
        ).fetchone()
        if exists is None:
            return False
        conn.execute(
            """
            UPDATE vendors
            SET vendor_archived_at = NULL, vendor_updated_at = ?, vendor_updated_by = ?
            WHERE vendor_uid = ?
            """,
            (vendor_updated_at, vendor_updated_by, vendor_uid),
        )
        return True


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

def list_labels() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, label_uid, label_name AS name, label_color AS color,
                   label_created_at AS created_at, label_created_by AS created_by,
                   label_updated_at AS updated_at, label_updated_by AS updated_by
            FROM labels
            ORDER BY label_name COLLATE NOCASE
            """
        ).fetchall()


def get_label_by_uid(label_uid: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, label_uid, label_name AS name, label_color AS color,
                   label_created_at AS created_at, label_created_by AS created_by,
                   label_updated_at AS updated_at, label_updated_by AS updated_by
            FROM labels
            WHERE label_uid = ?
            """,
            (label_uid,),
        ).fetchone()


def get_label_by_name(name: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, label_uid, label_name AS name, label_color AS color,
                   label_created_at AS created_at, label_created_by AS created_by,
                   label_updated_at AS updated_at, label_updated_by AS updated_by
            FROM labels
            WHERE label_name = ? COLLATE NOCASE
            """,
            (name,),
        ).fetchone()


def create_label(
    label_uid: str,
    name: str,
    color: str | None,
    created_at: str,
    created_by: str | None,
) -> int:
    if not is_valid_hex_color(color):
        raise ValueError(f"Invalid color format: {color}. Must be hex (e.g., #RRGGBB)")
    
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO labels (
                label_uid, label_name, label_color,
                label_created_at, label_created_by
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (label_uid, name, color, created_at, created_by),
        )
        return cursor.lastrowid


def update_label_by_uid(
    label_uid: str,
    name: str,
    color: str | None,
    updated_at: str,
    updated_by: str | None,
) -> bool:
    if not is_valid_hex_color(color):
        raise ValueError(f"Invalid color format: {color}. Must be hex (e.g., #RRGGBB)")
    
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM labels WHERE label_uid = ?",
            (label_uid,),
        ).fetchone()
        if existing is None:
            return False

        try:
            conn.execute(
                """
                UPDATE labels
                SET
                    label_name = ?,
                    label_color = ?,
                    label_updated_at = ?,
                    label_updated_by = ?
                WHERE label_uid = ?
                """,
                (name, color, updated_at, updated_by, label_uid),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("A label with that name already exists") from exc

        return True


def delete_label_by_uid(label_uid: str) -> bool:
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM labels WHERE label_uid = ?",
            (label_uid,),
        )
        return cursor.rowcount > 0


def search_labels_by_name(query: str, limit: int = 10) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, label_uid, label_name AS name, label_color AS color,
                   label_created_at AS created_at, label_created_by AS created_by,
                   label_updated_at AS updated_at, label_updated_by AS updated_by
            FROM labels
            WHERE label_name LIKE ? COLLATE NOCASE
            ORDER BY label_name COLLATE NOCASE
            LIMIT ?
            """,
            (f"%{query}%", limit),
        ).fetchall()


def list_labels_for_vendor_id(vendor_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT l.id, l.label_uid, l.label_name AS name, l.label_color AS color
            FROM vendor_labels vl
            JOIN labels l ON l.id = vl.label_id
            WHERE vl.vendor_id = ?
            ORDER BY l.label_name COLLATE NOCASE
            """,
            (vendor_id,),
        ).fetchall()


def replace_vendor_labels(vendor_id: int, label_ids: list[int]) -> None:
    unique_label_ids = list(dict.fromkeys(label_ids))
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM vendor_labels WHERE vendor_id = ?",
            (vendor_id,),
        )
        if unique_label_ids:
            conn.executemany(
                "INSERT INTO vendor_labels (vendor_id, label_id) VALUES (?, ?)",
                [(vendor_id, label_id) for label_id in unique_label_ids],
            )


def list_labels_for_entry_id(entry_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT l.id, l.label_uid, l.label_name AS name, l.label_color AS color
            FROM entry_labels el
            JOIN labels l ON l.id = el.label_id
            WHERE el.entry_id = ?
            ORDER BY l.label_name COLLATE NOCASE
            """,
            (entry_id,),
        ).fetchall()


def replace_entry_labels(entry_id: int, label_ids: list[int]) -> None:
    unique_label_ids = list(dict.fromkeys(label_ids))
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM entry_labels WHERE entry_id = ?",
            (entry_id,),
        )
        if unique_label_ids:
            conn.executemany(
                "INSERT INTO entry_labels (entry_id, label_id) VALUES (?, ?)",
                [(entry_id, label_id) for label_id in unique_label_ids],
            )


def resolve_submitted_labels(
    label_uids: list[str],
    new_label_names: list[str],
    actor: str | None,
    now: str,
) -> list[int]:
    resolved_ids: list[int] = []
    seen_ids: set[int] = set()

    for label_uid in label_uids:
        row = get_label_by_uid((label_uid or "").strip())
        if row is None:
            continue
        label_id = int(row["id"])
        if label_id in seen_ids:
            continue
        seen_ids.add(label_id)
        resolved_ids.append(label_id)

    for raw_name in new_label_names:
        normalized_name = normalize_label_name(raw_name)
        if not normalized_name:
            continue

        row = get_label_by_name(normalized_name)
        if row is None:
            try:
                new_id = create_label(
                    label_uid=make_uid("label"),
                    name=normalized_name,
                    color=None,
                    created_at=now,
                    created_by=actor,
                )
            except sqlite3.IntegrityError:
                retry_row = get_label_by_name(normalized_name)
                if retry_row is None:
                    continue
                new_id = int(retry_row["id"])
            label_id = new_id
        else:
            label_id = int(row["id"])

        if label_id in seen_ids:
            continue
        seen_ids.add(label_id)
        resolved_ids.append(label_id)

    return resolved_ids


# ---------------------------------------------------------------------------
# Entry helpers
# ---------------------------------------------------------------------------

def list_entries_for_vendor(vendor_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT *
            FROM entries
            WHERE vendor_id = ?
              AND entry_archived_at IS NULL
            ORDER BY entry_created_at DESC, id DESC
            """,
            (vendor_id,),
        ).fetchall()


def get_entry_by_uid(entry_uid: str) -> sqlite3.Row | None:
    """Returns the entry row joined with vendor_uid and vendor name."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT e.*, v.vendor_uid, v.vendor_name
            FROM entries e
            JOIN vendors v ON v.id = e.vendor_id
            WHERE e.entry_uid = ?
            """,
            (entry_uid,),
        ).fetchone()


def create_entry(
    entry_uid: str,
    vendor_id: int,
    entry_title: str | None,
    entry_interaction_at: str | None,
    entry_body_text: str | None,
    entry_rep_name: str | None,
    entry_created_by: str,
    entry_created_at: str,
) -> int:
    """Inserts an entry and returns the new row id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO entries (
                entry_uid, vendor_id, entry_title, entry_interaction_at,
                entry_body_text, entry_rep_name, entry_created_by, entry_created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_uid,
                vendor_id,
                entry_title,
                entry_interaction_at,
                entry_body_text,
                entry_rep_name,
                entry_created_by,
                entry_created_at,
            ),
        )
        return cursor.lastrowid


def update_entry_by_uid(
    entry_uid: str,
    entry_title: str | None,
    entry_interaction_at: str | None,
    entry_body_text: str | None,
    entry_rep_name: str | None,
    entry_updated_at: str,
    entry_updated_by: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE entries
            SET
                entry_title = ?,
                entry_interaction_at = ?,
                entry_body_text = ?,
                entry_rep_name = ?,
                entry_updated_at = ?,
                entry_updated_by = ?
            WHERE entry_uid = ?
            """,
            (
                entry_title,
                entry_interaction_at,
                entry_body_text,
                entry_rep_name,
                entry_updated_at,
                entry_updated_by,
                entry_uid,
            ),
        )


# ---------------------------------------------------------------------------
# Attachment helpers
# ---------------------------------------------------------------------------

def get_attachment_by_uid(attachment_uid: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT attachment_uid, entry_id, attachment_original_filename,
                   attachment_relative_path, attachment_mime_type
            FROM attachments
            WHERE attachment_uid = ?
            """,
            (attachment_uid,),
        ).fetchone()


def list_attachments_for_entry_id(entry_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT id, attachment_uid, entry_id, attachment_original_filename,
                   attachment_relative_path, attachment_mime_type,
                   attachment_file_size, attachment_created_at
            FROM attachments
            WHERE entry_id = ?
            ORDER BY id ASC
            """,
            (entry_id,),
        ).fetchall()


# NOTE:
# This dynamically generates "?, ?, ?" placeholders for a parameterized IN clause.
# Only placeholder tokens are interpolated, never user input.
# The actual values are still bound safely through sqlite parameters.
def list_attachments_for_entry_ids(entry_ids: list[int]) -> list[sqlite3.Row]:
    if not entry_ids:
        return []
    with get_connection() as conn:
        param_placeholders = ",".join("?" for _ in entry_ids)
        return conn.execute(
            f"""
            SELECT attachment_uid, entry_id, attachment_original_filename
            FROM attachments
            WHERE entry_id IN ({param_placeholders})
            ORDER BY id ASC
            """,
            tuple(entry_ids),
        ).fetchall()


def create_attachment(
    attachment_uid: str,
    entry_id: int,
    attachment_original_filename: str,
    attachment_stored_filename: str,
    attachment_relative_path: str,
    attachment_mime_type: str | None,
    attachment_file_size: int,
    attachment_created_by: str,
    attachment_created_at: str,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO attachments (
                attachment_uid, entry_id, attachment_original_filename,
                attachment_stored_filename, attachment_relative_path,
                attachment_mime_type, attachment_file_size,
                attachment_created_by, attachment_created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attachment_uid,
                entry_id,
                attachment_original_filename,
                attachment_stored_filename,
                attachment_relative_path,
                attachment_mime_type,
                attachment_file_size,
                attachment_created_by,
                attachment_created_at,
            ),
        )


def delete_attachment_by_uid_for_entry(entry_id: int, attachment_uid: str) -> sqlite3.Row | None:
    with get_connection() as conn:
        attachment = conn.execute(
            """
            SELECT id, attachment_uid, entry_id, attachment_original_filename,
                   attachment_relative_path, attachment_mime_type
            FROM attachments
            WHERE entry_id = ? AND attachment_uid = ?
            """,
            (entry_id, attachment_uid),
        ).fetchone()
        if attachment is None:
            return None

        conn.execute(
            "DELETE FROM attachments WHERE id = ?",
            (attachment["id"],),
        )
        return attachment
