from typing import Any, Dict, Optional

from fastapi import Request


def extract_authorizer_claims(request: Request) -> Optional[Dict[str, Any]]:
    scope_data = request.scope.get("aws.event")
    if not isinstance(scope_data, dict):
        return None

    request_context = scope_data.get("requestContext")
    if not isinstance(request_context, dict):
        return None

    authorizer = request_context.get("authorizer")
    if not isinstance(authorizer, dict):
        return None

    claims = authorizer.get("claims")
    return claims if isinstance(claims, dict) else None
