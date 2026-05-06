import pytest

from carlo_bot.domain.composer import build_html_body, build_plain_body, build_subject


def test_build_subject_returns_expected_subject():
    result = build_subject()

    assert result == "Il buongiorno che non ti meriti ma di cui hai bisogno!"


def test_build_body_includes_quote():
    quote = "Oggi spacchi tutto."

    result = build_plain_body(quote, "San Gennaro", "culone")

    assert "Buongiorno!" in result
    assert "Tieni ben a mente che" in result
    assert quote in result


def test_build_body_raises_if_quote_is_empty():
    with pytest.raises(ValueError, match="Quote cannot be empty"):
        build_plain_body("", "San Gennaro", "culone")


def test_build_body_raises_if_quote_is_only_spaces():
    with pytest.raises(ValueError, match="Quote cannot be empty"):
        build_plain_body("   ", "San Gennaro", "culone")


def test_build_plain_body_includes_unsubscribe_footer_when_url_is_provided():
    unsubscribe_url = "https://example.com/unsubscribe?email=alice@example.com&sig=abc"

    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", unsubscribe_url=unsubscribe_url)

    assert "Per non ricevere piu questa mail" in result
    assert unsubscribe_url in result


def test_build_html_body_includes_unsubscribe_link_when_url_is_provided():
    unsubscribe_url = "https://example.com/unsubscribe?email=alice@example.com&sig=abc"

    result = build_html_body("Oggi spacchi tutto.", "San Gennaro", "culone", unsubscribe_url=unsubscribe_url)

    assert "clicca qui" in result
    assert "href=\"https://example.com/unsubscribe?email=alice@example.com&amp;sig=abc\"" in result


def test_build_plain_body_includes_recipient_name_when_provided():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice")

    assert result.startswith("Buongiorno Alice!")


def test_build_html_body_includes_recipient_name_when_provided():
    result = build_html_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="Alice")

    assert "<p>Buongiorno Alice!</p>" in result


def test_build_plain_body_falls_back_to_generic_greeting_for_blank_name():
    result = build_plain_body("Oggi spacchi tutto.", "San Gennaro", "culone", recipient_name="   ")

    assert result.startswith("Buongiorno!")
