from __future__ import annotations

import hashlib
import hmac
from urllib.parse import urlencode


def sign_params(params: dict[str, str], secret: str) -> str:
    """Return query string with HMAC SHA256 signature."""
    if not secret:
        raise ValueError("secret required")
    query = urlencode(sorted(params.items()))
    signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    return f"{query}&signature={signature}"
