import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faVideo } from "@fortawesome/free-solid-svg-icons";
import Link from "next/link";

const PatientsAppointment = ({
    appointment,
    handleOpenRatingModal,
    handleOpenEditModal,
    handleDeleteClick,
}) => {
    const [buttonsDisabled, setButtonsDisabled] = useState(false);
    return (
        <div key={appointment.id} className={styles["appointment"]}>
            <div className={styles["subtitle"]}>
                {appointment.physician.specialty.charAt(0).toUpperCase() +
                    appointment.physician.specialty.slice(1)}
            </div>
            <p>
                Profesional:{" "}
                {appointment.physician.first_name +
                    " " +
                    appointment.physician.last_name}
                <a
                    onClick={() => {
                        handleOpenRatingModal(appointment.physician.id);
                    }}
                    className={styles["viewScoreButton"]}
                >
                    {"    "} (Ver Puntuacion)
                </a>
            </p>

            <p>
                Fecha y hora:{" "}
                {new Date(appointment.date * 1000).toLocaleString("es-AR")}
            </p>

            <p>Costo de la consulta: ${appointment.appointment_value}</p>

            {appointment.google_meet_conference ? (
                <p style={{ fontStyle: "italic" }}>
                    {" "}
                    <FontAwesomeIcon
                        icon={faVideo}
                        className={styles["meet-icon"]}
                    />
                    Esta consulta es a traves de Google Meet{" "}
                </p>
            ) : null}
            <div className={styles["appointment-buttons-container"]}>
                {handleOpenEditModal ? (
                    <button
                        className={
                            buttonsDisabled
                                ? styles["disabled-edit-button"]
                                : styles["edit-button"]
                        }
                        onClick={() =>
                            handleOpenEditModal(appointment, setButtonsDisabled)
                        }
                        disabled={buttonsDisabled}
                    >
                        Modificar
                    </button>
                ) : null}
                {handleOpenEditModal && appointment.meet_link ? (
                    <Link href={appointment.meet_link} target='_blank'>
                        <button className={styles["meet-button"]}>
                            Unirse con Google Meet
                        </button>
                    </Link>
                ) : null}
                {handleDeleteClick ? (
                    <button
                        className={
                            buttonsDisabled
                                ? styles["disabled-delete-button"]
                                : styles["delete-button"]
                        }
                        onClick={() =>
                            handleDeleteClick(
                                appointment.id,
                                setButtonsDisabled
                            )
                        }
                        disabled={buttonsDisabled}
                    >
                        Cancelar
                    </button>
                ) : null}
            </div>
        </div>
    );
};

export default PatientsAppointment;
