class TemplateHandler:
    type: str
    template_name: str
    data: object

    def __init__(self, type: str, data: object = {}):
        template_for_email_type = {
            "PATIENT_REGISTERED_ACCOUNT": "PatientRegisteredAccount",
            "PHYSICIAN_REGISTERED_ACCOUNT": "PhysicianRegisteredAccount",
            "PHYSICIAN_APPROVED_ACCOUNT": "ApprovedPhysicianAccount",
            "PHYSICIAN_DENIED_ACCOUNT": "RejectedPhysicianAccount",
            "PASSWORD_CHANGED": "PasswordChanged",
            "PENDING_APPOINTMENT": "PendingAppointment",
            "UPDATED_APPOINTMENT": "UpdatedAppointment",
            "APPROVED_APPOINTMENT": "ApprovedAppointment",
            "CANCELED_APPOINTMENT": "CanceledAppointment",
            "EDITED_RECORDS": "EditedRecords",
            "PHYSICIAN_UNBLOCKED_ACCOUNT": "UnblockedPhysicianAccount",
            "APPROVED_UPDATED_APPOINTMENT": "ApprovedUpdatedAppointment",
            "CANCELED_APPOINTMENT_DUE_TO_PHYSICIAN_DENIAL": "CanceledAppointmentDueToPhysicianDenial",
            "NEW_SPECIALTY_VALUE": "UpdateSpecialtyValue",
        }
        self.type = type
        self.template_name = template_for_email_type[self.type]
        self.data = data

    def generate_template(self):
        with open(f"app/models/email_templates/{self.template_name}.html", "r") as fp:
            template_content = fp.read()
        return template_content.format(**self.data)
