"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import styles from "../styles/styles.module.css";
import "react-datepicker/dist/react-datepicker.css";
import Modal from "react-modal";
import axios from "axios";
import https from "https";
import { Header, Footer, PhysicianTabBar } from "../components/header";
import ConfirmationModal from "../components/ConfirmationModal";
import { redirect } from "../components/userCheck";
import { toast } from "react-toastify";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";
import PhysiciansAppointment from "../components/PhysiciansAppointment";

const PhysicianAgenda = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [appointments, setAppointments] = useState([]);
    const [isAddObservationModalOpen, setIsAddObervationModalOpen] =
        useState(false);
    const [patientId, setPatientId] = useState("");
    const [startTime, setStartTime] = useState("");
    const [newObservationContent, setNewObservationContent] = useState("");
    const [appointmentAttended, setAppointmentAttended] = useState(true);
    const [appointmentToClose, setAppointmentToClose] = useState("");
    const [showModal, setShowModal] = useState(false);
    const [appointmentIdToDelete, setAppointmentIdToDelete] = useState(null);
    const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
    const [patientScores, setPatientScores] = useState([]);
    const [buttonsDisabledSetter, setButtonsDisabledSetter] = useState(
        () => {}
    );
    const [disabledCloseAppointmentButton, setDisabledCloseAppointmentButton] =
        useState(false);

    const [reviews, setReviews] = useState({
        puntuality: {
            name: "Puntualidad",
            rating: -1,
        },
        cleanliness: {
            name: "Limpieza",
            rating: -1,
        },
        attendance: {
            name: "Asistencia",
            rating: -1,
        },
        treat: {
            name: "Trato",
            rating: -1,
        },
        communication: {
            name: "Comunicacion",
            rating: -1,
        },
    });

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const getPatientScores = async (id) => {
        try {
            const response = await axios.get(`${apiURL}users/score/${id}`, {
                httpsAgent: agent,
            });
            console.log(response.data.score_metrics);

            let tempReviews = [
                { id: 1, type: "Puntualidad", rating: 0 },
                { id: 2, type: "Asistencia", rating: 0 },
                { id: 3, type: "Limpieza", rating: 0 },
                { id: 4, type: "Trato", rating: 0 },
                { id: 5, type: "Comunicacion", rating: 0 },
            ];

            tempReviews[0].rating = response.data.score_metrics.puntuality;
            tempReviews[1].rating = response.data.score_metrics.attendance;
            tempReviews[2].rating = response.data.score_metrics.cleanliness;
            tempReviews[3].rating = response.data.score_metrics.treat;
            tempReviews[4].rating = response.data.score_metrics.communication;

            setPatientScores([...tempReviews]);
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
        }
    };

    const handleOpenRatingModal = (patientId) => {
        getPatientScores(patientId);
        setIsRatingModalOpen(true);
    };

    const handleCloseRatingModal = () => {
        setPatientScores([]);
        setIsRatingModalOpen(false);
    };

    const fetchAppointments = async () => {
        try {
            const response = await axios.get(
                `${apiURL}appointments/physician`,
                {
                    httpsAgent: agent,
                }
            );
            response.data.appointments == undefined
                ? setAppointments([])
                : setAppointments(response.data.appointments);
        } catch (error) {
            toast.error("Error al obtener los turnos");
            console.error(error);
        }
    };

    const handleOpenAppointmentClosureModal = (
        appointment,
        setButtonsDisabled
    ) => {
        setButtonsDisabledSetter(() => setButtonsDisabled);
        setIsAddObervationModalOpen(true);
        setAppointmentToClose(appointment);
        setPatientId(appointment.patient.id);
    };

    const handleAppointmentClosure = async () => {
        buttonsDisabledSetter(true);
        setDisabledCloseAppointmentButton(true);
        console.log(appointmentToClose.id);
        console.log(appointmentAttended);
        console.log(startTime);
        let hour = startTime.split(":")[0];
        let minutes = startTime.split(":")[1];
        let date = new Date();
        date.setHours(hour);
        date.setMinutes(minutes);
        console.log((date.getTime() / 1000).toString());

        try {
            const response = await axios.put(
                `${apiURL}appointments/close-appointment/${appointmentToClose.id}`,
                {
                    attended: appointmentAttended,
                    start_time: (date.getTime() / 1000).toString(),
                },
                {
                    httpsAgent: agent,
                }
            );
        } catch (error) {
            toast.error("Error al cerrar el turno");
            console.error(error);
        }

        try {
            const response = await axios.post(
                `${apiURL}records/update`,
                {
                    appointment_id: appointmentToClose.id,
                    attended: appointmentAttended.toString(),
                    real_start_time: (date.getTime() / 1000).toString(),
                    observation: newObservationContent,
                },
                {
                    httpsAgent: agent,
                }
            );
            toast.info("Turno cerrado exitosamente");
            fetchAppointments();
            setIsAddObervationModalOpen(false);
        } catch (error) {
            toast.error("Error al agregar la observación");
            console.error(error);
        }
        try {
            let reviewsToSend = {};
            Object.keys(reviews).forEach((review) => {
                if (reviews[review].rating >= 0)
                    reviewsToSend[review] = reviews[review].rating;
            });
            console.log(reviewsToSend);
            const response = await axios.post(
                `${apiURL}users/add-score`,
                {
                    appointment_id: appointmentToClose.id,
                    ...reviewsToSend,
                },
                {
                    httpsAgent: agent,
                }
            );
            toast.info("Puntaje cargado exitosamente");
        } catch (error) {
            toast.error("Error al agregar la puntaje");
            console.error(error);
        }
        setDisabledCloseAppointmentButton(false);
        buttonsDisabledSetter(false);
    };

    const handleDeleteClick = (appointmentId, setDisabledButtons) => {
        setButtonsDisabledSetter(() => setDisabledButtons);
        setAppointmentIdToDelete(appointmentId);
        setShowModal(true);
    };

    const handleDeleteAppointment = async () => {
        buttonsDisabledSetter(true);
        setShowModal(false);
        toast.info("Eliminando turno...");
        try {
            await axios.delete(
                `${apiURL}appointments/${appointmentIdToDelete}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Turno eliminado exitosamente");
            fetchAppointments();
            setAppointmentIdToDelete(null); // Limpiar el ID del turno después de eliminar
        } catch (error) {
            console.error(error);
            toast.error("Error al eliminar turno");
        }
        buttonsDisabledSetter(false);
    };

    const handleCloseEditModal = () => {
        setIsAddObervationModalOpen(false);
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        fetchAppointments()
            .then(() => setIsLoading(false)) // Marcar como cargado cuando la respuesta llega
            .catch(() => {
                setIsLoading(false); // Asegúrate de marcar como cargado en caso de error
            });
    }, []);

    const ratingModalStyles = {
        content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -30%)",
            width: "80%",
        },
    };

    return (
        <div className={styles.dashboard}>
            {isRatingModalOpen && (
                <Modal
                    ariaHideApp={false}
                    isOpen={isRatingModalOpen}
                    onRequestClose={handleCloseRatingModal}
                    style={ratingModalStyles}
                    contentLabel='Example Modal'
                >
                    <div
                        key={patientScores.key}
                        className={styles["reviews-container"]}
                    >
                        {patientScores.length > 0 ? (
                            <>
                                {patientScores.map((review) => (
                                    <div
                                        key={review.id}
                                        className={styles["review"]}
                                    >
                                        <div
                                            className={
                                                styles["review-cards-container"]
                                            }
                                        >
                                            <div
                                                className={
                                                    styles["review-card"]
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
                            <label>No hay reviews</label>
                        )}
                    </div>

                    {/* Botones de Guardar y Cerrar */}
                    <button
                        className={styles["standard-button"]}
                        onClick={() => handleCloseRatingModal()}
                    >
                        Cerrar
                    </button>
                </Modal>
            )}
            {isAddObservationModalOpen && (
                <Modal
                    ariaHideApp={false}
                    isOpen={isAddObservationModalOpen}
                    onRequestClose={handleCloseEditModal}
                    style={{
                        content: {
                            height: "70%",
                            transform: "translate(0px, 30%)",
                        },
                    }}
                >
                    <div
                        className={styles["new-record-section"]}
                        onSubmit={handleAppointmentClosure}
                    >
                        <div className={styles["title"]}>Gestion del Turno</div>
                        <div className={styles["appointment"]}>
                            <div className={styles["subtitle"]}>
                                El paciente fue atendido?
                            </div>
                            <select
                                className={styles["select"]}
                                name='attended'
                                id='attended'
                                onChange={(e) => {
                                    setAppointmentAttended(
                                        e.target.value === "true"
                                    );
                                }}
                            >
                                <option value={true}>Si</option>
                                <option value={false}>No</option>
                            </select>

                            <div className={styles["subtitle"]}>
                                Horario real de atencion:{" "}
                            </div>

                            <input
                                type='time'
                                id='time'
                                name='time'
                                onChange={(date) => {
                                    setStartTime(date.target.value.toString());
                                    console.log(date.target.value.toString());
                                }}
                                disabled={appointmentAttended === false}
                                required={appointmentAttended === true}
                                className={`${
                                    appointmentAttended === false
                                        ? styles["disabled-input"]
                                        : ""
                                }`}
                            />

                            <div className={styles["subtitle"]}>
                                Observaciones
                            </div>

                            <textarea
                                id='observation'
                                value={newObservationContent}
                                onChange={(e) => {
                                    console.log(e.target.value);
                                    setNewObservationContent(e.target.value);
                                }}
                                placeholder='Escribe una nueva observación'
                                required={appointmentAttended === true}
                                className={`${styles["observation-input"]} ${
                                    appointmentAttended === false
                                        ? styles["disabled-input"]
                                        : ""
                                }`}
                                wrap='soft'
                                disabled={appointmentAttended === false}
                            />
                        </div>

                        <div
                            key={reviews.key}
                            className={styles["reviews-container"]}
                        >
                            {Object.keys(reviews).length > 0 ? (
                                <>
                                    {Object.keys(reviews).map((review) => (
                                        <div
                                            key={review}
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
                                                        styles["review-card"]
                                                    }
                                                >
                                                    <div
                                                        className={
                                                            styles[
                                                                "review-card-title"
                                                            ]
                                                        }
                                                    >
                                                        {reviews[review].name}
                                                    </div>
                                                    <div
                                                        className={
                                                            styles[
                                                                "review-card-content"
                                                            ]
                                                        }
                                                    >
                                                        <select
                                                            onChange={(e) =>
                                                                setReviews({
                                                                    ...reviews,
                                                                    [review]: {
                                                                        name: reviews[
                                                                            review
                                                                        ].name,
                                                                        rating: Number(
                                                                            e
                                                                                .target
                                                                                .value
                                                                        ),
                                                                    },
                                                                })
                                                            }
                                                        >
                                                            <option value={-1}>
                                                                N/A
                                                            </option>
                                                            <option value={0}>
                                                                Muy Malo
                                                            </option>
                                                            <option value={1}>
                                                                Malo
                                                            </option>
                                                            <option value={2}>
                                                                Neutro
                                                            </option>
                                                            <option value={3}>
                                                                Bueno
                                                            </option>
                                                            <option value={4}>
                                                                Muy Bueno
                                                            </option>
                                                            <option value={5}>
                                                                Excelente
                                                            </option>
                                                        </select>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </>
                            ) : (
                                // If there are no reviews, display the message
                                <div className={styles["subtitle"]}>
                                    No hay reviews
                                </div>
                            )}
                        </div>

                        <button
                            className={`${styles["edit-button"]} ${
                                (!newObservationContent &&
                                    appointmentAttended === true) ||
                                (!startTime && appointmentAttended === true) ||
                                disabledCloseAppointmentButton
                                    ? styles["disabled-button"]
                                    : ""
                            }`}
                            onClick={handleAppointmentClosure}
                            disabled={
                                (!newObservationContent &&
                                    appointmentAttended === true) ||
                                (!startTime && appointmentAttended === true) ||
                                disabledCloseAppointmentButton
                            }
                        >
                            Agregar
                        </button>
                    </div>
                </Modal>
            )}

            <PhysicianTabBar highlight={"TurnosActivos"} />

            <Header role='physician' />

            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Turnos Activos
                                <Tooltip
                                    title='En este panel se mostraran los turnos activos; estos son turnos que aun no han sido iniciados o que no han sido cerrados.'
                                    placement='right'
                                >
                                    <IconButton>
                                        <InfoIcon />
                                    </IconButton>
                                </Tooltip>
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Refrescar'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando...");
                                    fetchAppointments();
                                }}
                            />
                            <div className={styles["appointments-section"]}>
                                {appointments.length > 0 ? (
                                    // If there are appointments, map through them and display each appointment
                                    <div>
                                        {/* ... */}
                                        {appointments.map((appointment) => (
                                            <PhysiciansAppointment
                                                appointment={appointment}
                                                handleDeleteClick={
                                                    handleDeleteClick
                                                }
                                                handleOpenAppointmentClosureModal={
                                                    handleOpenAppointmentClosureModal
                                                }
                                                handleOpenRatingModal={
                                                    handleOpenRatingModal
                                                }
                                            />
                                        ))}
                                    </div>
                                ) : (
                                    // If there are no appointments, display the message
                                    <div className={styles["subtitle"]}>
                                        No hay turnos pendientes
                                    </div>
                                )}
                                {/* ... */}
                            </div>
                            {/* Modal de confirmación */}
                            <ConfirmationModal
                                isOpen={showModal}
                                closeModal={() => setShowModal(false)}
                                confirmAction={handleDeleteAppointment}
                                message='¿Estás seguro de que deseas cancelar este turno?'
                            />
                        </div>
                    </div>

                    <Footer />
                </>
            )}
        </div>
    );
};

export default PhysicianAgenda;
