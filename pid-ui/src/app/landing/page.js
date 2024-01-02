"use client";

import React, { useState, useLayoutEffect } from "react";
import Link from "next/link";
import styles from "./landing.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import { Footer, HeaderSlim } from "../components/header";
import { loginCheck } from "../components/userCheck";
import { toast } from "react-toastify";

const Landing = () => {
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [disabledLoginButton, setDisabledLoginButton] = useState(false);
    const router = useRouter();

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    useLayoutEffect(() => {
        console.log(process.env.NEXT_PUBLIC_API_URL);
        console.log(apiURL);

        loginCheck(router).then(() => {});
    }, []);

    const handleLogin = async (e) => {
        e.preventDefault();
        setDisabledLoginButton(true);
        toast.info("Iniciando sesión...");
        localStorage.removeItem("token");
        axios.defaults.headers.common = {
            Authorization: `bearer`,
        };

        const userData = {
            email,
            password,
        };

        try {
            const response = await axios.post(
                `${apiURL}users/login/`,
                userData,
                {
                    httpsAgent: agent,
                }
            );
            localStorage.setItem("token", response.data.token);
            loginCheck(router);
        } catch (error) {
            console.error(error);
            setDisabledLoginButton(false);
            switch (error.response.data.detail) {
                case "User must be logged in":
                    router.replace("/");
                    break;

                case "Invalid email and/or password":
                    toast.error("Correo o contraseña incorrectos");
                    break;
                case "Account has to be approved by admin":
                    toast.error(
                        <div>
                            Aprobacion pendiente <br /> Contacte al
                            administrador
                        </div>
                    );
                    break;
                case "Account is not approved":
                    toast.error(
                        <div>
                            Cuenta denegada <br /> Contacte al administrador
                        </div>
                    );
                    break;
            }
        }
    };

    return (
        <div className={styles["login-page"]}>
            <HeaderSlim />
            <form className={styles["form"]} onSubmit={handleLogin}>
                <div className={styles["title"]}>¡Bienvenido!</div>
                <div className={styles["subtitle"]}>Iniciar Sesion</div>
                <div className={styles["form-group"]}>
                    <label htmlFor='email'>Correo Electrónico</label>
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
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type='submit'
                    className={
                        disabledLoginButton
                            ? styles["disabled-button"]
                            : styles["cta-button"]
                    }
                    disabled={disabledLoginButton}
                >
                    Iniciar Sesión
                </button>
                <div className={styles["register-link"]}>
                    {" "}
                    <Link legacyBehavior href='/registro'>
                        <a>¿No tienes una cuenta? Registrarse</a>
                    </Link>
                </div>
            </form>
            <Footer />
        </div>
    );
};

export default Landing;
