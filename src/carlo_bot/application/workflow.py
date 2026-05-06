from carlo_bot.domain.composer import build_html_body, build_plain_body, build_subject
from carlo_bot.bootstrap.runtime import get_project_root
from carlo_bot.domain.picker import (
    pick_active_contacts,
    pick_random_blasfemia,
    pick_random_photo,
    pick_random_quote,
    pick_random_saint,
)
from carlo_bot.infrastructure.config import AppConfig
from carlo_bot.infrastructure.email.builder import build_email_message
from carlo_bot.infrastructure.email.sender import send_email
from carlo_bot.infrastructure.storage import build_storage_provider
from carlo_bot.infrastructure.unsubscribe import build_unsubscribe_url


def run_workflow(config: AppConfig, dry_run: bool) -> None:
    # Instantiates the storage provider (filesystem or Google Workspace) based on STORAGE_BACKEND
    project_root = get_project_root()
    storage_provider = build_storage_provider(config=config, project_root=project_root)

    # Loads all datasets from the configured backend in one pass
    contacts = storage_provider.load_contacts()
    quotes = storage_provider.load_quotes()
    photo_assets = storage_provider.load_photo_assets()
    saints = storage_provider.load_saints()
    blasfemie = storage_provider.load_blasfemie()

    # Filters contacts to active-only and picks one random item from each content dataset
    active_contacts = pick_active_contacts(contacts)
    selected_quote = pick_random_quote(quotes)
    selected_photo = pick_random_photo(photo_assets)
    selected_saint = pick_random_saint(saints)
    selected_blasfemia = pick_random_blasfemia(blasfemie)

    # Builds the shared email subject from the selected content
    subject = build_subject()
    recipients = [contact["email"] for contact in active_contacts]

    # Prints a structured summary of configuration, loaded data, selections, and email details
    print("=== Configuration ===")
    print(f"Environment: {config.app_env}")
    print(f"Dry run: {dry_run}")

    print("\n=== Loading summary ===")
    print(f"Contacts loaded: {len(contacts)}")
    print(f"Active contacts: {len(active_contacts)}")
    print(f"Quotes loaded: {len(quotes)}")
    print(f"Photos loaded: {len(photo_assets)}")

    print("\n=== Selection result ===")
    print(f"Selected quote: {selected_quote}")
    print(f"Selected saint: {selected_saint}")
    print(f"Selected blasfemia: {selected_blasfemia}")
    print(f"Selected photo: {selected_photo.name}")

    print("\n=== Composed email ===")
    print(f"Subject: {subject}")
    print(f"Recipients: {recipients}")
    print(f"Inline image: {selected_photo.name}")

    print("\n=== Delivery ===")

    # Builds one message per recipient so later steps can customize content safely per contact
    for recipient in recipients:
        unsubscribe_url = _build_recipient_unsubscribe_url(config, recipient)
        plain_body = build_plain_body(
            selected_quote,
            selected_saint,
            selected_blasfemia,
            unsubscribe_url=unsubscribe_url,
        )
        html_body = build_html_body(
            selected_quote,
            selected_saint,
            selected_blasfemia,
            unsubscribe_url=unsubscribe_url,
        )
        message = build_email_message(
            sender=config.smtp_sender,
            recipients=[recipient],
            subject=subject,
            plain_body=plain_body,
            html_body=html_body,
            image_asset=selected_photo,
        )

        if dry_run:
            print(f"Prepared email for: {recipient}")
            continue

        send_email(config, message)
        print(f"Email sent to: {recipient}")

    if dry_run:
        print("\nDRY_RUN enabled: emails not sent.")
        return

    print("\nEmail sent successfully.")


def _build_recipient_unsubscribe_url(config: AppConfig, recipient: str) -> str | None:
    if config.unsubscribe_base_url is None or config.unsubscribe_secret is None:
        return None

    return build_unsubscribe_url(config.unsubscribe_base_url, recipient, config.unsubscribe_secret)
