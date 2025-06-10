from __future__ import annotations

"""FastAPI validation middleware."""

import os
from typing import Any, Callable, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from . import InputValidationError, validate_schema

MAX_BODY_SIZE = int(os.getenv("MAX_REQUEST_SIZE", "1048576"))  # 1MB


class ValidationMiddleware:
    def __init__(self, app: Callable, schemas: Dict[str, str]) -> None:
        self.app = app
        self.schemas = schemas

    async def _reject(self, scope: Dict[str, Any], receive: Callable, send: Callable, msg: str, code: int) -> None:
        res = JSONResponse({"detail": msg}, status_code=code)
        await res(scope, receive, send)

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        if request.headers.get("content-type") != "application/json":
            await self._reject(scope, receive, send, "unsupported content type", 415)
            return
        body = await request.body()
        if len(body) > MAX_BODY_SIZE:
            await self._reject(scope, receive, send, "request too large", 413)
            return
        schema_name = self.schemas.get(scope["path"])
        if schema_name:
            try:
                data = await request.json()
            except Exception:
                await self._reject(scope, receive, send, "invalid json", 400)
                return
            try:
                scope["state"] = {"validated": validate_schema(data, schema_name)}
            except InputValidationError as exc:
                await self._reject(scope, receive, send, str(exc), 400)
                return
        await self.app(scope, receive, send)
