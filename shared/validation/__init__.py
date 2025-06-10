from __future__ import annotations

"""Unified input validation utilities."""

import json
from html import escape
from importlib import resources
from typing import Any, Dict

from jsonschema import ValidationError, validate


class InputValidationError(Exception):
    """Raised when input validation fails."""


def _load_schema(name: str) -> Dict[str, Any]:
    with resources.files('shared.schemas').joinpath(f"{name}.json").open() as f:
        return json.load(f)


def validate_schema(payload: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
    """Validate and sanitize payload against schema."""
    schema = _load_schema(schema_name)
    try:
        validate(payload, schema)
    except ValidationError as exc:
        raise InputValidationError(str(exc)) from exc
    return {k: escape(str(v)) if isinstance(v, str) else v for k, v in payload.items()}
