"use client";

import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import subTabStyles from "../styles/subTab.module.css";
import axios from "axios";
import validator from "validator";
import { AdminTabBar, Footer, Header, TabBar } from "../components/header";
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
            const response = await axios.get(`${apiURL}admin/user-info`);

            console.log(response);

            let user = {
                firstName: response.data.first_name,
                lastName: response.data.last_name,
                email: response.data.email,
                bloodtype: response.data.blood_type,
            };
            setUser(user);
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

    useEffect(() => {
        getUserData().then(() => setIsLoading(false));
    }, []);

    return (
        <div className={styles.dashboard}>
            <AdminTabBar />

            <Header role='admin' />

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
                        ) : (
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
                                {password !== confirmNewPassword && (
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
                        )}
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default UserProfile;
