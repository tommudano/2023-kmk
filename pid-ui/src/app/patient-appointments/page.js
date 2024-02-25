"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "../styles/styles.module.css";
import DatePicker, { registerLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import es from "date-fns/locale/es";
import axios from "axios";
import https from "https";
import { Footer, Header, TabBar } from "../components/header";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

registerLocale("es", es);

const DashboardPatient = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [doctors, setDoctors] = useState([]);
    const [specialties, setSpecialties] = useState([]);
    const [selectedSpecialty, setSelectedSpecialty] = useState("");
    const [selectedDoctorId, setSelectedDoctorId] = useState("");
    const [selectedDoctor, setSelectedDoctor] = useState("");
    const [physiciansAgenda, setPhysiciansAgenda] = useState({});
    const [date, setDate] = useState(new Date());
    const [disabledAppointmentButton, setDisabledAppointmentButton] =
        useState(false);
    const [physicianScores, setPhysicianScores] = useState([]);
    const [
        googleMeetConferenceForAppointment,
        setGoogleMeetConferenceForAppointment,
    ] = useState(false);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const checkPendingReviews = async () => {
        try {
            const response = await axios.get(
                `${apiURL}users/patient-pending-scores`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data);
            if (response.data.pending_scores.length > 0) {
                router.push("/patient-dashboard/pending-reviews");
            }
        } catch (error) {
            toast.error("Error al obtener las reseñas pendientes");
            console.error(error);
        }
    };

    const getPhysicianScores = async (id) => {
        try {
            const response = await axios.get(`${apiURL}users/score/${id}`, {
                httpsAgent: agent,
            });
            console.log(response.data.score_metrics);

            let tempReviews = [
                { id: 1, type: "Puntualidad", rating: 0 },
                { id: 2, type: "Atencion", rating: 0 },
                { id: 3, type: "Limpieza", rating: 0 },
                { id: 4, type: "Disponibilidad", rating: 0 },
                { id: 5, type: "Precio", rating: 0 },
                { id: 6, type: "Comunicacion", rating: 0 },
            ];

            tempReviews[0].rating = response.data.score_metrics.puntuality;
            tempReviews[1].rating = response.data.score_metrics.attention;
            tempReviews[2].rating = response.data.score_metrics.cleanliness;
            tempReviews[3].rating = response.data.score_metrics.availability;
            tempReviews[4].rating = response.data.score_metrics.price;
            tempReviews[5].rating = response.data.score_metrics.communication;

            setPhysicianScores(tempReviews);
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
        }
    };

    const fetchSpecialties = async () => {
        try {
            const response = await axios.get(`${apiURL}specialties`, {
                httpsAgent: agent,
            });
            response.data.specialties == undefined
                ? setSpecialties([])
                : setSpecialties(response.data.specialties);
        } catch (error) {
            toast.error("Error al cargar especialidades");
            console.error(error);
        }
    };

    const fetchPhysicians = async (specialty) => {
        try {
            if (specialty) {
                const response = await axios.get(
                    `${apiURL}physicians/specialty/${specialty}`,
                    {
                        httpsAgent: agent,
                    }
                );
                response.data.physicians == undefined
                    ? setDoctors([])
                    : setDoctors(response.data.physicians);
            } else {
                setDoctors([]);
                setPhysiciansAgenda({});
            }
        } catch (error) {
            toast.error("Error al cargar médicos");
            console.error(error);
        }
    };

    const saveInformation = (doctorId) => {
        if (doctorId) {
            let doctor = doctors.filter((doctor) => doctor.id == doctorId)[0];
            console.log(doctor.agenda);
            setSelectedDoctor(doctor);
            setPhysiciansAgenda(doctor.agenda);
            getPhysicianScores(doctorId);
        } else {
            setPhysiciansAgenda({});
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setDisabledAppointmentButton(true);
        try {
            toast.info("Solicitando turno...");
            const response = await axios.post(
                `${apiURL}appointments/`,
                {
                    physician_id: selectedDoctorId,
                    date: Math.round(date.getTime() / 1000),
                    google_meet_conference: googleMeetConferenceForAppointment,
                },
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Turno solicitado. Aguarde aprobacion del mismo");
            setSelectedDoctorId("");
            setSelectedDoctor({});
            setDate(new Date());
            setSelectedSpecialty("");
            setPhysiciansAgenda({});
            setPhysicianScores([]);
            setGoogleMeetConferenceForAppointment(false);
        } catch (error) {
            if (error.response.status === 500)
                toast.error("Error al solicitar turno");
            else if (
                error.response.data.error &&
                error.response.data.error[0].msg ===
                    "Value error, Can only set appointment at physicians available hours"
            )
                toast.error("El horario ya ha sido reservado");
            else toast.error(error.response.data.detail);
        }
        setDisabledAppointmentButton(false);
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        checkPendingReviews()
            .then(() => {
                fetchSpecialties();
            })
            .then(() => setIsLoading(false));
    }, []);

    return (
        <div className={styles.dashboard}>
            <TabBar highlight='SolicitarTurnos' />

            <Header role='patient' />

            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        {/* Formulario de selección de especialidad y doctor */}
                        <form className={styles.form} onSubmit={handleSubmit}>
                            <div className={styles["title"]}>
                                Solicitar un nuevo turno
                            </div>

                            {/* Selector de especialidades */}
                            <div className={styles["subtitle"]}>
                                Seleccione una especialidad
                            </div>
                            <select
                                id='specialty'
                                value={selectedSpecialty}
                                required
                                onChange={(e) => {
                                    setSelectedSpecialty(e.target.value);
                                    fetchPhysicians(e.target.value);
                                }}
                            >
                                <option value=''>Especialidad</option>
                                {specialties.map((specialty) => (
                                    <option key={specialty} value={specialty}>
                                        {specialty.charAt(0).toUpperCase() +
                                            specialty.slice(1)}
                                    </option>
                                ))}
                            </select>

                            {/* Selector de médicos */}
                            <div className={styles["subtitle"]}>
                                Seleccione un médico
                            </div>
                            <select
                                id='doctor'
                                value={selectedDoctorId}
                                required
                                onChange={(e) => {
                                    setSelectedDoctorId(e.target.value);
                                    saveInformation(e.target.value);
                                    if (e.target.value === "")
                                        setPhysicianScores([]);
                                }}
                                disabled={!selectedSpecialty}
                            >
                                <option value=''>Médico</option>
                                {doctors.map((doctor) => (
                                    <option
                                        key={doctor.id}
                                        value={doctor.id}
                                        agenda={doctor.agenda}
                                    >
                                        {doctor.first_name} {doctor.last_name}
                                    </option>
                                ))}
                            </select>

                            {selectedDoctorId ? (
                                <div
                                    className={
                                        styles["appointment-value-patient"]
                                    }
                                >
                                    Precio de consulta: $
                                    {selectedDoctor.appointment_value}
                                </div>
                            ) : null}

                            <div className={styles["subtitle"]}>
                                Puntuaciones del médico{" "}
                                <Tooltip
                                    title='Las puntuaciones muestran la opinion de los usuarios acerca de los medicos. La puntuacion mas baja es 0 (muy malo) y la mas alta es 5 (excelente). En caso de que el medico no haya sido puntuado en una categoria aun, se mostrara que dicha seccion no tiene reviews.'
                                    placement='right'
                                >
                                    <IconButton>
                                        <InfoIcon />
                                    </IconButton>
                                </Tooltip>
                            </div>

                            <div
                                key={physicianScores.key}
                                className={styles["reviews-container"]}
                            >
                                {physicianScores.length > 0 ? (
                                    <>
                                        {physicianScores.map((review) => (
                                            <div
                                                key={review.id}
                                                className={styles["review"]}
                                            >
                                                <div
                                                    className={
                                                        styles[
                                                            "review-cards-container"
                                                        ]
                                                    }
                                                >
                                                    <div
                                                        className={
                                                            styles[
                                                                "review-card"
                                                            ]
                                                        }
                                                    >
                                                        <div
                                                            className={
                                                                styles[
                                                                    "review-card-title"
                                                                ]
                                                            }
                                                        >
                                                            {review.type}
                                                        </div>
                                                        <div
                                                            className={
                                                                styles[
                                                                    "review-card-content"
                                                                ]
                                                            }
                                                        >
                                                            {review.rating}
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    // If there are no reviews, display the message
                                    <div
                                        style={{
                                            fontSize: "20px",
                                            paddingLeft: "1rem",
                                            marginBottom: "1rem",
                                        }}
                                    >
                                        No hay reviews
                                    </div>
                                )}
                            </div>

                            {/* Selector de fechas */}
                            <div className={styles["subtitle"]}>
                                Seleccione una fecha
                            </div>
                            <div className={styles["physician-info-container"]}>
                                <div className={styles["datepicker-container"]}>
                                    <DatePicker
                                        locale='es'
                                        selected={date}
                                        onChange={(date) => {
                                            setDate(date);
                                        }}
                                        timeCaption='Hora'
                                        timeIntervals={30}
                                        showPopperArrow={false}
                                        showTimeSelect
                                        inline
                                        filterDate={(date) => {
                                            if (physiciansAgenda.working_days) {
                                                if (
                                                    physiciansAgenda.working_days.includes(
                                                        date.getDay()
                                                    )
                                                ) {
                                                    let workingHour =
                                                        physiciansAgenda.working_hours.filter(
                                                            (workingHour) =>
                                                                workingHour.day_of_week ===
                                                                date.getDay()
                                                        )[0];
                                                    return (
                                                        workingHour.start_time !==
                                                            0 &&
                                                        workingHour.finish_time !==
                                                            0
                                                    );
                                                }
                                            }
                                            return false;
                                        }}
                                        minDate={new Date()}
                                        filterTime={(time) => {
                                            if (
                                                physiciansAgenda.appointments &&
                                                !physiciansAgenda.appointments.includes(
                                                    Math.round(
                                                        time.getTime() / 1000
                                                    )
                                                ) &&
                                                physiciansAgenda.working_hours &&
                                                time >= new Date()
                                            ) {
                                                let workingHour =
                                                    physiciansAgenda.working_hours.filter(
                                                        (workingHour) =>
                                                            workingHour.day_of_week ===
                                                            date.getDay()
                                                    )[0];
                                                let parsedTime =
                                                    time.getHours() +
                                                    time.getMinutes() / 60;
                                                return (
                                                    workingHour &&
                                                    workingHour.start_time !==
                                                        undefined &&
                                                    workingHour.finish_time !==
                                                        undefined &&
                                                    workingHour.start_time <=
                                                        parsedTime &&
                                                    workingHour.finish_time >
                                                        parsedTime
                                                );
                                            }
                                            return false;
                                        }}
                                    />
                                </div>
                                {selectedDoctor.google_meet_conference_enabled ? (
                                    <div
                                        className={
                                            styles["schedule-day-modify"]
                                        }
                                    >
                                        <input
                                            type='checkbox'
                                            id='googleMeet'
                                            name='googleMeet'
                                            defaultChecked={
                                                googleMeetConferenceForAppointment
                                            }
                                            className={styles["checkbox-input"]}
                                            onChange={(e) =>
                                                setGoogleMeetConferenceForAppointment(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        <label
                                            htmlFor='googleMeet'
                                            className={styles["checkbox-label"]}
                                        >
                                            {"    "}¿Deseas tener la consulta a
                                            traves de Google Meet?
                                        </label>
                                    </div>
                                ) : null}
                            </div>

                            <button
                                type='submit'
                                className={`${styles["submit-button"]} ${
                                    !selectedDoctorId ||
                                    disabledAppointmentButton
                                        ? styles["disabled-button"]
                                        : ""
                                }`}
                                disabled={
                                    !selectedDoctorId ||
                                    disabledAppointmentButton
                                }
                            >
                                Solicitar turno
                            </button>
                        </form>
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default DashboardPatient;
