import base64
from email.message import EmailMessage

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


class NotificationManager:
    """
    This class manages sending emails using Gmail API.

    Attributes:
        SCOPES (list): List of scopes for authorization flow.

    Methods:
        validate_text(text: str) -> bool: Validates input text before sending an email.
        send_email(self, text: str): Sends an email to specified recipients.
    """

    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

    @staticmethod
    def validate_text(text: str) -> bool:
        """
        Validate input text.

        Args:
            text (str): Text to be validated.

        Returns:
            bool: True if valid, False otherwise.
        """
        # Add your validation logic here, for example checking if text contains certain keywords or phrases.
        return True  # Replace this with actual validation.

    def get_credentials(self):
        """Get credentials from token.json file."""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        return creds

    def refresh_credentials(self, creds):
        """Refresh expired credentials."""
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("Credentials are not available")

    def save_credentials(self, creds):
        """Save refreshed credentials in token.json file."""
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    def send_email(self, text: str):
        """
        Send an email to specified recipients.

        Args:
            text (str): Body of the email.

        Returns:
            dict: Response from Gmail API containing message id.
        """
        try:
            service = build("gmail", "v1", credentials=self.get_credentials())

            message = EmailMessage()
            if not self.validate_text(text):
                raise ValueError("Invalid input")

            message.set_content(text)

            message["To"] = "adventistmany@gmail.com, viviana.eonv@gmail.com"
            message["From"] = "esanchezc.sqa@gmail.com"
            message["Subject"] = "New cheap flights found!"

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}

            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
        except Exception as e:
            print(f"An error occurred: {e}")
            send_message = None
        return send_message
