from fastapi import HTTPException, status
from datetime import datetime
from firebase_admin import firestore

db = firestore.client()


class Specialty:
    id: str
    name: str
    value: int

    def __init__(self, id: str, name: str, value: int):
        self.name = name.lower()
        self.id = id
        self.value = value

    @staticmethod
    def get_by_name(name):
        specialty = db.collection("specialties").where("name", "==", name.lower()).get()

        return Specialty(**specialty[0].to_dict())

    @staticmethod
    def get_all_names():
        specialties_doc = db.collection("specialties").order_by("name").get()
        return [specialty_doc.to_dict()["name"] for specialty_doc in specialties_doc]

    @staticmethod
    def get_all():
        specialties_doc = db.collection("specialties").order_by("name").get()
        return [specialty_doc.to_dict() for specialty_doc in specialties_doc]

    @staticmethod
    def exists_with_name(name):
        return (
            len(db.collection("specialties").where("name", "==", name.lower()).get())
            > 0
        )

    @staticmethod
    def add_specialty(name):
        if Specialty.exists_with_name(name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La especialidad ya existe",
            )
        id = db.collection("specialties").document().id
        db.collection("specialties").document(id).set(
            {"id": id, "name": name.lower(), "value": 3000}
        )

    @staticmethod
    def delete_specialty(name):
        query = db.collection("specialties").where("name", "==", name.lower())

        docs = query.stream()

        for doc in docs:
            doc.reference.delete()

    def update_value(self, value):
        db.collection("specialties").document(self.id).update({"value": value})
        physicians_to_update = (
            db.collection("physicians").where("appointment_value", ">", value * 2).get()
        )
        from app.models.entities.Physician import Physician

        for physician in physicians_to_update:
            physician = Physician(**physician.to_dict())
            physician.update_appointment_value(value * 2)
        return Specialty(**{**self.__dict__, "value": value})
