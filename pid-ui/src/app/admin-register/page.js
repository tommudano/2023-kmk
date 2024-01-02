"use client";

import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import validator from "validator";
import { Header, Footer, AdminTabBar } from "../components/header";
import { toast } from "react-toastify";
import { userCheck } from "../components/userCheck";
import ConfirmationModal from "../components/ConfirmationModal";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [nombre, setNombre] = useState("");
    const [apellido, setApellido] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [disabledRegisterButton, setDisabledRegisterButton] = useState(false);
    const [showModal, setShowModal] = useState(false);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

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

    const handleSubmit = (e) => {
        e.preventDefault();
        setShowModal(true);
    };

    const registerAdmin = async () => {
        toast.info("Registrando...");
        setDisabledRegisterButton(true);
        setShowModal(false);

        let userData = {
            name: nombre,
            last_name: apellido,
            email: email,
            password: password,
        };

        try {
            const response = await axios.post(
                `${apiURL}admin/register`,
                userData,
                { httpsAgent: agent }
            );
            toast.success(response.data.message);
            setNombre("");
            setApellido("");
            setEmail("");
            setPassword("");
            setConfirmPassword("");
        } catch (error) {
            setDisabledRegisterButton(false);
            console.error(error);
            if (error.response.status === 400)
                toast.error(error.response.data.detail);
            else toast.error("Ha ocurrido un error");
        }
        setDisabledRegisterButton(false);
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router, "admin").then(() => {
            setIsLoading(false);
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            <ConfirmationModal
                isOpen={showModal}
                closeModal={() => setShowModal(false)}
                confirmAction={registerAdmin}
                message='¿Estás seguro de que deseas crear a este administrador?'
            />

            <AdminTabBar highlight='RegisterAdmin' />

            <Header role='admin' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <form
                            className={styles["form"]}
                            onSubmit={handleSubmit}
                        >
                            <div className={styles["title"]}>
                                Registro de Administradores
                            </div>
                            <div className={styles["subtitle"]}>
                                Ingrese los datos del nuevo administrador
                            </div>

                            <div className={styles["form-group"]}>
                                <label htmlFor='nombre'>Nombre</label>
                                <input
                                    type='text'
                                    id='nombre'
                                    value={nombre}
                                    onChange={(e) => setNombre(e.target.value)}
                                    required
                                />
                            </div>
                            <div className={styles["form-group"]}>
                                <label htmlFor='apellido'>Apellido</label>
                                <input
                                    type='text'
                                    id='apellido'
                                    value={apellido}
                                    onChange={(e) =>
                                        setApellido(e.target.value)
                                    }
                                    required
                                />
                            </div>
                            <div className={styles["form-group"]}>
                                <label htmlFor='email'>
                                    Correo Electrónico
                                </label>
                                <input
                                    type='email'
                                    id='email'
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                            </div>

                            <div className={styles["form-group"]}>
                                <label htmlFor='password'>Contraseña</label>
                                <input
                                    type='password'
                                    id='password'
                                    value={password}
                                    onChange={(e) => {
                                        setPassword(e.target.value);
                                        validate(e.target.value);
                                    }}
                                    required
                                />
                            </div>
                            <div className={styles["form-group"]}>
                                <label htmlFor='confirmPassword'>
                                    Repetir Contraseña
                                </label>
                                <input
                                    type='password'
                                    id='confirmPassword'
                                    value={confirmPassword}
                                    onChange={(e) => {
                                        setConfirmPassword(e.target.value);
                                        validate(e.target.value);
                                    }}
                                    required
                                />
                            </div>
                            {error && (
                                <div className={styles["error-message"]}>
                                    {error}
                                </div>
                            )}
                            {password !== confirmPassword && (
                                <div className={styles["error-message"]}>
                                    Las contraseñas no coinciden.
                                </div>
                            )}
                            <button
                                type='submit'
                                className={`${styles["button"]} ${
                                    password !== confirmPassword ||
                                    error ||
                                    disabledRegisterButton
                                        ? styles["disabled-button"]
                                        : ""
                                }`}
                                disabled={
                                    password !== confirmPassword ||
                                    error ||
                                    disabledRegisterButton
                                }
                            >
                                Registrarse
                            </button>
                        </form>
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default Admin;
