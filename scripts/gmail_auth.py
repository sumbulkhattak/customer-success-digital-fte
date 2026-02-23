"""Gmail OAuth2 authorization flow.

Run this script to authorize the app with your Gmail account.
It will open a browser window for you to sign in and grant permissions.
The resulting token will be saved to credentials/gmail_token.json.
"""

import os
import json
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_SECRET_FILE = os.path.join(PROJECT_ROOT, "credentials", "gmail.json")
TOKEN_FILE = os.path.join(PROJECT_ROOT, "credentials", "gmail_token.json")


def main():
    creds = None

    # Check for existing token
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"ERROR: Client secret file not found at {CLIENT_SECRET_FILE}")
                print("Download it from Google Cloud Console > APIs & Services > Credentials")
                sys.exit(1)

            print("Opening browser for Gmail authorization...")
            print("Sign in with your Google account and grant permissions.\n")

            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8090)

        # Save the token
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        print(f"\nToken saved to: {TOKEN_FILE}")

    print("\nGmail authorization successful!")
    print(f"  Email scopes: {', '.join(SCOPES)}")
    print(f"  Token file: {TOKEN_FILE}")
    print("\nUpdate your .env file:")
    print(f"  GMAIL_CREDENTIALS_PATH={TOKEN_FILE}")


if __name__ == "__main__":
    main()
