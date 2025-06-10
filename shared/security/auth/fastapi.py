from __future__ import annotations

"""FastAPI authentication middleware."""

from typing import Any, Callable, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from .jwt import AuthError, SERVICE_NAME, validate_token


class AuthMiddleware:
    """Validate JWT in Authorization header."""

    def __init__(self, app: Callable) -> None:
        self.app = app

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        auth = request.headers.get("authorization", "")
        token = auth.replace("Bearer ", "")
        try:
            validate_token(token, request.app.state.service_name)
        except AuthError as exc:
            res = JSONResponse({"detail": str(exc)}, status_code=401)
            await res(scope, receive, send)
            return
        await self.app(scope, receive, send)
