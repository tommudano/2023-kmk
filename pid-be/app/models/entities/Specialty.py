from fastapi import HTTPException, status
from datetime import datetime
from firebase_admin import firestore

db = firestore.client()


class Specialty:
    id: str
    name: str

    def __init__(
        self,
        id: str,
        name: str,
    ):
        self.name = name.lower()
        self.id = id

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
        db.collection("specialties").document().set(
            {"name": name.lower(), "value": 3000}
        )

    @staticmethod
    def delete_specialty(name):
        query = db.collection("specialties").where("name", "==", name.lower())

        docs = query.stream()

        for doc in docs:
            doc.reference.delete()

    @staticmethod
    def update_value(name, value):
        docs = db.collection("specialties").where("name", "==", name.lower()).get()
        db.collection("specialties").document(docs[0].id).update({"value": value})
