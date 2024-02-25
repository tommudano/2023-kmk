from datetime import datetime

from app.models.entities.Specialty import Specialty
from app.models.entities.Physician import Physician


class MetricParserHelper:
    @staticmethod
    def filter_appointments_for_current_year_by_month_and_key(appointments, key):
        monthly_appointment_metric = {
            "enero": 0,
            "febrero": 0,
            "marzo": 0,
            "abril": 0,
            "mayo": 0,
            "junio": 0,
            "julio": 0,
            "agosto": 0,
            "septiembre": 0,
            "octubre": 0,
            "noviembre": 0,
            "diciembre": 0,
        }
        current_year = datetime.today().year
        for appointment in appointments:
            appointment_date_key_as_datetime = datetime.fromtimestamp(appointment[key])
            if appointment_date_key_as_datetime.year == current_year:
                month_name = list(monthly_appointment_metric.keys())[
                    appointment_date_key_as_datetime.month - 1
                ]
                monthly_appointment_metric[month_name] += 1
        return monthly_appointment_metric

    @staticmethod
    def filter_appointments_per_specialty(appointments):
        specialties = Specialty.get_all_names()
        appointments_per_specialty = {}
        for specialty in specialties:
            appointments_per_specialty[specialty] = 0
        for appointment in appointments:
            appointments_physician = Physician.get_by_id(appointment["physician_id"])
            if appointments_per_specialty.get(appointments_physician.specialty) != None:
                appointments_per_specialty[appointments_physician.specialty] += 1
        filtered_appointments_per_specialty = {
            k: v for k, v in appointments_per_specialty.items() if v > 0
        }
        return filtered_appointments_per_specialty
