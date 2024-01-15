"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import styles from "../styles/styles.module.css";
import "react-datepicker/dist/react-datepicker.css";
import axios from "axios";
import https from "https";
import { Header, Footer, PhysicianTabBar } from "../components/header";
import ConfirmationModal from "../components/ConfirmationModal";
import { toast } from "react-toastify";
import PhysiciansAppointment from "../components/PhysiciansAppointment";
import Modal from "react-modal";

const PhysicianPendingAppointments = () => {
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [appointments, setAppointments] = useState([]);
    const [showModal, setShowModal] = useState(false);
    const [appointmentIdToDeny, setAppointmentIdToDeny] = useState(null);
    const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
    const [patientScores, setPatientScores] = useState([]);
    const [buttonsDisabledSetter, setButtonsDisabledSetter] = useState(
        () => {}
    );

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
                `${apiURL}physicians/pending-appointments`
            );
            response.data.appointments == undefined
                ? setAppointments([])
                : setAppointments(response.data.appointments);
        } catch (error) {
            toast.error("Error al obtener los turnos");
            console.log(error);
        }
    };

    const handleApproveAppointment = async (
        appointmentId,
        setButtonsDisabled
    ) => {
        console.log(appointmentId);
        setButtonsDisabled(true);
        toast.info("Aprobando turno...");
        try {
            await axios.post(
                `${apiURL}physicians/approve-appointment/${appointmentId}`
            );
            toast.success("Turno aprobado exitosamente");
            fetchAppointments();
        } catch (error) {
            console.log(error);
        }
        setButtonsDisabled(false);
    };

    const handleDenyClick = (appointmentId, setButtonsDisabled) => {
        setButtonsDisabledSetter(() => setButtonsDisabled);
        setAppointmentIdToDeny(appointmentId);
        setShowModal(true);
    };

    const handleDenyAppointment = async () => {
        buttonsDisabledSetter(true);
        setShowModal(false);
        toast.info("Rechazando turno...");
        try {
            await axios.delete(`${apiURL}appointments/${appointmentIdToDeny}`, {
                httpsAgent: agent,
            });
            toast.success("Turno rechazado exitosamente");
            fetchAppointments();
        } catch (error) {
            console.log(error);
            toast.error("Error al rechazar turno");
        }
        buttonsDisabledSetter(false);
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        fetchAppointments()
            .then(() => setIsLoading(false)) // Marcar como cargado cuando la respuesta llega
            .catch(() => {
                setIsLoading(false); // Asegúrate de marcar como cargado en caso de error
                toast.error("Error al obtener los datos del usuario");
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

            <PhysicianTabBar highlight={"TurnosPorAprobar"} />

            <Header role='physician' />

            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Turnos solicitados sin confirmar
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando turnos...");
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
                                                handleApproveAppointment={
                                                    handleApproveAppointment
                                                }
                                                handleDenyClick={
                                                    handleDenyClick
                                                }
                                                handleOpenRatingModal={
                                                    handleOpenRatingModal
                                                }
                                                key={appointment.id}
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
                                confirmAction={handleDenyAppointment}
                                message='¿Estás seguro de que deseas rechazar este turno?'
                            />
                        </div>
                    </div>

                    <Footer />
                </>
            )}
        </div>
    );
};

export default PhysicianPendingAppointments;
