import time
import os
import requests
from datetime import datetime
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
    appointment_value: int

    def __init__(
        self,
        date: int,
        physician_id: str,
        patient_id: str,
        appointment_value: int,
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
        self.appointment_value = appointment_value

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
    def get_all_pending_appointments_for_patient_with(uid):
        if not Patient.is_patient(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("patient_id", "==", uid)
            .where("status", "==", "pending")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_approved_appointments_for_physician_with(uid):
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
    def get_all_appointments_for_physician_with(uid):
        if not Physician.is_physician(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only physicians can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("physician_id", "==", uid)
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
            .order_by("date")
            .get()
        )
        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def update_rated_status(id):
        db.collection("appointments").document(id).update({"status": "rated"})

    @staticmethod
    def remove_pending_to_score_patient_register(patient_id, appointment_id):
        patients_appointments_pending_to_score = (
            db.collection("patientsPendingToScore").document(patient_id).get().to_dict()
        )
        patients_appointments_pending_to_score.pop(appointment_id)
        db.collection("patientsPendingToScore").document(patient_id).set(
            patients_appointments_pending_to_score
        )

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

    @staticmethod
    def get_all_rated_appointments_for_patient_with(uid):
        if not Patient.is_patient(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only patients can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("patient_id", "==", uid)
            .where("status", "==", "rated")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_closed_appointments_for_physician_with(uid):
        if not Physician.is_physician(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only physicians can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("physician_id", "==", uid)
            .where("status", "==", "closed")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]

    @staticmethod
    def get_all_rated_appointments_for_physician_with(uid):
        if not Physician.is_physician(uid):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only physicians can access this resource",
            )
        appointments = (
            db.collection("appointments")
            .where("physician_id", "==", uid)
            .where("status", "==", "rated")
            .order_by("date")
            .get()
        )

        return [appointment.to_dict() for appointment in appointments]

    def delete(self):
        db.collection("appointments").document(self.id).delete()
        Physician.free_agenda(self.physician_id, self.date)

    def update(self, updated_values):
        if not Physician.get_by_id(self.physician_id).has_availability(
            updated_values["date"]
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
                "status": "closed",
            }
        )
        db.collection("patientsPendingToScore").document(self.patient_id).set(
            {self.id: True}
        )

    def create(self):
        if Patient.has_pending_scores(self.patient_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El paciente tiene turnos pendientes por puntuar",
            )
        id = db.collection("appointments").document().id
        db.collection("appointments").document(id).set(
            {
                "id": id,
                "date": self.date,
                "physician_id": self.physician_id,
                "patient_id": self.patient_id,
                "created_at": round(time.time()),
                "status": self.status,
                "appointment_value": self.appointment_value,
            }
        )
        Physician.schedule_appointment(id=self.physician_id, date=self.date)
        return id

    def cancel_due_physician_denial(self):
        self.delete()
        physician = Physician.get_by_id(self.physician_id)
        patient = Patient.get_by_id(self.patient_id)
        date = datetime.fromtimestamp(self.date)
        requests.post(
            os.environ.get("NOTIFICATIONS_API_URL"),
            json={
                "type": "CANCELED_APPOINTMENT_DUE_TO_PHYSICIAN_DENIAL",
                "data": {
                    "email": patient["email"],
                    "name": physician.first_name,
                    "last_name": physician.last_name,
                    "day": date.day,
                    "month": date.month,
                    "year": date.year,
                    "hour": date.hour,
                    "minute": date.minute,
                    "second": date.second,
                },
            },
        )
