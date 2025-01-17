import os

import discord
from app.db_interface import db
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dateutil.parser import parse

import wsgiref

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class _RedirectWSGIApp(object):
    def __init__(self, success_message="Success! You may now close this window."):
        self.last_request_uri = None
        self._success_message = success_message

    def __call__(self, environ, start_response):
        start_response("200 OK", [("Content-type", "text/plain; charset=utf-8")])
        self.last_request_uri = wsgiref.util.request_uri(environ)
        return [self._success_message.encode("utf-8")]


class CustomFlow(InstalledAppFlow):
    async def run_local_server(
        self,
        message_channel: discord.channel,
        host="localhost",
        bind_addr=None,
        port=8080,
        redirect_uri_trailing_slash=True,
        timeout_seconds=None,
        **kwargs
    ):
        wsgi_app = _RedirectWSGIApp()
        # Fail fast if the address is occupied
        wsgiref.simple_server.WSGIServer.allow_reuse_address = False
        local_server = wsgiref.simple_server.make_server(
            bind_addr or host, port, wsgi_app
        )

        redirect_uri_format = (
            "http://{}:{}/" if redirect_uri_trailing_slash else "http://{}:{}"
        )
        self.redirect_uri = redirect_uri_format.format(host, local_server.server_port)
        auth_url, _ = self.authorization_url(**kwargs)

        await message_channel.send(auth_url)

        local_server.timeout = timeout_seconds
        local_server.handle_request()

        # Note: using https here because oauthlib is very picky that
        # OAuth 2.0 should only occur over https.
        authorization_response = wsgi_app.last_request_uri.replace("http", "https")
        self.fetch_token(authorization_response=authorization_response)

        # This closes the socket
        local_server.server_close()

        return self.credentials


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
            flow = CustomFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = await flow.run_local_server(
                message_channel=message.channel, port=0, open_browser=False
            )

        db.set_token(message.author.id, creds.to_json())

    await message.channel.send("Logged in.")


def add_event(user_id, name, start, end=None, location=""):
    if not db.get_token(user_id):
        return None
    
    temp = dict()
    creds = Credentials.from_authorized_user_info(db.get_token(user_id), SCOPES)
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": name,
        "location": location,
        "start": {
            "dateTime": parse(start).isoformat(),
            "timeZone": "Europe/Stockholm",
        },
        "end": {
            "dateTime": parse(end).isoformat() if end else parse(start).isoformat(),
            "timeZone": "Europe/Stockholm",
        },
    }

    event = service.events().insert(calendarId="primary", body=event).execute()
    return event


def remove_event(author_id, event_id):
    creds = Credentials.from_authorized_user_info(db.get_token(author_id), SCOPES)
    service = build("calendar", "v3", credentials=creds)

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
    except HttpError as e:
        if e.resp.status == 410:
            return False
        else:
            raise e
    return True


def modify_event(
    event_id,
    author_id,
    name,
    start,
    location="",
    end=None,
):
    creds = Credentials.from_authorized_user_info(db.get_token(author_id), SCOPES)
    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": name,
        "location": location,
        "start": {
            "dateTime": parse(start).isoformat(),
            "timeZone": "Europe/Stockholm",
        },
        "end": {
            "dateTime": parse(end).isoformat() if end else parse(start).isoformat(),
            "timeZone": "Europe/Stockholm",
        },
    }

    service.events().update(
        calendarId="primary", eventId=event_id, body=event
    ).execute()
    return True
