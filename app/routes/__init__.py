from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

templates = Jinja2Templates(directory="templates")


def _resolve_current_actor(_request: Request) -> dict[str, str]:
    # Temporary development actor resolution. Replace with real auth integration later.
    return {
        "actor_id": "devUser",
        "display_name": "devUser",
        "source": "hardcoded",
    }


def render_template(request: Request, template_name: str, context: dict | None = None):
    payload = {
        "request": request,
        "current_actor": getattr(request.state, "current_actor", _resolve_current_actor(request)),
    }
    if context:
        payload.update(context)
    return templates.TemplateResponse(template_name, payload)
