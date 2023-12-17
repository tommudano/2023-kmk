import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";

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
