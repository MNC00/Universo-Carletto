from types import SimpleNamespace

from carlo_bot.application.workflow import run_workflow
from carlo_bot.infrastructure.storage.models import PhotoAsset


class FakeStorageProvider:
    def load_contacts(self) -> list[dict]:
        return [
            {"name": "Alice", "email": "alice@example.com", "active": True},
            {"name": "Bob", "email": "bob@example.com", "active": True},
        ]

    def load_quotes(self) -> list[str]:
        return ["Quote of the day"]

    def load_photo_assets(self) -> list[PhotoAsset]:
        return [PhotoAsset(name="carlo.jpg", content_bytes=b"fake-image-bytes", mime_type="image/jpeg")]

    def load_saints(self) -> list[str]:
        return ["San Gennaro"]

    def load_blasfemie(self) -> list[str]:
        return ["culone"]


def test_run_workflow_sends_one_message_per_active_contact(monkeypatch):
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url="https://example.com/unsubscribe",
        unsubscribe_secret="super-secret",
    )
    built_messages: list[tuple[str, list[str]]] = []
    sent_recipients: list[str] = []

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_messages.append((sender, recipients, plain_body, html_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr(
        "carlo_bot.application.workflow.send_email",
        lambda config, message: sent_recipients.extend(message["recipients"]),
    )

    run_workflow(config=config, dry_run=False)

    assert built_messages[0][0:2] == ("bot@example.com", ["alice@example.com"])
    assert built_messages[1][0:2] == ("bot@example.com", ["bob@example.com"])
    assert "https://example.com/unsubscribe?email=alice%40example.com&sig=" in built_messages[0][2]
    assert "https://example.com/unsubscribe?email=bob%40example.com&sig=" in built_messages[1][2]
    assert "href=\"https://example.com/unsubscribe?email=alice%40example.com&amp;sig=" in built_messages[0][3]
    assert sent_recipients == ["alice@example.com", "bob@example.com"]


def test_run_workflow_dry_run_builds_one_message_per_active_contact_without_sending(monkeypatch):
    config = SimpleNamespace(
        app_env="test",
        smtp_sender="bot@example.com",
        unsubscribe_base_url=None,
        unsubscribe_secret=None,
    )
    built_recipients: list[tuple[list[str], str]] = []
    send_calls = 0

    monkeypatch.setattr(
        "carlo_bot.application.workflow.build_storage_provider",
        lambda config, project_root: FakeStorageProvider(),
    )

    def fake_build_email_message(*, sender, recipients, subject, plain_body, html_body, image_asset):
        built_recipients.append((recipients, plain_body))
        return {"sender": sender, "recipients": recipients, "subject": subject}

    def fake_send_email(config, message):
        nonlocal send_calls
        send_calls += 1

    monkeypatch.setattr("carlo_bot.application.workflow.build_email_message", fake_build_email_message)
    monkeypatch.setattr("carlo_bot.application.workflow.send_email", fake_send_email)

    run_workflow(config=config, dry_run=True)

    assert built_recipients == [(["alice@example.com"], built_recipients[0][1]), (["bob@example.com"], built_recipients[1][1])]
    assert "Per non ricevere piu questa mail" not in built_recipients[0][1]
    assert send_calls == 0