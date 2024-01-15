from .config import *
from app.models.entities.TemplateHandler import TemplateHandler
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

patient_account_data = {
    "name": "Tomas",
    "last_name": "Mudano",
    "email": "user@kmk.com",
}

physician_account_data = {
    "name": "Tomas",
    "last_name": "Mudano",
    "email": "user@kmk.com",
}

date_data = {"day": 20, "month": 3, "year": 2023, "hour": 10, "minute": 30}


def test_email_sending_endpoint_sends_returns_a_200_code():
    response_from_email_sending = client.post(
        "/emails/send",
        json={"type": "PATIENT_REGISTERED_ACCOUNT", "data": physician_account_data},
    )

    assert response_from_email_sending.status_code == 200


def test_email_template_handler_generates_correct_HTML_from_the_patient_registered_account():
    template_handler = TemplateHandler(
        **{"type": "PATIENT_REGISTERED_ACCOUNT", "data": physician_account_data}
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/PatientRegisteredAccount.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        name=physician_account_data["name"],
        last_name=physician_account_data["last_name"],
    )


def test_email_template_handler_generates_correct_HTML_from_the_physician_registered_account():
    template_handler = TemplateHandler(
        **{"type": "PHYSICIAN_REGISTERED_ACCOUNT", "data": physician_account_data}
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/PhysicianRegisteredAccount.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        name=physician_account_data["name"],
        last_name=physician_account_data["last_name"],
    )


def test_email_template_handler_generates_correct_HTML_from_the_physician_approved_account():
    template_handler = TemplateHandler(
        **{
            "type": "PHYSICIAN_APPROVED_ACCOUNT",
            "data": {"email": physician_account_data["email"]},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/ApprovedPhysicianAccount.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format()


def test_email_template_handler_generates_correct_HTML_from_the_physician_rejected_account():
    template_handler = TemplateHandler(
        **{
            "type": "PHYSICIAN_DENIED_ACCOUNT",
            "data": {"email": physician_account_data["email"]},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/RejectedPhysicianAccount.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format()


def test_email_template_handler_generates_correct_HTML_for_password_change():
    template_handler = TemplateHandler(
        **{
            "type": "PASSWORD_CHANGED",
            "data": {"email": physician_account_data["email"]},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/PasswordChanged.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format()


def test_email_template_handler_generates_correct_HTML_for_pending_to_approve_appointment():
    template_handler = TemplateHandler(
        **{
            "type": "PENDING_APPOINTMENT",
            "data": {**patient_account_data, **date_data},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/PendingAppointment.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        **{**patient_account_data, **date_data}
    )


def test_email_template_handler_generates_correct_HTML_for_updated_appointment():
    template_handler = TemplateHandler(
        **{
            "type": "UPDATED_APPOINTMENT",
            "data": {**patient_account_data, **date_data},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/UpdatedAppointment.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        **{**patient_account_data, **date_data}
    )


def test_email_template_handler_generates_correct_HTML_for_approved_appointment():
    template_handler = TemplateHandler(
        **{
            "type": "APPROVED_APPOINTMENT",
            "data": {
                "physician_first_name": physician_account_data["name"],
                "physician_last_name": physician_account_data["last_name"],
                "email": patient_account_data["email"],
                **date_data,
            },
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/ApprovedAppointment.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        physician_first_name=physician_account_data["name"],
        physician_last_name=physician_account_data["last_name"],
        **date_data
    )


def test_email_template_handler_generates_correct_HTML_for_approved_appointment_that_has_been_updated():
    template_handler = TemplateHandler(
        **{
            "type": "APPROVED_UPDATED_APPOINTMENT",
            "data": {
                "physician_first_name": physician_account_data["name"],
                "physician_last_name": physician_account_data["last_name"],
                "email": patient_account_data["email"],
                **date_data,
            },
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/ApprovedUpdatedAppointment.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        physician_first_name=physician_account_data["name"],
        physician_last_name=physician_account_data["last_name"],
        **date_data
    )


def test_email_template_handler_generates_correct_HTML_for_canceled_appointment():
    template_handler = TemplateHandler(
        **{
            "type": "CANCELED_APPOINTMENT",
            "data": {"email": physician_account_data["email"], **date_data},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/CanceledAppointment.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(**date_data)


def test_email_template_handler_generates_correct_HTML_for_canceled_appointment_due_to_physician_denial():
    template_handler = TemplateHandler(
        **{
            "type": "CANCELED_APPOINTMENT_DUE_TO_PHYSICIAN_DENIAL",
            "data": {
                "email": patient_account_data["email"],
                "name": physician_account_data["name"],
                "last_name": physician_account_data["last_name"],
                **date_data,
            },
        }
    )
    generated_template = template_handler.generate_template()
    with open(
        "app/models/email_templates/CanceledAppointmentDueToPhysicianDenial.html", "r"
    ) as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format(
        **{**physician_account_data, **date_data}
    )


def test_email_template_handler_generates_correct_HTML_for_edited_records():
    template_handler = TemplateHandler(
        **{
            "type": "EDITED_RECORDS",
            "data": {"email": patient_account_data["email"]},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/EditedRecords.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format()


def test_email_template_handler_generates_correct_HTML_for_ublocked_physician_accounts():
    template_handler = TemplateHandler(
        **{
            "type": "PHYSICIAN_UNBLOCKED_ACCOUNT",
            "data": {"email": physician_account_data["email"]},
        }
    )
    generated_template = template_handler.generate_template()
    with open("app/models/email_templates/UnblockedPhysicianAccount.html", "r") as fp:
        expected_template = fp.read()
    assert generated_template == expected_template.format()
