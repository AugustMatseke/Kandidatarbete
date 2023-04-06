import os

import discord
from app.db_interface import db
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/calendar.events']


async def do_auth(message: discord.Message):
    token = db.get_token(message.author.id)
    if token:
        creds = Credentials.from_authorized_user_info(token, SCOPES)
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            await message.channel.send(flow.authorization_url()[0] + "&redirect_uri=http://localhost:8080/")
            creds = flow.run_local_server(port=8080, open_browser=False)

        db.set_token(message.author.id, creds.to_json())

    # for testing
    service = build('calendar', 'v3', credentials=creds)
    events_result = service.events().list(calendarId='primary',
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
    events = events_result.get('items', [])
    await message.channel.send(str(events))

