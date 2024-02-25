"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import styles from "../styles/styles.module.css";
import DatePicker, { registerLocale } from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import es from "date-fns/locale/es";
import Modal from "react-modal";
import axios from "axios";
import https from "https";
import { Footer, Header, TabBar } from "../components/header";
import ConfirmationModal from "../components/ConfirmationModal";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import PatientsAppointment from "../components/PatientsAppointment";

registerLocale("es", es);

const DashboardPatient = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [appointments, setAppointments] = useState([]);
    const [pendingAppointments, setPendingAppointments] = useState([]);
    const [date, setDate] = useState(new Date());
    const [dateToEdit, setDateToEdit] = useState(new Date());
    const [isEditModalOpen, setIsEditModalOpen] = useState(false);
    const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
    const [editingAppointment, setEditingAppointment] = useState({});
    const [showModal, setShowModal] = useState(false);
    const [appointmentIdToDelete, setAppointmentIdToDelete] = useState(null);
    const [appointmentScores, setAppointmentScores] = useState([]);
    const [buttonsDisabledSetter, serButtonsDisabledSetter] = useState(
        () => {}
    );

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const getAppointmentScores = async (id) => {
        try {
            const response = await axios.get(`${apiURL}users/score/${id}`, {
                httpsAgent: agent,
            });
            console.log(response.data.score_metrics);

            let tempReviews = [
                { id: 1, type: "Puntualidad", rating: 5 },
                { id: 2, type: "Atencion", rating: 4.5 },
                { id: 3, type: "Limpieza", rating: 4.5 },
                { id: 4, type: "Disponibilidad", rating: 3 },
                { id: 5, type: "Precio", rating: 4.5 },
                { id: 6, type: "Comunicacion", rating: 2.5 },
            ];

            tempReviews[0].rating = response.data.score_metrics.puntuality;
            tempReviews[1].rating = response.data.score_metrics.attention;
            tempReviews[2].rating = response.data.score_metrics.cleanliness;
            tempReviews[3].rating = response.data.score_metrics.availability;
            tempReviews[4].rating = response.data.score_metrics.price;
            tempReviews[5].rating = response.data.score_metrics.communication;

            if (
                tempReviews[0].rating +
                    tempReviews[1].rating +
                    tempReviews[2].rating +
                    tempReviews[3].rating +
                    tempReviews[4].rating +
                    tempReviews[5].rating ==
                0
            ) {
                setAppointmentScores([]);
            } else {
                setAppointmentScores(tempReviews);
            }
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
        }
    };

    const fetchAppointments = async () => {
        try {
            const response = await axios.get(`${apiURL}appointments/`, {
                httpsAgent: agent,
            });
            response.data.appointments == undefined
                ? setAppointments([])
                : setAppointments(response.data.appointments);
        } catch (error) {
            toast.error("Error al cargar turnos");
            console.error(error);
        }
    };

    const fetchPendingAppointments = async () => {
        try {
            const response = await axios.get(
                `${apiURL}appointments/patients-pending-appointments/`,
                {
                    httpsAgent: agent,
                }
            );
            response.data.appointments == undefined
                ? setPendingAppointments([])
                : setPendingAppointments(response.data.appointments);
        } catch (error) {
            toast.error("Error al cargar turnos");
            console.error(error);
        }
    };

    const handleOpenEditModal = (appointment, setButtonsDisabled) => {
        serButtonsDisabledSetter(() => setButtonsDisabled);
        setEditingAppointment({});
        setIsEditModalOpen(true);
        setEditingAppointment({
            id: appointment.id,
            specialty: appointment.physician.specialty,
            doctor: appointment.physician,
            date: appointment.date,
            patient: appointment.patient,
            agenda: appointment.physician.agenda,
        });
    };

    const handleSaveAppointment = async () => {
        buttonsDisabledSetter(true);
        try {
            await axios.put(
                `${apiURL}appointments/${editingAppointment.id}`,
                {
                    date: Math.round(dateToEdit.getTime() / 1000),
                },
                {
                    httpsAgent: agent,
                }
            );
            fetchAppointments();
            fetchPendingAppointments();
            setIsEditModalOpen(false);
            toast.info("Turno modificado exitosamente");
        } catch (error) {
            console.error(error);
            toast.error("Error al modificar turno");
        }
        buttonsDisabledSetter(false);
    };

    const handleCloseEditModal = () => {
        setIsEditModalOpen(false);
    };

    const handleOpenRatingModal = (doctorId) => {
        getAppointmentScores(doctorId);
        setIsRatingModalOpen(true);

        console.log(doctorId);
        //Logica de fecth review para el doctorID pasado por parametro
    };

    const handleCloseRatingModal = () => {
        setAppointmentScores([]);
        setIsRatingModalOpen(false);
    };

    const handleDeleteClick = (appointmentId, setButtonsDisabled) => {
        serButtonsDisabledSetter(() => setButtonsDisabled);
        setAppointmentIdToDelete(appointmentId);
        setShowModal(true);
    };

    const handleDeleteAppointment = async () => {
        setShowModal(false);
        buttonsDisabledSetter(true);
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
            fetchPendingAppointments();
            setAppointmentIdToDelete(null); // Limpiar el ID del turno después de eliminar
        } catch (error) {
            console.error(error);
            toast.error("Error al eliminar turno");
        }
        buttonsDisabledSetter(false);
    };

    const customStyles = {
        content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -50%)",
        },
    };

    const ratingModalStyles = {
        content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -50%)",
            width: "auto",
        },
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        fetchAppointments();
        fetchPendingAppointments().then(() => setIsLoading(false));
    }, []);

    return (
        <div className={styles.dashboard}>
            {/* Modal de edición */}
            {isEditModalOpen && (
                <Modal
                    ariaHideApp={false}
                    isOpen={isEditModalOpen}
                    onRequestClose={handleCloseEditModal}
                    style={customStyles}
                    contentLabel='Example Modal'
                >
                    {/* Campos de edición de especialidad, médico y fecha */}

                    <div style={{ marginTop: "90px" }} className={styles.form}>
                        <div className={styles["title"]}>Editar Cita</div>

                        {/* Selector de fechas */}
                        <label htmlFor='fecha'>Fechas disponibles:</label>

                        <DatePicker
                            locale='es'
                            selected={dateToEdit}
                            onChange={(date) => {
                                setDate(date);
                                setDateToEdit(date);
                            }}
                            timeCaption='Hora'
                            timeIntervals={30}
                            showPopperArrow={false}
                            showTimeSelect
                            inline
                            filterDate={(date) => {
                                if (
                                    editingAppointment.doctor.agenda
                                        .working_days
                                ) {
                                    if (
                                        editingAppointment.doctor.agenda.working_days.includes(
                                            date.getDay()
                                        )
                                    ) {
                                        let workingHour =
                                            editingAppointment.doctor.agenda.working_hours.filter(
                                                (workingHour) =>
                                                    workingHour.day_of_week ===
                                                    date.getDay()
                                            )[0];
                                        return (
                                            workingHour.start_time !== 0 &&
                                            workingHour.finish_time !== 0
                                        );
                                    }
                                }
                                return false;
                            }}
                            minDate={new Date()}
                            filterTime={(time) => {
                                if (
                                    editingAppointment.doctor.agenda
                                        .appointments &&
                                    !editingAppointment.doctor.agenda.appointments.includes(
                                        Math.round(time.getTime() / 1000)
                                    ) &&
                                    editingAppointment.doctor.agenda
                                        .working_hours &&
                                    time >= new Date()
                                ) {
                                    let workingHour =
                                        editingAppointment.doctor.agenda.working_hours.filter(
                                            (workingHour) =>
                                                workingHour.day_of_week ===
                                                date.getDay()
                                        )[0];
                                    let parsedTime =
                                        time.getHours() +
                                        time.getMinutes() / 60;
                                    return (
                                        workingHour &&
                                        workingHour.start_time &&
                                        workingHour.finish_time &&
                                        workingHour.start_time <= parsedTime &&
                                        workingHour.finish_time > parsedTime
                                    );
                                }
                                return false;
                            }}
                        />
                    </div>

                    {/* Botones de Guardar y Cerrar */}
                    <button
                        className={styles["standard-button"]}
                        onClick={() => {
                            handleSaveAppointment();
                        }}
                    >
                        Guardar
                    </button>
                    <button
                        className={styles["standard-button"]}
                        onClick={() => {
                            handleCloseEditModal();
                            console.log(editingAppointment);
                        }}
                    >
                        Cerrar
                    </button>
                </Modal>
            )}

            {/* Modal de ratings */}
            {isRatingModalOpen && (
                <Modal
                    ariaHideApp={false}
                    isOpen={isRatingModalOpen}
                    onRequestClose={handleCloseRatingModal}
                    style={ratingModalStyles}
                    contentLabel='Example Modal'
                >
                    <div
                        key={appointmentScores.key}
                        className={styles["reviews-container"]}
                    >
                        {appointmentScores.length > 0 ? (
                            <>
                                {appointmentScores.map((review) => (
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

            <TabBar highlight='Turnos' />

            <Header role='patient' />

            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Mis Turnos Vigentes
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    fetchAppointments();
                                    toast.info(
                                        "Actualizando turnos vigentes..."
                                    );
                                }}
                            />
                            <div className={styles["appointments-section"]}>
                                {appointments.length > 0 ? (
                                    <div>
                                        {/* ... */}
                                        {appointments.map((appointment) => (
                                            <PatientsAppointment
                                                key={appointment.id}
                                                appointment={appointment}
                                                handleDeleteClick={
                                                    handleDeleteClick
                                                }
                                                handleOpenEditModal={
                                                    handleOpenEditModal
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

                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Turnos Pendientes de Aprobacion
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    fetchPendingAppointments();
                                    toast.info(
                                        "Actualizando turnos pendientes..."
                                    );
                                }}
                            />
                            <div className={styles["appointments-section"]}>
                                {pendingAppointments.length > 0 ? (
                                    <div>
                                        {/* ... */}
                                        {pendingAppointments.map(
                                            (appointment) => (
                                                <PatientsAppointment
                                                    appointment={appointment}
                                                    handleOpenRatingModal={
                                                        handleOpenRatingModal
                                                    }
                                                    key={appointment.id}
                                                />
                                            )
                                        )}
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

export default DashboardPatient;
