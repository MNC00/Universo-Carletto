import pytest

from carlo_bot.infrastructure.unsubscribe import (
    build_unsubscribe_signature,
    build_unsubscribe_url,
    normalize_unsubscribe_email,
)


def test_normalize_unsubscribe_email_trims_and_lowercases():
    assert normalize_unsubscribe_email("  Alice@Example.com  ") == "alice@example.com"


def test_normalize_unsubscribe_email_raises_for_empty_value():
    with pytest.raises(ValueError, match="Email cannot be empty"):
        normalize_unsubscribe_email("   ")


def test_build_unsubscribe_signature_is_deterministic():
    result = build_unsubscribe_signature("Alice@Example.com", "super-secret")

    assert result == "8cyn6OQV5khgX4n8LJMoN73cPRx1qqcfEOs1Wx3CnQQ"


def test_build_unsubscribe_url_encodes_email_and_signature():
    result = build_unsubscribe_url("https://example.com/unsubscribe", "Alice@Example.com", "super-secret")

    assert result.startswith("https://example.com/unsubscribe?email=alice%40example.com&sig=")


def test_build_unsubscribe_url_appends_to_existing_query_string():
    result = build_unsubscribe_url("https://example.com/unsubscribe?source=bot", "Alice@Example.com", "super-secret")

    assert result.startswith("https://example.com/unsubscribe?source=bot&email=alice%40example.com&sig=")