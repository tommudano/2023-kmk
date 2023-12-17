from fastapi import HTTPException, status
from datetime import datetime
from firebase_admin import firestore

db = firestore.client()


class Physician:
    role: str
    name: str
    last_name: str
    tuition: str
    specialty: str
    email: str
    id: str
    approved: str

    def __init__(
        self,
        role: str,
        name: str,
        last_name: str,
        tuition: str,
        specialty: str,
        email: str,
        id: str,
        approved: str = "pending",
    ):
        self.role = role
        self.name = name
        self.last_name = last_name
        self.tuition = tuition
        self.specialty = specialty.lower()
        self.email = email
        self.id = id
        self.approved = approved

    @staticmethod
    def get_by_id(id):
        return db.collection("physicians").document(id).get().to_dict()

    @staticmethod
    def get_blocked_by_id(id):
        return db.collection("deniedPhysicians").document(id).get().to_dict()

    @staticmethod
    def get_by_specialty(specialty_name):
        physicians = (
            db.collection("physicians")
            .where("specialty", "==", specialty_name)
            .where("approved", "==", "approved")
            .get()
        )
        physiciansList = [physician.to_dict() for physician in physicians]
        return sorted(
            physiciansList,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    @staticmethod
    def has_availability(id, date):
        physician_doc = db.collection("physicians").document(id).get().to_dict()
        day_of_week_of_appointment = str(
            datetime.fromtimestamp(date).date().strftime("%w")
        )
        precise_start_hour_of_appointment = (
            datetime.fromtimestamp(date).hour + datetime.fromtimestamp(date).minute / 60
        )

        if not physician_doc["agenda"].get(day_of_week_of_appointment):
            return False

        if physician_doc.get("appointments") and physician_doc["appointments"].get(
            str(date)
        ):
            return False

        appointment_begins_after_shift_starts = (
            precise_start_hour_of_appointment
            >= physician_doc["agenda"][day_of_week_of_appointment]["start"]
        )

        appointment_finishes_before_shift_ends = (
            precise_start_hour_of_appointment + 0.5
            <= physician_doc["agenda"][day_of_week_of_appointment]["finish"]
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
        physicians_list = [physician.to_dict() for physician in physicians]
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
        physicians_list = [physician.to_dict() for physician in physicians]
        return sorted(
            physicians_list,
            key=lambda physician: physician["first_name"].lower()
            + physician["last_name"].lower(),
        )

    @staticmethod
    def get_physicians_denied():
        physicians = db.collection("deniedPhysicians").get()
        physicians_list = [physician.to_dict() for physician in physicians]
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
    def update_agenda(id, agenda):
        db.collection("physicians").document(id).update({"agenda": agenda})

    def create(self):
        if db.collection("physicians").document(self.id).get().exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user already exists",
            )
        db.collection("physicians").document(self.id).set(
            {
                "id": self.id,
                "first_name": self.name,
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
            }
        )
        return self.id
