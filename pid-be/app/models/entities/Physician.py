from fastapi import HTTPException, status
from datetime import datetime
from firebase_admin import firestore
from app.models.entities.Specialty import Specialty

db = firestore.client()


class Physician:
    role: str
    first_name: str
    last_name: str
    tuition: str
    specialty: str
    email: str
    id: str
    approved: str
    agenda: dict
    appointments: list
    appointment_value: int
    google_meet_conference_enabled: bool

    def __init__(
        self,
        first_name: str,
        last_name: str,
        tuition: str,
        specialty: str,
        email: str,
        id: str,
        role: str = "physician",
        google_meet_conference_enabled=False,
        appointment_value: int = None,
        agenda: dict = {},
        approved: str = "pending",
        appointments: dict = {},
    ):
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.tuition = tuition
        self.specialty = specialty.lower()
        self.email = email
        self.id = id
        self.agenda = agenda
        self.approved = approved
        self.appointments = appointments
        self.appointment_value = (
            appointment_value
            if appointment_value
            else Specialty.get_by_name(self.specialty).value
        )
        self.google_meet_conference_enabled = google_meet_conference_enabled

    @staticmethod
    def get_by_id(id):
        physician_document = db.collection("physicians").document(id).get().to_dict()
        return Physician(**physician_document)

    @staticmethod
    def get_blocked_by_id(id):
        blocked_physician_document = (
            db.collection("deniedPhysicians").document(id).get().to_dict()
        )
        return Physician(**blocked_physician_document)

    @staticmethod
    def get_approved_by_specialty(specialty_name):
        physicians = (
            db.collection("physicians")
            .where("specialty", "==", specialty_name)
            .where("approved", "==", "approved")
            .get()
        )
        physiciansList = [
            Physician(**physician.to_dict()).__dict__ for physician in physicians
        ]
        return sorted(
            physiciansList,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    def has_availability(self, date):
        day_of_week_of_appointment = str(
            datetime.fromtimestamp(date).date().strftime("%w")
        )
        precise_start_hour_of_appointment = (
            datetime.fromtimestamp(date).hour + datetime.fromtimestamp(date).minute / 60
        )

        if not self.agenda.get(str(day_of_week_of_appointment)):
            return False

        if self.appointments and self.appointments.get(str(date)):
            return False

        appointment_begins_after_shift_starts = (
            precise_start_hour_of_appointment
            >= self.agenda[day_of_week_of_appointment]["start"]
        )

        appointment_finishes_before_shift_ends = (
            precise_start_hour_of_appointment + 0.5
            <= self.agenda[day_of_week_of_appointment]["finish"]
        )

        return (
            appointment_begins_after_shift_starts
            and appointment_finishes_before_shift_ends
        )

    @staticmethod
    def schedule_appointment(id, date):
        db.collection("physicians").document(id).update({f"appointments.{date}": True})

    @staticmethod
    def get_pending_physicians():
        physicians = (
            db.collection("physicians").where("approved", "==", "pending").get()
        )
        physicians_list = [
            Physician(**physician.to_dict()).__dict__ for physician in physicians
        ]
        return sorted(
            physicians_list,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    @staticmethod
    def get_physicians_working():
        physicians = (
            db.collection("physicians").where("approved", "==", "approved").get()
        )
        physicians_list = [
            Physician(**physician.to_dict()).__dict__ for physician in physicians
        ]
        return sorted(
            physicians_list,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    @staticmethod
    def get_physicians_denied():
        physicians = db.collection("deniedPhysicians").get()
        physicians_list = [
            Physician(**physician.to_dict()).__dict__ for physician in physicians
        ]
        return sorted(
            physicians_list,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    @staticmethod
    def is_physician(id):
        return db.collection("physicians").document(id).get().exists

    @staticmethod
    def is_blocked_physician(id):
        return db.collection("deniedPhysicians").document(id).get().exists

    @staticmethod
    def free_agenda(id, date):
        db.collection("physicians").document(id).update(
            {f"appointments.{date}": firestore.DELETE_FIELD}
        )

    @staticmethod
    def approve_appointment(id):
        db.collection("appointments").document(id).update({"status": "approved"})

    @staticmethod
    def deny_appointment(id):
        db.collection("appointments").document(id).update({"status": "denied"})

    @staticmethod
    def update_agenda(id, agenda, google_meet_conference_enabled):
        db.collection("physicians").document(id).update(
            {
                "agenda": agenda,
                "google_meet_conference_enabled": google_meet_conference_enabled,
            }
        )

    def update_appointment_value(self, new_value):
        specialty = Specialty.get_by_name(self.specialty)
        if specialty.value * 2 < new_value:
            raise HTTPException(
                status_code=400,
                detail="El nuevo valor debe ser menor o igual al doble del valo que uso el administrador",
            )
        db.collection("physicians").document(self.id).update(
            {"appointment_value": new_value}
        )
        return Physician(**{**self.__dict__, "appointment_value": new_value})

    def create(self):
        if db.collection("physicians").document(self.id).get().exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user already exists",
            )
        db.collection("physicians").document(self.id).set(
            {
                "id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "tuition": self.tuition,
                "specialty": self.specialty,
                "email": self.email,
                "approved": self.approved,
                "agenda": {
                    "1": {"start": 8, "finish": 18},
                    "2": {"start": 8, "finish": 18},
                    "3": {"start": 8, "finish": 18},
                    "4": {"start": 8, "finish": 18},
                    "5": {"start": 8, "finish": 18},
                },
                "appointment_value": self.appointment_value,
                "google_meet_conference_enabled": self.google_meet_conference_enabled,
            }
        )
        return self.id
