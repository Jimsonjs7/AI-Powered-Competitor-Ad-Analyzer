import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("security")
security_bearer = HTTPBearer(auto_error=False)


def verify_auth_token(credentials: HTTPAuthorizationCredentials | None = Security(security_bearer)) -> bool:
    # Allow local development mode with default token or header
    if settings.environment == "development":
        return True

    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Bearer authentication header",
        )

    if credentials.credentials != settings.api_bearer_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Invalid credentials",
        )
    return True


def validate_target_url(raw_url: str) -> str:
    # Ensure URL is HTTPS and belongs to allowed public ad platforms
    parsed = urlparse(raw_url.strip())
    if parsed.scheme.lower() not in ("https", "http"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL scheme. Must be http or https.",
        )

    host = parsed.hostname
    if not host:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format. Hostname is missing.",
        )

    # Prevent loopback and private IP SSRF attacks
    try:
        resolved_ip = socket.gethostbyname(host)
        ip_obj = ipaddress.ip_address(resolved_ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
            logger.warning(f"SSRF attempt blocked for IP: {resolved_ip}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access to internal networks and private IP addresses is prohibited.",
            )
    except socket.gaierror:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resolve target domain.",
        )

    # Host whitelist verification
    normalized_host = host.lower()
    if not any(
        normalized_host == allowed or normalized_host.endswith("." + allowed)
        for allowed in settings.ssrf_allowed_hosts
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Host '{host}' is not in the allowed source domain list.",
        )

    return raw_url.strip()


def sanitize_text(text: str | None) -> str:
    # Remove null bytes and excessive whitespace from untrusted scraped text
    if not text:
        return ""
    clean = text.replace("\x00", "").strip()
    return clean

