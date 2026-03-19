from pathlib import Path
import os
from urllib.parse import urlparse

from fastapi import APIRouter, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent.parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
ACTOR_OVERRIDE_COOKIE = "actor_override"

router = APIRouter()

templates = Jinja2Templates(directory="templates")


def _normalize_actor_value(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _is_truthy_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _trust_upstream_auth() -> bool:
    return _is_truthy_env(os.getenv("TRUST_UPSTREAM_AUTH", "false"))


def _upstream_actor_header_name() -> str:
    return os.getenv("UPSTREAM_ACTOR_HEADER", "X-Remote-User")


def _read_upstream_actor(request: Request) -> str | None:
    if not _trust_upstream_auth():
        return None

    header_name = _upstream_actor_header_name()
    if not header_name:
        return None

    return _normalize_actor_value(request.headers.get(header_name))


def _resolve_current_actor(request: Request) -> dict[str, str | None]:
    override_actor = _normalize_actor_value(request.cookies.get(ACTOR_OVERRIDE_COOKIE))
    return _resolve_actor_with_override(request, override_actor)


def _resolve_actor_with_override(request: Request, override_actor: str | None) -> dict[str, str | None]:
    upstream_actor = _read_upstream_actor(request)

    if override_actor:
        actor_id = override_actor
        source = "override"
    elif upstream_actor:
        actor_id = upstream_actor
        source = "upstream"
    else:
        actor_id = "user"
        source = "default"

    return {
        "actor_id": actor_id,
        "display_name": actor_id,
        "source": source,
        "upstream_actor": upstream_actor,
    }


def _is_async_request(request: Request) -> bool:
    requested_with = (request.headers.get("x-requested-with") or "").strip().lower()
    accept = (request.headers.get("accept") or "").lower()
    return requested_with == "fetch" or "application/json" in accept


def _actor_json_payload(actor: dict[str, str | None]) -> dict[str, object]:
    return {
        "ok": True,
        "current_actor": {
            "actor_id": actor["actor_id"],
            "display_name": actor["display_name"],
            "source": actor["source"],
        },
    }


def _redirect_target(request: Request) -> str:
    referer = request.headers.get("referer")
    if referer:
        parsed = urlparse(referer)
        if not parsed.netloc or parsed.netloc == request.url.netloc:
            path = parsed.path or "/"
            if parsed.query:
                path = f"{path}?{parsed.query}"
            return path
    return "/"


@router.post("/actor/set")
async def set_actor_override(request: Request, actor_id: str = Form("")):
    normalized_actor = _normalize_actor_value(actor_id)

    if _is_async_request(request):
        if normalized_actor:
            actor = _resolve_actor_with_override(request, normalized_actor)
        else:
            actor = _resolve_current_actor(request)

        response = JSONResponse(_actor_json_payload(actor))

        if normalized_actor:
            response.set_cookie(
                ACTOR_OVERRIDE_COOKIE,
                normalized_actor,
                path="/",
                httponly=True,
                samesite="lax",
            )

        return response

    response = RedirectResponse(url=_redirect_target(request), status_code=303)

    if normalized_actor:
        response.set_cookie(
            ACTOR_OVERRIDE_COOKIE,
            normalized_actor,
            path="/",
            httponly=True,
            samesite="lax",
        )

    return response


@router.post("/actor/reset")
async def reset_actor_override(request: Request):
    if _is_async_request(request):
        actor = _resolve_actor_with_override(request, None)
        response = JSONResponse(_actor_json_payload(actor))
        response.delete_cookie(ACTOR_OVERRIDE_COOKIE, path="/")
        return response

    response = RedirectResponse(url=_redirect_target(request), status_code=303)
    response.delete_cookie(ACTOR_OVERRIDE_COOKIE, path="/")
    return response


def render_template(request: Request, template_name: str, context: dict | None = None):
    payload = {
        "request": request,
        "current_actor": getattr(request.state, "current_actor", _resolve_current_actor(request)),
    }
    if context:
        payload.update(context)
    return templates.TemplateResponse(template_name, payload)
