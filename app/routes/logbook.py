from urllib.parse import urlencode

from fastapi import APIRouter, Request

from app.db.attachments import list_attachments_for_entry_ids
from app.db.entries import count_logbook_entries, list_logbook_entries
from app.db.labels import list_labels_for_entry_ids
from app.routes import path_for, render_template
from app.runtime import APP_COOKIE_PATH

router = APIRouter()

PAGE_SIZE = 25


@router.get("/logbook")
def logbook_page(request: Request, page: int = 1, show_archived: int | None = None, q: str = ""):
    query_has_preference = "show_archived" in request.query_params
    if query_has_preference:
        include_archived = show_archived == 1
    else:
        include_archived = request.cookies.get("show_archived_vendors") == "1"

    current_q = q.strip()
    search_text = current_q or None

    current_page = max(1, int(page))
    total_entries = count_logbook_entries(
        include_archived_vendors=include_archived,
        search_text=search_text,
    )
    if total_entries > 0:
        total_pages = (total_entries + PAGE_SIZE - 1) // PAGE_SIZE
        current_page = min(current_page, total_pages)

    entries = list_logbook_entries(
        current_page,
        page_size=PAGE_SIZE,
        include_archived_vendors=include_archived,
        search_text=search_text,
    )

    entry_edit_return_target = path_for(request, "logbook_page")
    return_query_params: dict[str, str] = {}
    if current_page > 1:
        return_query_params["page"] = str(current_page)
    if include_archived:
        return_query_params["show_archived"] = "1"
    if current_q:
        return_query_params["q"] = current_q
    if return_query_params:
        entry_edit_return_target = f"{entry_edit_return_target}?{urlencode(return_query_params)}"

    entry_ids = [int(entry["id"]) for entry in entries]

    attachments_by_entry: dict[int, list] = {}
    for attachment in list_attachments_for_entry_ids(entry_ids):
        attachments_by_entry.setdefault(int(attachment["entry_id"]), []).append(attachment)

    labels_by_entry: dict[int, list] = {}
    for label in list_labels_for_entry_ids(entry_ids):
        labels_by_entry.setdefault(int(label["entry_id"]), []).append(label)

    has_prev = current_page > 1
    has_next = current_page * PAGE_SIZE < total_entries

    response = render_template(
        request,
        "logbook.html",
        {
            "breadcrumbs": [
                {"label": "Home", "url": path_for(request, "read_root")},
                {"label": "Logbook", "url": None},
            ],
            "entries": entries,
            "attachments_by_entry": attachments_by_entry,
            "labels_by_entry": labels_by_entry,
            "page": current_page,
            "has_prev": has_prev,
            "has_next": has_next,
            "show_archived": include_archived,
            "q": current_q,
            "entry_edit_return_target": entry_edit_return_target,
        },
    )

    if query_has_preference:
        response.set_cookie(
            key="show_archived_vendors",
            value="1" if include_archived else "0",
            max_age=60 * 60 * 24 * 365,
            path=APP_COOKIE_PATH,
            samesite="lax",
            httponly=True,
        )

    return response
