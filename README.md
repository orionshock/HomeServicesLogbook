
# Home Services Logbook

A simple self‑hosted web application for tracking the companies and people who service your home.

Think of it as a **digital household logbook + filing cabinet** for things like:

- ISP support calls
- utility account information
- HVAC service visits
- plumbing repairs
- contractor estimates
- invoices and work orders
- maintenance history for the house

Instead of scattered notes, emails, PDFs, and photos, everything is stored in **one timeline organized by vendor**.

---

# Why This Exists

Many people end up with important home service information spread across:

- email inboxes
- phone notes
- screenshots
- downloads folders
- paper folders

Home Services Logbook provides a structured place to keep:

Vendor → Interaction history → Documents

This makes it easy to answer questions like:

- When was the HVAC last serviced?
- What was the work order number for that repair?
- Which company installed the water heater?
- What did the ISP support rep say last time I called?

---

# Core Concept

The system revolves around three simple objects.

## Vendors

A vendor is any person or company that services your home.

Examples:

- Internet provider
- electric utility
- water utility
- HVAC contractor
- plumber
- electrician
- appliance repair company
- insurance provider
- landscaper

Each vendor has a **reference page** with useful information such as:

- account numbers
- contact numbers
- portal URLs
- support PINs
- service location
- general notes

## Entries

Entries form the **logbook timeline** for a vendor.

Examples:

- support call notes
- technician visits
- billing issues
- document uploads
- estimates
- repairs

Entries are chronological and behave like a logbook.

The interface encourages **adding new entries rather than rewriting old history**.

## Attachments

Entries can include uploaded documents such as:

- invoices
- work orders
- PDFs
- photos
- estimates
- manuals

Files are stored on disk and linked to entries in the database.

---

# Features

Current design goals include:

- Vendor reference pages
- Chronological vendor history timeline
- Freeform logbook entries
- File attachments (PDFs, images, documents)
- Simple calendar export via `.ics`
- Local-first architecture
- Minimal dependencies
- Easy self-hosting

The system is intentionally **simple and utilitarian**.

---

# Technology Stack

The project uses a lightweight stack designed for maintainability.

Backend

- Python
- FastAPI

Templating

- Jinja

Database

- SQLite

Storage

- Local filesystem for uploaded files

This avoids heavy frontend frameworks or complicated infrastructure.

---

# Architecture Philosophy

The system is intentionally designed to stay small and understandable.

Guiding principles:

- prefer simple code
- avoid unnecessary abstractions
- minimize dependencies
- keep architecture local-first
- favor server-rendered pages
- keep the schema easy to understand

The application structure roughly follows:

Vendor → Entries → Attachments

---

# Example Workflow

A typical use case might look like:

1. Open the vendor page for your ISP.
2. Write a note about a support call.
3. Add the case number provided by the support rep.
4. Attach a screenshot of the bill.
5. Save the entry.

Later you can open the vendor page and instantly see the entire history of interactions.

---

# Example Use Cases

Internet outage support call

```
Vendor: ISP

Entry:
Called technical support regarding outage.
Rep: Michael
Case number: 483920
Said issue is neighborhood node failure.
Expected resolution: tomorrow morning.
```

HVAC service visit

```
Vendor: Desert Air HVAC

Entry:
Technician replaced AC capacitor.
Tech: Carlos
Invoice: $285
System running normally.
```

Document upload

```
Vendor: City Water

Entry:
Uploaded June bill.
```

---

# Project Status

This project is currently in early development.

Initial focus:

- vendor management
- logbook entries
- attachments
- timeline interface

Advanced features such as tagging, search, and integrations will be considered later.

---

# Future Ideas

Possible future features:

- entry labels/tags
- search
- vendor categories
- Home Assistant integration
- revision history

---

# License

This project is open source.  
License to be determined.

---

# Contributing

Contributions and ideas are welcome.

If contributing:

- keep the code simple
- avoid unnecessary dependencies
- follow the coding-style guide in `docs/`
