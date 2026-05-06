from pathlib import Path
import json


# Scopes requested: read-only access to Drive files and Sheets data
DEFAULT_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_google_credentials(
    credentials_file: Path,
    token_file: Path | None = None,
    scopes: list[str] | None = None,
):
    # Loads Google credentials from either a Service Account key file or an OAuth client config + token.json
    scopes = scopes or DEFAULT_GOOGLE_SCOPES

    credentials_payload = json.loads(credentials_file.read_text(encoding="utf-8"))

    if _is_service_account_credentials(credentials_payload):
        from google.oauth2 import service_account

        return service_account.Credentials.from_service_account_file(
            str(credentials_file), scopes=scopes
        )

    if _is_installed_app_credentials(credentials_payload):
        return _load_oauth_credentials(credentials_file, token_file, scopes)

    raise ValueError(
        "Unsupported Google credentials format. Expected a Service Account key or an installed-app OAuth client file."
    )


def _is_service_account_credentials(payload: dict) -> bool:
    return payload.get("type") == "service_account"


def _is_installed_app_credentials(payload: dict) -> bool:
    return "installed" in payload or "web" in payload


def _load_oauth_credentials(
    credentials_file: Path,
    token_file: Path | None,
    scopes: list[str],
):
    from google.auth.transport.requests import Request
    from google.auth.exceptions import RefreshError
    from google.oauth2.credentials import Credentials

    if token_file is None or not token_file.exists():
        raise FileNotFoundError(
            "token.json not found for OAuth credentials. Generate it first or provide a valid token file."
        )

    creds = Credentials.from_authorized_user_file(str(token_file), scopes=scopes)

    if creds.valid:
        return creds

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            token_file.write_text(creds.to_json(), encoding="utf-8")
            return creds
        except RefreshError as exc:
            raise ValueError(
                f"OAuth token is invalid or expired and cannot be refreshed. Re-authenticate using {credentials_file.name}."
            ) from exc

    raise ValueError(
        f"OAuth token is invalid or expired and cannot be refreshed. Re-authenticate using {credentials_file.name}."
    )


def build_drive_service(credentials_file: Path, token_file: Path | None = None):
    # Builds an authenticated Google Drive API v3 client using Service Account credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file, token_file=token_file)
    return build("drive", "v3", credentials=creds)


def build_sheets_service(credentials_file: Path, token_file: Path | None = None):
    # Builds an authenticated Google Sheets API v4 client using Service Account credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file, token_file=token_file)
    return build("sheets", "v4", credentials=creds)


def reauthorize_google_oauth(
    credentials_file: Path,
    token_file: Path,
    scopes: list[str] | None = None,
):
    scopes = scopes or DEFAULT_GOOGLE_SCOPES

    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), scopes=scopes)
    creds = flow.run_local_server(port=0)
    token_file.write_text(creds.to_json(), encoding="utf-8")
    return creds


if __name__ == "__main__":
    # Standalone auth helper: reads credential paths from .env and triggers the OAuth browser flow
    # Run from the project root: python -m carlo_bot.infrastructure.google.auth
    from carlo_bot.infrastructure.config import load_config
    from carlo_bot.bootstrap.runtime import get_project_root

    _config = load_config()
    _project_root = get_project_root()
    _credentials_file = _project_root / _config.google_credentials_file
    _token_file = _project_root / _config.google_token_file

    print(f"Using credentials: {_credentials_file}")
    print(f"Token will be saved to: {_token_file}")

    _payload = json.loads(_credentials_file.read_text(encoding="utf-8"))
    if _is_installed_app_credentials(_payload):
        reauthorize_google_oauth(_credentials_file, _token_file)
        print("OAuth authentication successful. token.json has been refreshed.")
    else:
        get_google_credentials(_credentials_file, _token_file)
        print("Authentication successful.")