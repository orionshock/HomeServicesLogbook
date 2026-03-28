from fastapi import APIRouter, Request

from app.runtime import resolve_effective_root_path

router = APIRouter()


@router.get("/__debug/scope", name="debug_scope")
async def debug_scope(request: Request):
    interesting = {
        key: value
        for key, value in request.scope.items()
        if key in {"type", "root_path", "path", "scheme", "server", "client"}
    }

    headers = {
        key.decode("latin-1"): value.decode("latin-1")
        for key, value in request.scope.get("headers", [])
        if key.decode("latin-1").lower()
        in {
            "host",
            "x-forwarded-for",
            "x-forwarded-proto",
            "x-forwarded-host",
            "x-forwarded-prefix",
            "x-ingress-path",
        }
    }

    effective_root_path = getattr(request.state, "effective_root_path", None)
    if effective_root_path is None:
        effective_root_path = resolve_effective_root_path(request.headers)

    return {
        "scope": interesting,
        "headers": headers,
        "url": str(request.url),
        "base_url": str(request.base_url),
        "app_root_path": request.app.root_path,
        "effective_root_path": effective_root_path,
    }