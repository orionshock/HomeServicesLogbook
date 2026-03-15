# Home Services Logbook - Post-MVP Backlog

These ideas were intentionally deferred from the MVP. They are captured here to avoid scope creep during initial development. None of these should be implemented until the MVP is stable and the need is confirmed.

---

## UX / Entry Experience

- **Entry labels / tags** — Tag entries with categories like `billing`, `repair`, `support-call`, `estimate`
- **Vendor notes field** — A dedicated freeform notes/memo section separate from the entry timeline (already has `vendor_notes` column, not surfaced in UI yet)
- **Entry type refinement** — Surface `vendor_reference` (case/work order) and `rep_name` fields in the entry form
- **Inline attachment preview** — Show image thumbnails or PDF icons inline in the timeline
- **Rich timestamps** — Show relative time (e.g., "3 months ago") alongside the UTC timestamp

---

## Search & Discovery

- **Vendor search / filter** — Filter vendors by category or name on the vendors list
- **Full-text search** — Search across all entry body text
- **Timeline filter** — Filter a vendor's timeline by entry type or date range

---

## Editing & History

- **Entry revision history** — Preserve previous versions of edited entries
- **Soft-delete entries** — Archive individual entries rather than deleting them

---

## File Handling

- **File type restrictions** — Whitelist allowed MIME types server-side
- **Attachment description** — Allow a short caption/description per attachment
- **Bulk upload** — Upload multiple files at once per entry

---

## Calendar

- **Calendar event history** — Persist generated calendar events alongside the entry that triggered them
- **Recurring service reminders** — Create entries or calendar events on a schedule

---

## Infrastructure & Deployment

- **Home Assistant add-on packaging** — Containerize and expose as an HA add-on
- **Configurable upload directory** — Set via environment variable
- **Backup / export** — Export all vendor data and attachments as a ZIP
- **Real authentication** — Token-based or HA identity header verification
- **Multi-user support** — Separate views per household member

---

## Data Integrity

- **SHA-256 checksum verification at download** — Verify stored file integrity before serving
- **Database export** — Dump to JSON or CSV for portability

---

## Developer / Ops

- **Structured logging** — Replace print/log to structured JSON log output
- **Health check endpoint** — `GET /healthz` returning `{"status": "ok"}`
- **Database migration support** — Add lightweight migration system for schema changes
