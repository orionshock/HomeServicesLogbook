# Home Services Logbook - MVP Scope

## Purpose

Defines the minimum viable product scope for the project.

Core concept: Vendor → Entries → Attachments

## Core Features

- Vendor management (create, edit, archive)
- Entry logbook (create, edit)
- File attachments (upload and download)
- Vendor timeline / history view
- Simple calendar export (`.ics` download)
- Custom error pages (404, general error)
- Actor metadata on all records (`created_by`, `updated_by`)

## Out of Scope

- tagging systems
- full-text search
- authentication / multi-user support
- Home Assistant integration
- mobile apps
- analytics dashboards
- calendar sync (read-back from external calendars)
- revision history / audit log

## Success Criteria

Users can:
1. Create a vendor and fill in reference details
2. Write notes about interactions as logbook entries
3. Upload documents and download them by attachment UID
4. Review the full history timeline for any vendor
5. Edit a vendor's reference data or an existing entry
6. Archive a vendor they no longer actively use
7. Export a calendar reminder as a downloadable `.ics` file

