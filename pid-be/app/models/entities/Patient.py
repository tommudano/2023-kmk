from fastapi import status, HTTPException

from firebase_admin import firestore

db = firestore.client()


class Patient:
    role: str
    first_name: str
    last_name: str
    email: str
    id: str

    def __init__(
        self,
        role: str,
        first_name: str,
        last_name: str,
        email: str,
        id: str,
    ):
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.id = id

    @staticmethod
    def get_by_id(id):
        return db.collection("patients").document(id).get().to_dict()

    @staticmethod
    def is_patient(id):
        return db.collection("patients").document(id).get().exists

    @staticmethod
    def has_pending_scores(id):
        pending_scores_doc = db.collection("patientsPendingToScore").document(id).get()
        if not pending_scores_doc.exists:
            return False
        return len(pending_scores_doc.to_dict()) > 0

    def create(self):
        if db.collection("patients").document(self.id).get().exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user already exists",
            )
        db.collection("patients").document(self.id).set(
            {
                "id": self.id,
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
            }
        )
