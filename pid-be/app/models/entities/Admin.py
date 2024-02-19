from fastapi import HTTPException, status
from firebase_admin import firestore

from app.models.entities.Physician import Physician
from app.models.entities.Appointment import Appointment
from app.models.entities.Specialty import Specialty

db = firestore.client()


class Admin:
    name: str
    last_name: str
    email: str
    id: str
    registered_by: str

    def __init__(
        self, name: str, last_name: str, email: str, id: str, registered_by: str
    ):
        self.name = name
        self.last_name = last_name
        self.email = email
        self.id = id
        self.registered_by = registered_by

    @staticmethod
    def get_by_id(id):
        return db.collection("superusers").document(id).get().to_dict()

    @staticmethod
    def is_admin(id):
        return db.collection("superusers").document(id).get().exists

    @staticmethod
    def approve_physician(id):
        db.collection("physicians").document(id).update({"approved": "approved"})

    @staticmethod
    def cancel_appointments_for_physician(physician_id):
        appointments_for_physician = (
            db.collection("appointments")
            .where("physician_id", "==", physician_id)
            .get()
        )
        for appointment_doc in appointments_for_physician:
            appointment = Appointment(**appointment_doc.to_dict())
            appointment.cancel_due_physician_denial()

    @staticmethod
    def deny_physician(id):
        Admin.cancel_appointments_for_physician(id)
        denied_physician = Physician.get_by_id(id)
        db.collection("deniedPhysicians").document(id).set(denied_physician.__dict__)
        db.collection("deniedPhysicians").document(id).update({"approved": "denied"})
        Admin.delete_physician(id)

    @staticmethod
    def unblock_physician(denied_physician):
        db.collection("physicians").document(denied_physician.id).set(
            {**denied_physician.__dict__, "approved": "approved"}
        )
        db.collection("deniedPhysicians").document(denied_physician.id).delete()

    @staticmethod
    def delete_physician(id):
        db.collection("physicians").document(id).delete()

    @staticmethod
    def get_specialies_with_physician_count():
        specialies_with_physician_count = []
        specialties = Specialty.get_all()
        for specialty in specialties:
            physician_count_for_specialty = (
                db.collection("physicians")
                .where("approved", "==", "approved")
                .where("specialty", "==", specialty["name"])
                .count()
                .get()
            )
            specialies_with_physician_count.append(
                {
                    "name": specialty["name"],
                    "value": specialty["value"],
                    "physicians_count": physician_count_for_specialty[0][0].value,
                }
            )
        return specialies_with_physician_count

    def create(self):
        if db.collection("superusers").document(self.id).get().exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The admin already exists",
            )
        db.collection("superusers").document(self.id).set(
            {
                "id": self.id,
                "first_name": self.name,
                "last_name": self.last_name,
                "email": self.email,
                "registered_by": self.registered_by,
            }
        )
