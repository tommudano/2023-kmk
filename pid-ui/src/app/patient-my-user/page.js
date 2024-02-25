"use client";

import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import subTabStyles from "../styles/subTab.module.css";
import axios from "axios";
import https from "https";
import validator from "validator";
import { Footer, Header, TabBar } from "../components/header";
import { toast } from "react-toastify";

const UserProfile = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [user, setUser] = useState({
        firstName: "",
        lastName: "",
        email: "",
        bloodtype: "",
    });
    const [password, setPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmNewPassword, setConfirmNewPassword] = useState("");
    const [error, setError] = useState("");
    const [activeSubTab, setActiveSubTab] = useState("tab1");
    const [patientScores, setPatientScores] = useState([]);

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

            setPatientScores(tempReviews);
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
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
            setError(
                "La contraseña no es lo suficientemente fuerte: debe incluir al menos 8 caracteres, 1 minúscula, 1 mayúscula y 1 número"
            );
        }
    };

    const getUserData = async () => {
        try {
            const response = await axios.get(`${apiURL}users/user-info`);
            let user = {
                firstName: response.data.first_name,
                lastName: response.data.last_name,
                email: response.data.email,
                bloodtype: response.data.blood_type,
                id: response.data.id,
            };
            setUser({ ...user });
            getPatientScores(user.id);
        } catch (error) {
            console.error(error);
            toast.error("Error al obtener los datos del usuario");
        }
    };

    const handleChangePassword = async () => {
        if (newPassword !== confirmNewPassword) {
            toast.error("Las contraseñas no coinciden.");
            return;
        }

        try {
            toast.info("Cambiando contraseña...");
            const response = await axios.post(
                `${apiURL}users/change-password`,
                {
                    current_password: password,
                    new_password: newPassword,
                }
            );

            console.log(response);

            toast.success("Contraseña cambiada exitosamente.");
            setPassword("");
            setNewPassword("");
            setConfirmNewPassword("");
        } catch (error) {
            toast.error(
                "Error al cambiar la contraseña: " + error.response.data.detail
            );
        }
    };

    const handleTab1 = () => setActiveSubTab("tab1");
    const handleTab2 = () => setActiveSubTab("tab2");
    const handleTab3 = () => setActiveSubTab("tab3");

    useEffect(() => {
        getUserData().then(() => setIsLoading(false));
    }, []);

    return (
        <div className={styles.dashboard}>
            <TabBar />

            <Header role='patient' />

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
                                    Cambiar contrase&ntilde;a
                                </li>
                                <li
                                    className={`${subTabStyles.subTabElement} ${
                                        activeSubTab === "tab3"
                                            ? subTabStyles.activeSubTabElement
                                            : subTabStyles.inactiveSubTabElement
                                    }`}
                                    onClick={handleTab3}
                                >
                                    Mi Puntaje
                                </li>
                            </ul>
                        </div>

                        {activeSubTab === "tab1" ? (
                            <div className={styles.form}>
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
                            </div>
                        ) : null}
                        {activeSubTab === "tab2" ? (
                            <div className={styles["form"]}>
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
                                        onChange={(e) => {
                                            setNewPassword(e.target.value);
                                            validate(e.target.value);
                                        }}
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
                                        onChange={(e) => {
                                            setConfirmNewPassword(
                                                e.target.value
                                            );
                                            validate(e.target.value);
                                        }}
                                        required
                                        autoComplete='new-password'
                                    />
                                </div>
                                {error && (
                                    <div className={styles["error-message"]}>
                                        {error}
                                    </div>
                                )}
                                {newPassword !== confirmNewPassword && (
                                    <div className={styles["error-message"]}>
                                        Las contraseñas no coinciden.
                                    </div>
                                )}
                                <button
                                    type='submit'
                                    className={`${styles["standard-button"]} ${
                                        newPassword !== confirmNewPassword ||
                                        error
                                            ? styles["disabled-button"]
                                            : ""
                                    }`}
                                    onClick={handleChangePassword}
                                    disabled={
                                        newPassword !== confirmNewPassword ||
                                        error
                                    }
                                >
                                    Cambiar Contraseña
                                </button>
                            </div>
                        ) : null}

                        {activeSubTab === "tab3" ? (
                            patientScores.length > 0 ? (
                                <>
                                    {patientScores.map((review) => (
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
