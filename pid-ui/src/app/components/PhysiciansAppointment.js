import Link from "next/link";
import styles from "../styles/styles.module.css";
import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faVideo } from "@fortawesome/free-solid-svg-icons";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

const PhysiciansAppointment = ({
    appointment,
    handleOpenAppointmentClosureModal,
    handleDeleteClick,
    handleApproveAppointment,
    handleDenyClick,
    handleOpenRatingModal,
}) => {
    const [buttonsDisabled, setButtonsDisabled] = useState(false);
    return (
        <div key={appointment.id} className={styles["appointment"]}>
            <div className={styles["subtitle"]}>
                Paciente:{" "}
                {appointment.patient.first_name +
                    " " +
                    appointment.patient.last_name}
                <a
                    onClick={() => {
                        handleOpenRatingModal(appointment.patient.id);
                    }}
                    className={styles["viewScoreButton"]}
                >
                    {"    "} (Ver Puntuacion)
                </a>
            </div>
            <p>
                Fecha y hora:{" "}
                {new Date(appointment.date * 1000).toLocaleString("es-AR")}
            </p>
            <p>Valor de la consulta: ${appointment.appointment_value}</p>

            {appointment.google_meet_conference ? (
                <p style={{ fontStyle: "italic" }}>
                    {" "}
                    <FontAwesomeIcon
                        icon={faVideo}
                        className={styles["meet-icon"]}
                    />
                    Esta consulta es a traves de Google Meet
                    <Tooltip
                        title='La sala de reuniones estara habilitada 15 minutos antes de la consulta.'
                        placement='right'
                    >
                        <IconButton>
                            <InfoIcon />
                        </IconButton>
                    </Tooltip>
                </p>
            ) : null}
            <div className={styles["appointment-buttons-container"]}>
                {handleOpenAppointmentClosureModal ? (
                    <button
                        className={
                            buttonsDisabled
                                ? styles["disabled-edit-button"]
                                : styles["standard-button"]
                        }
                        onClick={() => {
                            handleOpenAppointmentClosureModal(
                                appointment,
                                setButtonsDisabled
                            );
                        }}
                        disabled={buttonsDisabled}
                    >
                        Finalizar Turno
                    </button>
                ) : null}
                {handleOpenAppointmentClosureModal ? (
                    <Link
                        href={{
                            pathname: buttonsDisabled
                                ? "#"
                                : "/medical-records?patientId",
                            query: appointment.patient.id,
                        }}
                        as={`medical-records?patientId=${appointment.patient.id}`}
                    >
                        <button
                            className={
                                buttonsDisabled
                                    ? styles["disabled-edit-button"]
                                    : styles["standard-button"]
                            }
                            disabled={buttonsDisabled}
                        >
                            Ver Historia Clinica
                        </button>
                    </Link>
                ) : null}

                {handleOpenAppointmentClosureModal && appointment.meet_link ? (
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

                {handleApproveAppointment ? (
                    <button
                        className={
                            buttonsDisabled
                                ? styles["disabled-approve-button"]
                                : styles["approve-button"]
                        }
                        onClick={() =>
                            handleApproveAppointment(
                                appointment.id,
                                setButtonsDisabled
                            )
                        }
                        disabled={buttonsDisabled}
                    >
                        Confirmar{" "}
                    </button>
                ) : null}

                {handleDenyClick ? (
                    <button
                        className={
                            buttonsDisabled
                                ? styles["disabled-delete-button"]
                                : styles["delete-button"]
                        }
                        onClick={() =>
                            handleDenyClick(appointment.id, setButtonsDisabled)
                        }
                        disabled={buttonsDisabled}
                    >
                        Rechazar
                    </button>
                ) : null}
            </div>
        </div>
    );
};

export default PhysiciansAppointment;
