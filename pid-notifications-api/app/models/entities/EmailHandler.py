import os
from dotenv import load_dotenv

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.models.entities.TemplateHandler import TemplateHandler

load_dotenv()


class EmailHandler:
    type: str
    subject: str
    data: object
    configuration = ConnectionConfig(
        MAIL_USERNAME=os.environ.get("MAIL_USERNAME"),
        MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD"),
        MAIL_FROM=os.environ.get("MAIL_FROM"),
        MAIL_PORT=os.environ.get("MAIL_PORT"),
        MAIL_SERVER=os.environ.get("MAIL_SERVER"),
        MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )

    def __init__(self, type: str, data: object):
        subject_for_email_type = {
            "PATIENT_REGISTERED_ACCOUNT": "Bienvenid@!",
            "PHYSICIAN_REGISTERED_ACCOUNT": "Bienvenid@!",
            "PHYSICIAN_APPROVED_ACCOUNT": "Cuenta Verificada",
            "PHYSICIAN_DENIED_ACCOUNT": "Cuenta Bloqueada",
            "PASSWORD_CHANGED": "Contrase&ntilde;a Modificada",
            "PENDING_APPOINTMENT": "Nuevo Turno",
            "UPDATED_APPOINTMENT": "Turno Modificado",
            "APPROVED_APPOINTMENT": "Turno Aprobado",
            "CANCELED_APPOINTMENT": "Turno Cancelado",
            "EDITED_RECORDS": "Registros Actualizados",
            "PHYSICIAN_UNBLOCKED_ACCOUNT": "Cuenta Desbloqueada",
            "APPROVED_UPDATED_APPOINTMENT": "Tu turno modificado ha sido Aprobado",
            "CANCELED_APPOINTMENT_DUE_TO_PHYSICIAN_DENIAL": "Turno Cancelado",
            "NEW_SPECIALTY_VALUE": "Valor de especialidad actualizado",
        }
        self.type = type
        self.subject = subject_for_email_type[self.type]
        self.data = data

    async def send_email(self):
        template_handler = TemplateHandler(self.type, self.data)
        message = MessageSchema(
            subject=self.subject,
            recipients=[self.data["email"]],
            body=template_handler.generate_template(),
            subtype="html",
        )

        fm = FastMail(self.configuration)
        await fm.send_message(message)
