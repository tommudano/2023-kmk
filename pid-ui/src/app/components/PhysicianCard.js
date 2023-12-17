import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";

const PhysicianCard = ({
    doctor,
    handleOpenRatingModal,
    handleApprovePhysician,
    handleDenyPhysician,
    approveButtonText = "Aprobar",
    denyButtonText = "Bloquear",
}) => {
    const [buttonDisabled, setButtonDisabled] = useState(false);

    const handleButtonClick = async (callbackToRun, doctor) => {
        setButtonDisabled(true);
        await callbackToRun(doctor);
        setButtonDisabled(false);
    };

    return (
        <div key={doctor.id} className={styles["appointment"]}>
            <div className={styles["subtitle"]}>
                {doctor.first_name + " " + doctor.last_name}
            </div>
            <p
                onClick={() => {
                    handleOpenRatingModal(doctor.id);
                }}
                className={styles["viewScoreButton"]}
            >
                Ver Puntuacion
            </p>
            <p>Especialidad: {doctor.specialty}</p>
            <p>E-mail: {doctor.email}</p>
            <p>Matricula: {doctor.tuition}</p>
            <div className={styles["appointment-buttons-container"]}>
                {handleApprovePhysician ? (
                    <button
                        className={
                            buttonDisabled
                                ? styles["disabled-approve-button"]
                                : styles["approve-button"]
                        }
                        onClick={() =>
                            handleButtonClick(handleApprovePhysician, doctor)
                        }
                        disabled={buttonDisabled}
                    >
                        {approveButtonText}
                    </button>
                ) : null}

                {handleDenyPhysician ? (
                    <button
                        className={
                            buttonDisabled
                                ? styles["disabled-delete-button"]
                                : styles["delete-button"]
                        }
                        onClick={() =>
                            handleButtonClick(handleDenyPhysician, doctor)
                        }
                        disabled={buttonDisabled}
                    >
                        {denyButtonText}
                    </button>
                ) : null}
            </div>
        </div>
    );
};

export default PhysicianCard;
