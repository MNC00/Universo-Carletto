from html import escape


def build_subject() -> str:
    # Returns the fixed email subject line used for every message
    return "Il buongiorno che non ti meriti ma di cui hai bisogno!"


def _validate_quote(quote: str) -> None:
    # Guards against empty or whitespace-only quotes before they are embedded in email bodies
    if not quote or not quote.strip():
        raise ValueError("Quote cannot be empty.")


def _build_greeting(recipient_name: str | None) -> str:
    if recipient_name is None:
        return "Buongiorno!"

    normalized_name = recipient_name.strip()
    if not normalized_name:
        return "Buongiorno!"

    return f"Buongiorno {normalized_name}!"


def _build_plain_unsubscribe_footer(unsubscribe_url: str | None) -> str:
    if unsubscribe_url is None:
        return ""

    return (
        "\n\n"
        "Per non ricevere piu questa mail, usa questo link:\n"
        f"{unsubscribe_url}"
    )


def _build_html_unsubscribe_footer(unsubscribe_url: str | None) -> str:
    if unsubscribe_url is None:
        return ""

    safe_url = escape(unsubscribe_url.strip(), quote=True)
    return (
        "\n        <hr>\n"
        "        <p style=\"font-size: 0.9em;\">"
        "Se vuoi disiscriverti, "
        f"<a href=\"{safe_url}\">clicca qui</a>."
        "</p>"
    )


def build_plain_body(
    quote: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
) -> str:
    # Assembles the plain-text email body by combining quote, saint name, and blasfemia into a template
    _validate_quote(quote)
    greeting = _build_greeting(recipient_name)

    return (
        f"{greeting}\n\n"
        f'Tieni ben a mente che:\n"{quote}"\n\n'
        "Passa una buona giornata,\n"
        f"{saint.capitalize()} {blasfemia}\n\n"
        "Carlo"
        f"{_build_plain_unsubscribe_footer(unsubscribe_url)}"
    )


def build_html_body(
    quote: str,
    saint: str,
    blasfemia: str,
    recipient_name: str | None = None,
    unsubscribe_url: str | None = None,
) -> str:
    # Assembles the HTML email body; HTML-escapes all dynamic content to prevent injection
    _validate_quote(quote)

    greeting = escape(_build_greeting(recipient_name))
    safe_quote = escape(quote.strip())
    safe_saint = escape(saint.strip().capitalize())
    safe_blasfemia = escape(blasfemia.strip())

    # References the inline photo via the Content-ID "carlo_photo" set by the email builder
    return f"""
    <html>
      <body>
        <p>{greeting}</p>
        <p>Tieni ben a mente che:<br><strong>\"{safe_quote}\"</strong></p>
        <p>
          <img src=\"cid:carlo_photo\" alt=\"Foto di Carlo\" style=\"max-width: 300px; height: auto;\">
        </p>
        <p>
          Passa una buona giornata,<br>
          <strong>{safe_saint.capitalize()} {safe_blasfemia}</strong>
        </p>
        <p>Carlo</p>
        {_build_html_unsubscribe_footer(unsubscribe_url)}
      </body>
    </html>
    """.strip()
