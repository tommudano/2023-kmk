"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "../styles/styles.module.css";
import subTabStyles from "../styles/subTab.module.css";
import axios from "axios";
import https from "https";
import validator from "validator";
import { Footer, Header, PhysicianTabBar } from "../components/header";
import { toast } from "react-toastify";
import ValueModal from "../components/ValueModal";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

const UserProfile = () => {
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [physicianScores, setPhysicianScores] = useState([]);
    const [user, setUser] = useState({
        firstName: "",
        lastName: "",
        email: "",
        bloodtype: "",
        agenda: {
            working_days: [0, 1, 2, 3, 4, 5, 6],
            working_hours: [
                { day_of_week: 0, start_time: 0, finish_time: 0 },
                { day_of_week: 1, start_time: 0, finish_time: 0 },
                { day_of_week: 2, start_time: 0, finish_time: 0 },
                { day_of_week: 3, start_time: 0, finish_time: 0 },
                { day_of_week: 4, start_time: 0, finish_time: 0 },
                { day_of_week: 5, start_time: 0, finish_time: 0 },
                { day_of_week: 6, start_time: 0, finish_time: 0 },
            ],
            appointments: [],
        },
    });
    const [password, setPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [error, setError] = useState("");
    const [activeSubTab, setActiveSubTab] = useState("tab1");
    const [showValueModal, setShowValueModal] = useState(false);
    const [newValue, setNewValue] = useState(undefined);
    const [googleMeetServiceEnabled, setGoogleMeetServiceEnabled] =
        useState(false);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const getPhysicianScores = async (id) => {
        try {
            const response = await axios.get(`${apiURL}users/score/${id}`, {
                httpsAgent: agent,
            });
            console.log(response.data.score_metrics);

            let reviews = [
                { id: 1, type: "Puntualidad" },
                { id: 2, type: "Atencion" },
                { id: 3, type: "Limpieza" },
                { id: 4, type: "Disponibilidad" },
                { id: 5, type: "Precio" },
                { id: 6, type: "Comunicacion" },
            ];

            reviews[0].rating = response.data.score_metrics.puntuality;
            reviews[1].rating = response.data.score_metrics.attention;
            reviews[2].rating = response.data.score_metrics.cleanliness;
            reviews[3].rating = response.data.score_metrics.availability;
            reviews[4].rating = response.data.score_metrics.price;
            reviews[5].rating = response.data.score_metrics.communication;
            setPhysicianScores([...reviews]);
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
        }
    };

    const getUserData = async () => {
        try {
            const response = await axios.get(`${apiURL}users/user-info`, {
                httpsAgent: agent,
            });

            console.log("RESPONSE", response);

            const userData = {
                firstName: response.data.first_name,
                lastName: response.data.last_name,
                email: response.data.email,
                agenda: user.agenda,
                id: response.data.id,
                specialty: response.data.specialty,
                appointment_value: response.data.appointment_value,
            };

            response.data.agenda.working_hours.forEach((element) => {
                userData.agenda.working_hours[element.day_of_week].start_time =
                    element.start_time;
                userData.agenda.working_hours[element.day_of_week].finish_time =
                    element.finish_time;
                userData.agenda.working_hours[element.day_of_week].day_of_week =
                    element.day_of_week;
            });

            console.log(userData);

            setUser(userData);
            setGoogleMeetServiceEnabled(
                response.data.google_meet_conference_enabled
            );
            getPhysicianScores(userData.id);
        } catch (error) {
            console.error(error);
            toast.error("Error al obtener los datos del usuario");
        }
    };

    const addTimeToAgenda = (day) => {};

    const removeTimeFromAgenda = (day) => {
        user.agenda.working_hours.map((item) => {
            if (item.day_of_week == day) {
                item.start_time = 0;
                item.finish_time = 0;
            }
        });
    };

    const convertTime = (time) => {
        let hours = Math.floor(time);
        let minutes = (time - hours) * 60;

        if (hours < 10) {
            hours = `0${hours}`;
        }

        if (minutes < 10) {
            minutes = `0${minutes}`;
        }
        return `${hours}:${minutes}`;
    };

    const convertTimeForAPI = (time) => {
        let hours = time.split(":")[0];
        let minutes = time.split(":")[1];

        return parseInt(hours) + parseInt(minutes) / 60;
    };

    const convertDay = (day) => {
        switch (day) {
            case 1:
                return "Lunes";
            case 2:
                return "Martes";
            case 3:
                return "Miércoles";
            case 4:
                return "Jueves";
            case 5:
                return "Viernes";
            case 6:
                return "Sábado";
            case 0:
                return "Domingo";
        }
    };

    const handleStartTimeChange = (day, time) => {
        user.agenda.working_hours.map((item) => {
            if (item.day_of_week == day) {
                item.start_time = convertTimeForAPI(time);
            }
        });
    };

    const handleFinishTimeChange = (day, time) => {
        user.agenda.working_hours.map((item) => {
            if (item.day_of_week == day) {
                item.finish_time = convertTimeForAPI(time);
            }
        });
    };

    const handleSaveChanges = async () => {
        try {
            let payload1 = {
                start: user.agenda.working_hours[1].start_time,
                finish: user.agenda.working_hours[1].finish_time,
            };
            let payload2 = {
                start: user.agenda.working_hours[2].start_time,
                finish: user.agenda.working_hours[2].finish_time,
            };
            let payload3 = {
                start: user.agenda.working_hours[3].start_time,
                finish: user.agenda.working_hours[3].finish_time,
            };
            let payload4 = {
                start: user.agenda.working_hours[4].start_time,
                finish: user.agenda.working_hours[4].finish_time,
            };
            let payload5 = {
                start: user.agenda.working_hours[5].start_time,
                finish: user.agenda.working_hours[5].finish_time,
            };
            let payload6 = {
                start: user.agenda.working_hours[6].start_time,
                finish: user.agenda.working_hours[6].finish_time,
            };
            let payload0 = {
                start: user.agenda.working_hours[0].start_time,
                finish: user.agenda.working_hours[0].finish_time,
            };
            const response = await axios.put(`${apiURL}physicians/agenda`, {
                agenda: {
                    0: payload0,
                    1: payload1,
                    2: payload2,
                    3: payload3,
                    4: payload4,
                    5: payload5,
                    6: payload6,
                },
                google_meet_conference_enabled: googleMeetServiceEnabled,
            });
            getUserData();
            toast.success("Horario de atención actualizado exitosamente.");
        } catch (error) {
            console.error(error);
            toast.error("Error al actualizar el horario de atención.");
        }
    };

    const validate = (value) => {
        if (
            validator.isStrongPassword(value, {
                minLength: 8,
                minLowercase: 1,
                minUppercase: 1,
                minNumbers: 1,
                minSymbols: 0,
            })
        ) {
            setError("");
        } else {
            toast.error(
                "La contraseña no es lo suficientemente fuerte: debe incluir al menos 8 caracteres, 1 minúscula, 1 mayúscula y 1 número"
            );
        }
    };

    const handleChangePassword = async (e) => {
        e.preventDefault();
        if (newPassword !== confirmNewPassword) {
            toast.error("Las contraseñas no coinciden.");
            return;
        }

        validate(newPassword);

        try {
            // Realiza una solicitud a la API para cambiar la contraseña
            await axios.post(`${apiURL}users/change-password`, {
                current_password: password,
                new_password: newPassword,
            });

            setPassword("");
            setNewPassword("");
            setConfirmNewPassword("");
            toast.success("Contraseña cambiada exitosamente.");
        } catch (error) {
            console.error(error);
            toast.error(
                "Error al cambiar la contraseña: " + error.response.data.detail
            );
        }
    };

    const updateAppointmentValue = async () => {
        setShowValueModal(false);
        try {
            toast.info("Actualizando valor...");
            const response = await axios.put(`${apiURL}physicians/value`, {
                new_value: newValue,
            });
            console.log(response.data);
            toast.success("Valor actualizado exitosamente");
            getUserData();
        } catch (error) {
            console.error(error);
            toast.error("Error al actualizar el valor");
        }
    };

    const handleTab1 = () => setActiveSubTab("tab1");
    const handleTab2 = () => setActiveSubTab("tab2");
    const handleTab3 = () => setActiveSubTab("tab3");
    const handleTab4 = () => setActiveSubTab("tab4");

    useEffect(() => {
        getUserData()
            .then(() =>
                user.agenda.working_hours.sort(
                    (a, b) => a.day_of_week - b.day_of_week
                )
            )
            .then(() => setIsLoading(false)) // Marcar como cargado cuando la respuesta llega
            .catch(() => {
                setIsLoading(false); // Asegúrate de marcar como cargado en caso de error
                toast.error("Error al obtener los datos del usuario");
            });
    }, []);

    return (
        <div className={styles.dashboard}>
            <PhysicianTabBar />

            <Header role='physician' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={subTabStyles.subTabNav}>
                            <ul className={subTabStyles.subTabList}>
                                <li
                                    className={`${subTabStyles.subTabElement} ${
                                        activeSubTab === "tab1"
                                            ? subTabStyles.activeSubTabElement
                                            : subTabStyles.inactiveSubTabElement
                                    }`}
                                    onClick={handleTab1}
                                >
                                    Datos del usuario
                                </li>
                                <li
                                    className={`${subTabStyles.subTabElement} ${
                                        activeSubTab === "tab2"
                                            ? subTabStyles.activeSubTabElement
                                            : subTabStyles.inactiveSubTabElement
                                    }`}
                                    onClick={handleTab2}
                                >
                                    Horarios de atencion
                                </li>
                                <li
                                    className={`${subTabStyles.subTabElement} ${
                                        activeSubTab === "tab3"
                                            ? subTabStyles.activeSubTabElement
                                            : subTabStyles.inactiveSubTabElement
                                    }`}
                                    onClick={handleTab3}
                                >
                                    Cambiar contrase&ntilde;a
                                </li>
                                <li
                                    className={`${subTabStyles.subTabElement} ${
                                        activeSubTab === "tab4"
                                            ? subTabStyles.activeSubTabElement
                                            : subTabStyles.inactiveSubTabElement
                                    }`}
                                    onClick={handleTab4}
                                >
                                    Mi Puntaje
                                </li>
                            </ul>
                        </div>

                        {activeSubTab === "tab1" ? (
                            <div className={styles.form}>
                                <ValueModal
                                    isOpen={showValueModal}
                                    closeModal={() => setShowValueModal(false)}
                                    confirmAction={updateAppointmentValue}
                                    currentValue={user.appointment_value}
                                    setNewValue={setNewValue}
                                    title={`Asignar un valor a las consultas (Maximo valor admitido: $${
                                        user.specialty.value * 2
                                    })`}
                                    message={
                                        "¿Cual es el nuevo valor de las consultas?"
                                    }
                                    aclaration='Este valor solo sera aplicado a los nuevos turnos'
                                />
                                {/* Datos del usuario */}
                                <div className={styles["title"]}>
                                    Datos del Usuario
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='firstName'>Nombre:</label>
                                    <input
                                        type='text'
                                        id='firstName'
                                        value={user.firstName}
                                        readOnly
                                        className={
                                            styles["disabled-input-info"]
                                        }
                                    />
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='lastName'>Apellido:</label>
                                    <input
                                        type='text'
                                        id='lastName'
                                        value={user.lastName}
                                        readOnly
                                        className={
                                            styles["disabled-input-info"]
                                        }
                                    />
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='email'>
                                        Correo Electrónico:
                                    </label>
                                    <input
                                        type='email'
                                        id='email'
                                        value={user.email}
                                        readOnly
                                        className={
                                            styles["disabled-input-info"]
                                        }
                                    />
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='email'>Especialidad:</label>
                                    <input
                                        type='text'
                                        id='especialidad'
                                        value={
                                            user.specialty.name
                                                .charAt(0)
                                                .toUpperCase() +
                                            user.specialty.name.slice(1)
                                        }
                                        readOnly
                                        className={
                                            styles["disabled-input-info"]
                                        }
                                    />
                                </div>
                                <div
                                    className={styles["physician-value-group"]}
                                >
                                    <label htmlFor='email'>
                                        Valor de la Consulta:
                                    </label>
                                    <div
                                        className={
                                            styles[
                                                "physician-value-update-group"
                                            ]
                                        }
                                    >
                                        <input
                                            type='text'
                                            id='valor'
                                            value={`\$${user.appointment_value}`}
                                            readOnly
                                            className={
                                                styles["disabled-input-info"]
                                            }
                                        />
                                        <button
                                            className={
                                                styles["standard-button"]
                                            }
                                            onClick={() =>
                                                setShowValueModal(true)
                                            }
                                        >
                                            Actualizar
                                        </button>
                                    </div>
                                </div>{" "}
                            </div>
                        ) : null}

                        {activeSubTab === "tab2" ? (
                            <div className={styles.form}>
                                {/* Modificar horario de atencion */}
                                <h3 className={styles["title"]}>
                                    Servicio de Google Meet
                                </h3>

                                <div className='horario'>
                                    <div
                                        className={
                                            styles["schedule-day-modify"]
                                        }
                                    >
                                        <input
                                            type='checkbox'
                                            id='googleMeet'
                                            name='googleMeet'
                                            className={styles["checkbox-input"]}
                                            defaultChecked={
                                                googleMeetServiceEnabled
                                            }
                                            onChange={(e) =>
                                                setGoogleMeetServiceEnabled(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        <label
                                            htmlFor='googleMeet'
                                            className={styles["checkbox-label"]}
                                        >
                                            {"    "}¿Tiene el servicio de Google
                                            Meet habilitado?
                                            <Tooltip
                                                title='Al habilitar el servicio de Google Meet, los pacientes podran solicitar turnos que seran realizados a traves de dicha plataforma.'
                                                placement='right'
                                            >
                                                <IconButton>
                                                    <InfoIcon />
                                                </IconButton>
                                            </Tooltip>
                                        </label>
                                    </div>
                                </div>

                                <div className={styles["title"]}>
                                    Horario de Atención
                                </div>

                                <div className='horario'>
                                    {user.agenda.working_hours.map((item) => (
                                        <div
                                            key={item.day_of_week}
                                            className={
                                                styles["schedule-day-modify"]
                                            }
                                        >
                                            <h3>
                                                {convertDay(item.day_of_week)}
                                            </h3>
                                            <input
                                                type='checkbox'
                                                id='workingDay'
                                                name='workingDay'
                                                className={
                                                    styles["checkbox-input"]
                                                }
                                                defaultChecked={
                                                    item.start_time !== 0 ||
                                                    item.finish_time !== 0
                                                }
                                                value={item.day_of_week}
                                                onChange={(e) =>
                                                    e.target.checked
                                                        ? addTimeToAgenda(
                                                              item.day_of_week
                                                          )
                                                        : removeTimeFromAgenda(
                                                              item.day_of_week
                                                          )
                                                }
                                            />
                                            <label
                                                htmlFor={item.day_of_week}
                                                className={
                                                    styles["checkbox-label"]
                                                }
                                            >
                                                {"    "}¿Atiende este día?
                                            </label>
                                            <div
                                                className={
                                                    styles[
                                                        "time-picker-container"
                                                    ]
                                                }
                                            >
                                                <label>Inicio: </label>
                                                <input
                                                    type='time'
                                                    defaultValue={convertTime(
                                                        item.start_time
                                                    )}
                                                    onChange={(e) =>
                                                        handleStartTimeChange(
                                                            item.day_of_week,
                                                            e.target.value
                                                        )
                                                    }
                                                />

                                                <label>Fin:</label>
                                                <input
                                                    type='time'
                                                    defaultValue={convertTime(
                                                        item.finish_time
                                                    )}
                                                    onChange={(e) =>
                                                        handleFinishTimeChange(
                                                            item.day_of_week,
                                                            e.target.value
                                                        )
                                                    }
                                                />
                                            </div>
                                        </div>
                                    ))}
                                    <button
                                        className={styles["standard-button"]}
                                        onClick={handleSaveChanges}
                                    >
                                        Guardar Cambios
                                    </button>
                                </div>
                            </div>
                        ) : null}

                        {/* Cambio de Contraseña */}
                        {activeSubTab === "tab3" ? (
                            <form
                                className={styles["form"]}
                                onSubmit={handleChangePassword}
                            >
                                <div className={styles["title"]}>
                                    Cambiar Contraseña
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='currentPassword'>
                                        Contraseña Actual:
                                    </label>
                                    <input
                                        type='password'
                                        id='currentPassword'
                                        value={password}
                                        onChange={(e) =>
                                            setPassword(e.target.value)
                                        }
                                        required
                                        autoComplete='current-password'
                                    />
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='newPassword'>
                                        Nueva Contraseña:
                                    </label>
                                    <input
                                        type='password'
                                        id='newPassword'
                                        value={newPassword}
                                        onChange={(e) =>
                                            setNewPassword(e.target.value)
                                        }
                                        required
                                        autoComplete='new-password'
                                    />
                                </div>
                                <div className={styles["form-group"]}>
                                    <label htmlFor='confirmNewPassword'>
                                        Confirmar Nueva Contraseña:
                                    </label>
                                    <input
                                        type='password'
                                        id='confirmNewPassword'
                                        value={confirmNewPassword}
                                        onChange={(e) =>
                                            setConfirmNewPassword(
                                                e.target.value
                                            )
                                        }
                                        required
                                        autoComplete='new-password'
                                    />
                                </div>
                                <button
                                    type='submit'
                                    className={`${styles["standard-button"]} ${
                                        newPassword !== confirmNewPassword ||
                                        error
                                            ? styles["disabled-button"]
                                            : ""
                                    }`}
                                    disabled={
                                        newPassword !== confirmNewPassword ||
                                        error
                                    }
                                >
                                    Cambiar Contraseña
                                </button>
                            </form>
                        ) : null}

                        {activeSubTab === "tab4" ? (
                            physicianScores.length > 0 ? (
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
                                <div
                                    style={{
                                        fontSize: "20px",
                                        paddingLeft: "1rem",
                                        marginBottom: "1rem",
                                    }}
                                >
                                    No hay reviews
                                </div>
                            )
                        ) : null}
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default UserProfile;
