import React, { useLayoutEffect } from "react";
import Image from "next/image";
import styles from "../styles/Header.module.css";
import axios from "axios";
import { loginCheck, redirect, userCheck } from "../components/userCheck";
import { useRouter } from "next/navigation";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Header = (props) => {
    const router = useRouter();

    return (
        <div className={styles.header}>
            <ToastContainer
                limit={3}
                position={"top-right"}
                hideProgressBar={false}
                closeOnClick={true}
                pauseOnHover={true}
            />
            <Image
                src='/logo.png'
                alt='Logo de la empresa'
                className={styles.logo}
                width={200}
                height={200}
                onClick={() => {
                    redirect(router);
                }}
            />
            <Image
                src='/logout_icon.png'
                alt='CerrarSesion'
                className={styles["logout-icon"]}
                width={200}
                height={200}
                onClick={() => {
                    localStorage.removeItem("token");
                    axios.defaults.headers.common = {
                        Authorization: `bearer`,
                    };
                    router.push("/");
                }}
            />
            <Image
                src='/user_icon.png'
                alt='Usuario'
                className={styles["user-icon"]}
                width={200}
                height={200}
                onClick={() => {
                    router.push("/" + `${props.role}` + "-my-user");
                }}
            />
        </div>
    );
};

const HeaderSlim = () => {
    const router = useRouter();

    return (
        <div className={styles.header}>
            <ToastContainer
                limit={3}
                position={"top-right"}
                hideProgressBar={false}
                closeOnClick={true}
                pauseOnHover={true}
            />
            <Image
                src='/logo.png'
                alt='Logo de la empresa'
                className={styles.logo}
                width={200}
                height={200}
                onClick={() => {
                    redirect(router);
                }}
            />
        </div>
    );
};

const TabBar = (props) => {
    const router = useRouter();
    const handleLogoClick = () => {
        loginCheck(router);
    };

    useLayoutEffect(() => {
        userCheck(router, "patient");
    }, []);

    return (
        <div className={styles["tab-bar"]}>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Turnos" ? styles["selected-tab"] : ""
                }`}
                onClick={handleLogoClick}
            >
                Turnos Vigentes
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "SolicitarTurnos"
                        ? styles["selected-tab"]
                        : ""
                }`}
                onClick={() => router.push("/patient-appointments")}
            >
                Solicitar Turno
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Ficha" ? styles["selected-tab"] : ""
                }`}
                onClick={() => router.push("/patient-my-record")}
            >
                Mi Ficha
            </div>
        </div>
    );
};

const PhysicianTabBar = (props) => {
    const router = useRouter();
    useLayoutEffect(() => {
        userCheck(router, "physician");
    }, []);

    return (
        <div className={styles["tab-bar"]}>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "TurnosActivos"
                        ? styles["selected-tab"]
                        : ""
                }`}
                onClick={() => router.push("/physician-agenda")}
            >
                Turnos Activos
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "TurnosPorAprobar"
                        ? styles["selected-tab"]
                        : ""
                }`}
                onClick={() => router.push("/physician-peding-appointments")}
            >
                Turnos por aprobar
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Metricas" ? styles["selected-tab"] : ""
                }`}
                onClick={() => router.push("/physician-metrics")}
            >
                Mis metricas
            </div>
        </div>
    );
};

const AdminTabBar = (props) => {
    const router = useRouter();
    useLayoutEffect(() => {
        userCheck(router, "admin");
    }, []);

    return (
        <div className={styles["tab-bar"]}>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Especialidades"
                        ? styles["selected-tab"]
                        : ""
                }`}
                onClick={() => router.push("/admin-specialties")}
            >
                Especialidades
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Medicos" ? styles["selected-tab"] : ""
                }`}
                onClick={() => router.push("/admin-physicians")}
            >
                Medicos
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "Metricas" ? styles["selected-tab"] : ""
                }`}
                onClick={() => router.push("/admin-metrics")}
            >
                Mis metricas
            </div>
            <div
                className={`${styles["tab"]} ${
                    props.highlight === "RegisterAdmin"
                        ? styles["selected-tab"]
                        : ""
                }`}
                onClick={() => router.push("/admin-register")}
            >
                Registrar Administrador
            </div>
        </div>
    );
};

const Footer = () => {
    return (
        <footer className={styles["page-footer"]}>
            <p>Derechos de autor © 2023 KMK</p>
        </footer>
    );
};

export { Header, HeaderSlim, TabBar, PhysicianTabBar, AdminTabBar, Footer };
