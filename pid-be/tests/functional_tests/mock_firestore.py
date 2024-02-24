import time
from datetime import datetime
from config import *
from firebase_admin import firestore, auth

if __name__ == "__main__":
    db = firestore.client()

    specialties = [
        "cardiologia",
        "dermatologia",
        "endocrinologia",
        "gastroenterologia",
        "geriatria",
        "ginecologia",
        "hematologia",
        "infectologia",
        "nefrologia",
        "neurologia",
        "oftalmologia",
        "oncologia",
        "ortopedia",
        "otorrinolaringologia",
        "pediatria",
        "pneumologia",
        "psiquiatria",
        "reumatologia",
        "urologia",
    ]

    blood_types = [
        "A+",
        "A-",
        "B+",
        "B-",
        "AB+",
        "AB-",
        "O+",
        "O-",
    ]

    genders = ["Femenino", "Masculino", "Otro"]

    today_date = datetime.now().date()
    number_of_day_of_week = int(today_date.strftime("%w"))

    a_KMK_user_information = {
        "display_name": "KMK Test User",
        "email": "getPhysiciansBySpecialtyTestUser@kmk.com",
        "email_verified": True,
        "password": "verySecurePassword123",
    }

    a_patient_information = {
        "id": "apatientid",
        "name": "Patient",
        "last_name": "Test",
        "email": "aPatientEmail@kmk.com",
        "birth_date": "2000-01-01",
        "gender": genders[0],
        "blood_type": blood_types[0],
    }

    other_patient_information = {
        "id": "otherpatientid",
        "name": "OtherPatient",
        "last_name": "OtherTest",
        "email": "otherPatientEmail@kmk.com",
        "birth_date": "2012-12-19",
        "gender": genders[1],
        "blood_type": blood_types[3],
    }

    observation_one = {
        "date": "2023-01-01",
        "physician": "Doctor",
        "specialty": "Cardiologia",
        "observation": "This is an observation",
    }

    observation_two = {
        "date": "2023-09-12",
        "physician": "Doc",
        "specialty": "Oftalmologia",
        "observation": "This is another observation",
    }

    a_physician_information = {
        "approved": "approved",
        "id": "avalidid",
        "first_name": "Doc",
        "last_name": "Docson",
        "email": "DocDocson@kmk.com",
        "specialty": specialties[0],
        "tuition": "123456",
        "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
        "appointment_value": 1000,
    }

    another_physician_information = {
        "approved": "approved",
        "id": "anothervalidid",
        "first_name": "Doc",
        "last_name": "Docson the Second",
        "email": "DocDocsonTheSecond@kmk.com",
        "specialty": specialties[0],
        "tuition": "1112222",
        "agenda": {str(number_of_day_of_week): {"start": 8, "finish": 18.5}},
        "appointment_value": 1000,
    }

    other_physician_information = {
        "approved": "approved",
        "id": "othervalidid",
        "first_name": "Doc",
        "last_name": "Docson the Third",
        "email": "DocDocsonTheThird@kmk.com",
        "specialty": specialties[1],
        "tuition": "999543",
        "agenda": {
            str(number_of_day_of_week): {"start": 8, "finish": 18.5},
            str((number_of_day_of_week + 1) % 7): {"start": 7, "finish": 16},
        },
        "appointment_value": 1000,
    }

    admin_information = {
        "email": "admin@admin.com",
        "password": "Admin1234",
    }

    db.collection("physicians").document(a_physician_information["id"]).set(
        a_physician_information
    )
    db.collection("physicians").document(another_physician_information["id"]).set(
        another_physician_information
    )
    db.collection("physicians").document(other_physician_information["id"]).set(
        other_physician_information
    )

    a_patient_data = {
        key: value
        for key, value in a_patient_information.items()
        if key not in ["birth_date", "gender", "blood_type"]
    }
    db.collection("patients").document(a_patient_information["id"]).set(a_patient_data)
    other_patient_data = {
        key: value
        for key, value in other_patient_information.items()
        if key not in ["birth_date", "gender", "blood_type"]
    }
    db.collection("patients").document(other_patient_information["id"]).set(
        other_patient_data
    )
    record_data = {
        key: value
        for key, value in a_patient_information.items()
        if key not in ["role", "email"]
    }
    record_data["observations"] = [observation_one, observation_two]
    db.collection("records").document(a_patient_information["id"]).set(record_data)

    for specialty in specialties:
        id = db.collection("specialties").document().id
        db.collection("specialties").document(id).set(
            {"id": id, "name": specialty, "value": 3500}
        )

    for blood_type in blood_types:
        db.collection("blood_types").document().set({"type": blood_type})

    for gender in genders:
        db.collection("genders").document().set({"gender": gender})

    admin_uid = auth.create_user(**admin_information).uid
    db.collection("superusers").document(admin_uid).set(admin_information)
