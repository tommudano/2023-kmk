"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import styles from "../../styles/styles.module.css";
import "react-datepicker/dist/react-datepicker.css";
import Modal from "react-modal";
import axios from "axios";
import https from "https";
import { Footer, Header, TabBar } from "../../components/header";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { add } from "date-fns";

const DashboardPatient = () => {
    const [isLoading, setIsLoading] = useState(false);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [appointments, setAppointments] = useState([]);
    const [isReviewModalOpen, setIsAddObervationModalOpen] = useState(false);
    const [appointmentToReview, setAppointmentToReview] = useState("");
    const [appointmentScores, setAppointmentScores] = useState([]);
    const [disabledAddReviewButton, setDisabledAddReiewButton] =
        useState(false);
    const router = useRouter();
    const delay = (ms) => new Promise((res) => setTimeout(res, ms));
    const [reviews, setReviews] = useState({
        puntuality: {
            name: "Puntualidad",
            rating: -1,
        },
        attention: {
            name: "Atencion",
            rating: -1,
        },
        cleanliness: {
            name: "Limpieza",
            rating: -1,
        },
        availability: {
            name: "Disponibilidad",
            rating: -1,
        },
        price: {
            name: "Precio",
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

    const fetchPendingReviews = async () => {
        try {
            const response = await axios.get(
                `${apiURL}users/patient-pending-scores`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data);
            setAppointments(response.data.pending_scores);
            if (response.data.pending_scores.length === 0) {
                router.push("/patient-dashboard");
            }
        } catch (error) {
            toast.error("Error al obtener las reseñas pendientes");
            console.error(error);
        }
    };

    const handleOpenReviewModal = (appointment) => {
        setAppointmentToReview(appointment);
        setIsAddObervationModalOpen(true);
    };

    const handleCloseReviewModal = () => {
        setIsAddObervationModalOpen(false);
    };

    const addReview = async () => {
        setDisabledAddReiewButton(true);
        try {
            let reviewsToSend = {};
            Object.keys(reviews).forEach((review) => {
                if (reviews[review].rating >= 0)
                    reviewsToSend[review] = reviews[review].rating;
            });
            const response = await axios.post(
                `${apiURL}users/add-score`,
                { ...reviewsToSend, appointment_id: appointmentToReview.id },
                {
                    httpsAgent: agent,
                }
            );
            toast.info("Puntaje cargado exitosamente");
            await delay(5000);
            fetchPendingReviews();
        } catch (error) {
            toast.error("Error al agregar la puntaje");
            console.error(error);
        }
        setDisabledAddReiewButton(false);
    };

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

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        fetchPendingReviews();
    }, []);

    return (
        <>
            {isReviewModalOpen && (
                <Modal
                    ariaHideApp={false}
                    isOpen={isReviewModalOpen}
                    onRequestClose={handleCloseReviewModal}
                    style={ratingModalStyles}
                >
                    <div className={styles["new-record-section"]}>
                        <div className={styles["title"]}>Carga de Reseña</div>

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
                                disabledAddReviewButton
                                    ? styles["disabled-button"]
                                    : ""
                            }`}
                            onClick={addReview}
                            disabled={disabledAddReviewButton}
                        >
                            Agregar
                        </button>
                    </div>
                </Modal>
            )}

            <div className={styles.dashboard}>
                <TabBar highlight='SolicitarTurnos' />

                <Header role='patient' />

                {isLoading ? (
                    <p>Cargando...</p>
                ) : (
                    <>
                        <div className={styles["tab-content"]}>
                            <div className={styles.form}>
                                <div className={styles["title"]}>
                                    Turnos pendientes de reseña
                                </div>
                                <div className={styles["subtitle"]}>
                                    Usted tiene {appointments.length} turno
                                    {appointments.length === 1 ? " " : "s "}
                                    pendientes de reseña.
                                </div>
                                <div className={styles["subtitle"]}>
                                    Por favor, seleccione un turno para dejar su
                                    reseña; una vez que haya completado todas
                                    sus reseñas podrá volver al menu principal y
                                    solicitar un turno nuevo.
                                </div>

                                <Image
                                    src='/refresh_icon.png'
                                    alt='Notificaciones'
                                    className={styles["refresh-icon"]}
                                    width={200}
                                    height={200}
                                    onClick={() => {
                                        fetchPendingReviews();
                                        toast.info("Actualizando turnos...");
                                    }}
                                />
                                <div className={styles["appointments-section"]}>
                                    {appointments.length > 0 ? (
                                        <div>
                                            {appointments.map((appointment) => (
                                                <div
                                                    key={appointment.id}
                                                    className={
                                                        styles["appointment"]
                                                    }
                                                >
                                                    <div
                                                        className={
                                                            styles["subtitle"]
                                                        }
                                                    >
                                                        {appointment.specialty
                                                            .charAt(0)
                                                            .toUpperCase() +
                                                            appointment.specialty.slice(
                                                                1
                                                            )}
                                                    </div>
                                                    <p>
                                                        Profesional:{" "}
                                                        {appointment.first_name +
                                                            " " +
                                                            appointment.last_name}
                                                    </p>

                                                    <p>
                                                        Fecha y hora:{" "}
                                                        {new Date(
                                                            appointment.date *
                                                                1000
                                                        ).toLocaleString(
                                                            "es-AR"
                                                        )}
                                                    </p>
                                                    <div
                                                        className={
                                                            styles[
                                                                "appointment-buttons-container"
                                                            ]
                                                        }
                                                    >
                                                        <button
                                                            className={
                                                                styles[
                                                                    "edit-button"
                                                                ]
                                                            }
                                                            onClick={() =>
                                                                handleOpenReviewModal(
                                                                    appointment
                                                                )
                                                            }
                                                        >
                                                            Agregar reseña
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        // If there are no appointments, display the message
                                        <div className={styles["subtitle"]}>
                                            No hay turnos pendientes
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                        <Footer />
                    </>
                )}
            </div>
        </>
    );
};

export default DashboardPatient;
