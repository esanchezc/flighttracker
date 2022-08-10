from __future__ import print_function

import base64
from email.message import EmailMessage

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class NotificationManager:

    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

    def send_email(self, text):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/Users/emanuel.sanchez/PycharmProjects/flight-deal-finder/credentials.json', self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            message = EmailMessage()

            message.set_content(text)

            message['To'] = 'adventistmany@gmail.com, viviana.eonv@gmail.com'
            message['From'] = 'esanchezc.sqa@gmail.com'
            message['Subject'] = 'Nuevos vuelos baratos encontrados!'

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
                .decode()

            create_message = {
                'raw': encoded_message
            }
            # pylint: disable=E1101
            send_message = (service.users().messages().send
                            (userId="me", body=create_message).execute())
            print(F'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(F'An error occurred: {error}')
            send_message = None
        return send_message