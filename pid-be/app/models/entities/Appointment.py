import time
from firebase_admin import firestore
from fastapi import HTTPException, status

from .Physician import Physician
from .Patient import Patient

db = firestore.client()


class Appointment:
    id: str = None
    date: int
    physician_id: str
    patient_id: str
    created_at: int = None
    updated_at: int = None
    status: str
    attended: bool
    start_time: str

    def __init__(
        self,
        date: int,
        physician_id: str,
        patient_id: str,
        id: str = None,
        created_at: int = None,
        updated_at: int = None,
        status: str = "pending",
        attended: bool = None,
        start_time: str = None,
    ):
        if not Patient.is_patient(patient_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can create appointments",
            )

        self.physician_id = physician_id
        self.date = date
        self.patient_id = patient_id
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.status = status
        self.attended = attended
        self.start_time = start_time

    @staticmethod
    def get_all_appointments_for_patient_with(uid):
        if not Patient.is_patient(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("patient_id", "==", uid)
            .where("status", "==", "approved")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_appointments_for_physician_with(uid):
        if not Physician.is_physician(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only physicians can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("physician_id", "==", uid)
            .where("status", "==", "approved")
            .order_by("date")
            .get()
        )
        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_appointments():
        appointments = db.collection("appointments").get()

        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_appointments_updtated_for_physician(uid):
        updated_appointments = (
            db.collection("appointments")
            .where("physician_id", "==", uid)
            .where("updated_at", ">", 0)
            .get()
        )
        return [appointment.to_dict() for appointment in updated_appointments]

    @staticmethod
    def get_all_appointments_updtated(uid):
        updated_appointments = (
            db.collection("appointments").where("updated_at", ">", 0).get()
        )
        return [appointment.to_dict() for appointment in updated_appointments]

    @staticmethod
    def get_by_id(id):
        appointment_document = db.collection("appointments").document(id).get()
        if appointment_document.exists:
            return Appointment(**appointment_document.to_dict())
        return None

    @staticmethod
    def is_appointment(id):
        return db.collection("appointments").document(id).get().exists

    @staticmethod
    def get_pending_appointments(id):
        appointments = (
            db.collection("appointments")
            .where("physician_id", "==", id)
            .where("status", "==", "pending")
            .get()
        )
        return [appointment.to_dict() for appointment in appointments]
    
    @staticmethod
    def update_rated_status(id):
        db.collection("appointments").document(id).update({"status": "rated"})
    
    @staticmethod
    def get_all_closed_appointments_for_patient_with(uid):
        if not Patient.is_patient(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("patient_id", "==", uid)
            .where("status", "==", "closed")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]


    def delete(self):
        db.collection("appointments").document(self.id).delete()
        Physician.free_agenda(self.physician_id, self.date)

    def update(self, updated_values):
        if not Physician.has_availability(
            id=self.physician_id, date=updated_values["date"]
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only set appointment at physicians available hours",
            )
        Physician.free_agenda(self.physician_id, self.date)
        db.collection("appointments").document(self.id).update(
            {**updated_values, "updated_at": round(time.time()), "status": "pending"}
        )
        self.date = updated_values["date"]
        Physician.schedule_appointment(id=self.physician_id, date=self.date)

    def close(self, updated_values):
        db.collection("appointments").document(self.id).update(
            {
                **updated_values,
                "start_time": updated_values["start_time"],
                "attended": updated_values["attended"],
                "status": "closed"
            }
        )

    
    def create(self):
        id = db.collection("appointments").document().id
        db.collection("appointments").document(id).set(
            {
                "id": id,
                "date": self.date,
                "physician_id": self.physician_id,
                "patient_id": self.patient_id,
                "created_at": round(time.time()),
                "status": self.status,
            }
        )
        Physician.schedule_appointment(id=self.physician_id, date=self.date)
        return id
