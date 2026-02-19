# app/core/cache.py
import hashlib
from typing import Optional
from fastapi import Request, Response

def custom_key_builder(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    *args,
    **kwargs,
):
    """
    Standardizes the cache key based on the URL path, query params, AND the user's token.
    This ensures users do not see each other's cached private data.
    """
    auth_header = request.headers.get("Authorization", "no_auth")
    
    # Hash the token so we aren't storing raw JWTs in plain text in the Redis keys
    token_hash = hashlib.md5(auth_header.encode()).hexdigest()
    
    return f"{namespace}:{request.url.path}?{request.url.query}:u_{token_hash}"