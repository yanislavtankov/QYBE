from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass

SCIM_TOKEN_PREFIX = "scim_"


@dataclass(slots=True)
class ScimAuthError(Exception):
    detail: str
    status_code: int = 401


def _hash_scim_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_scim_token() -> tuple[str, str, str]:
    raw_token = f"{SCIM_TOKEN_PREFIX}{secrets.token_urlsafe(32)}"
    hashed_token = _hash_scim_token(raw_token)
    display_token = f"{SCIM_TOKEN_PREFIX}****{raw_token[-4:]}"
    return raw_token, hashed_token, display_token


def verify_scim_token(request, dal):
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise ScimAuthError("Missing SCIM authorization header")

    token_type, _, raw_token = authorization.partition(" ")
    if token_type != "Bearer" or not raw_token.startswith(SCIM_TOKEN_PREFIX):
        raise ScimAuthError("Invalid SCIM authorization header")

    token_hash = _hash_scim_token(raw_token)
    token = dal.get_token_by_hash(token_hash)
    if token is None:
        raise ScimAuthError("Invalid SCIM token")
    if not getattr(token, "is_active", False):
        raise ScimAuthError("SCIM token has been revoked")

    return token
