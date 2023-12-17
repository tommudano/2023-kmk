from firebase_admin import firestore

db = firestore.client()


class BloodType:
    @staticmethod
    def get_all():
        blood_types = db.collection("blood_types").order_by("type").get()
        return [blood_type.to_dict()["type"] for blood_type in blood_types]
