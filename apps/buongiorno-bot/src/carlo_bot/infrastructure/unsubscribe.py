import base64
import hashlib
import hmac
from urllib.parse import urlencode


def normalize_unsubscribe_email(email: str) -> str:
    normalized = email.strip().lower()

    if not normalized:
        raise ValueError("Email cannot be empty.")

    return normalized


def build_unsubscribe_signature(email: str, secret: str) -> str:
    normalized_email = normalize_unsubscribe_email(email)

    if not secret.strip():
        raise ValueError("Secret cannot be empty.")

    digest = hmac.new(
        secret.encode("utf-8"),
        normalized_email.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")


def build_unsubscribe_url(base_url: str, email: str, secret: str) -> str:
    normalized_base_url = base_url.strip()
    if not normalized_base_url:
        raise ValueError("Base URL cannot be empty.")

    normalized_email = normalize_unsubscribe_email(email)
    signature = build_unsubscribe_signature(normalized_email, secret)
    separator = "&" if "?" in normalized_base_url else "?"

    return f"{normalized_base_url}{separator}{urlencode({'email': normalized_email, 'sig': signature})}"