from pathlib import Path


# Scopes requested: read-only access to Drive files and Sheets data
DEFAULT_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
]


def get_google_credentials(
    credentials_file: Path,
    token_file: Path | None = None,  # kept for backwards compatibility, unused with Service Account
    scopes: list[str] | None = None,
):
    # Loads Service Account credentials from the JSON key file; no token refresh needed
    scopes = scopes or DEFAULT_GOOGLE_SCOPES

    from google.oauth2 import service_account

    return service_account.Credentials.from_service_account_file(
        str(credentials_file), scopes=scopes
    )


def build_drive_service(credentials_file: Path, token_file: Path | None = None):
    # Builds an authenticated Google Drive API v3 client using Service Account credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file)
    return build("drive", "v3", credentials=creds)


def build_sheets_service(credentials_file: Path, token_file: Path | None = None):
    # Builds an authenticated Google Sheets API v4 client using Service Account credentials
    from googleapiclient.discovery import build

    creds = get_google_credentials(credentials_file=credentials_file)
    return build("sheets", "v4", credentials=creds)


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
    get_google_credentials(_credentials_file, _token_file)
    print("Authentication successful. token.json has been saved.")