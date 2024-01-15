from firebase_admin import firestore

db = firestore.client()


class Gender:
    @staticmethod
    def get_all():
        genders = db.collection("genders").order_by("gender").get()
        return [gender.to_dict()["gender"] for gender in genders]
