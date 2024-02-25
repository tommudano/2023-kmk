import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleAPIHandler:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    @staticmethod
    def get_credentials():
        creds = None
        if os.path.exists("app/helpers/google_configs/token.json"):
            creds = Credentials.from_authorized_user_file(
                "app/helpers/google_configs/token.json", GoogleAPIHandler.SCOPES
            )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "app/helpers/google_configs/credentials.json",
                    GoogleAPIHandler.SCOPES,
                )
                creds = flow.run_local_server(port=0)
            with open("app/helpers/google_configs/token.json", "w") as token:
                token.write(creds.to_json())
        return creds

    @staticmethod
    def generate_event_body(appointment, physician, patient):
        appointment_times_in_iso_format = appointment.get_iso_formatted_time()
        return {
            "summary": f"Consulta Medica - {physician.first_name} {physician.last_name}",
            "description": f"<li><b>Especialidad</b>: {physician.specialty}</li><li><b>Paciente</b>: {patient['first_name']} {patient['last_name']}</li><li><b>Medico</b>: {physician.first_name} {physician.last_name}</li>",
            "start": {
                "dateTime": appointment_times_in_iso_format["start"],
                "timeZone": "America/Argentina/Buenos_Aires",
            },
            "end": {
                "dateTime": appointment_times_in_iso_format["finish"],
                "timeZone": "America/Argentina/Buenos_Aires",
            },
            "attendees": [
                {"email": patient["email"]},
                {"email": physician.email},
            ],
            "conferenceData": {
                "createRequest": {
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    "requestId": "RandomString",
                }
            },
        }

    @staticmethod
    def create_event(appointment, physician, patient):
        creds = GoogleAPIHandler.get_credentials()
        try:
            service = build("calendar", "v3", credentials=creds)
            event = (
                service.events()
                .insert(
                    calendarId="primary",
                    conferenceDataVersion=1,
                    sendUpdates="all",
                    body=GoogleAPIHandler.generate_event_body(
                        appointment, physician, patient
                    ),
                )
                .execute()
            )
            return event["hangoutLink"], event["id"]
        except HttpError as error:
            print(f"An error occurred: {error}")

    @staticmethod
    def delete_event(event_id):
        creds = GoogleAPIHandler.get_credentials()
        try:
            service = build("calendar", "v3", credentials=creds)
            service.events().delete(
                calendarId="primary",
                sendUpdates="all",
                eventId=event_id,
            ).execute()
        except HttpError as error:
            print(f"An error occurred: {error}")
