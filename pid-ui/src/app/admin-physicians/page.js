"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import styles from "../styles/styles.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import { Header, Footer, AdminTabBar } from "../components/header";
import { toast } from "react-toastify";
import { userCheck } from "../components/userCheck";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [firstLoad, setFirstLoad] = useState(true);
    const [physicians, setPhysicians] = useState([]);
    const [pendingPhysicians, setPendingPhysicians] = useState([]);
    const [blockedPhysicians, setBlockedPhysicians] = useState([]);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const fetchPendingPhysicians = async () => {
        try {
            const response = await axios.get(
                `${apiURL}admin/physicians-pending`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data.physicians_pending_validation);
            setPendingPhysicians(response.data.physicians_pending_validation);
            !firstLoad ? toast.success("Profesionales actualizados") : null;
        } catch (error) {
            console.error(error);
            !firstLoad
                ? toast.error("Error al actualizar los profesionales")
                : null;
        }
    };

    const fetchPhysicians = async () => {
        try {
            const response = await axios.get(
                `${apiURL}admin/physicians-working`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data.physicians_working);
            setPhysicians(response.data.physicians_working);
            !firstLoad ? toast.success("Profesionales actualizados") : null;
        } catch (error) {
            console.error(error);
            !firstLoad
                ? toast.error("Error al actualizar los profesionales")
                : null;
        }
    };

    const fetchBlockedPhysicians = async () => {
        try {
            const response = await axios.get(
                `${apiURL}admin/physicians-blocked`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data.physicians_blocked);
            setBlockedPhysicians(response.data.physicians_blocked);
            !firstLoad ? toast.success("Profesionales actualizados") : null;
        } catch (error) {
            console.error(error);
            !firstLoad
                ? toast.error("Error al actualizar los profesionales")
                : null;
        }
    };

    const handleApprovePhysician = async (physician) => {
        toast.info("Aprobando profesional...");
        try {
            toast.info("Aprobando medico...");
            console.log(physician.id);
            const response = await axios.post(
                `${apiURL}admin/approve-physician/${physician.id}`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data);
            toast.success("Profesional aprobado");
            setFirstLoad(true);
            fetchPendingPhysicians();
            fetchPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al aprobar profesional");
        }
    };

    const handleDenyPhysician = async (physician) => {
        toast.info("Denegando profesional...");
        try {
            toast.info("Bloquando medico...");
            console.log(physician.id);
            const response = await axios.post(
                `${apiURL}admin/deny-physician/${physician.id}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Profesional denegado");
            setFirstLoad(true);
            fetchPendingPhysicians();
            fetchPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al denegar profesional");
        }
    };

    const handleUnblockPhysician = async (physician) => {
        toast.info("Desbloqueando profesional...");
        try {
            toast.info("Desbloqueando medico...");
            console.log(physician.id);
            const response = await axios.post(
                `${apiURL}admin/unblock-physician/${physician.id}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Profesional desbloqueado");
            setFirstLoad(true);
            fetchPendingPhysicians();
            fetchPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al desbloquear profesional");
        }
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router, "admin").then(() => {
            fetchPhysicians();
            fetchBlockedPhysicians();
            fetchPendingPhysicians().then(() => setIsLoading(false));
            setFirstLoad(false);
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            <AdminTabBar highlight='Medicos' />

            <Header role='admin' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Profesionales pendientes de aprobación
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando profesionales...");
                                    fetchPendingPhysicians();
                                }}
                            />
                            <div className={styles["admin-section"]}>
                                {pendingPhysicians.length > 0 ? (
                                    <div>
                                        {pendingPhysicians.map((doctor) => (
                                            <div
                                                key={doctor.id}
                                                className={
                                                    styles["appointment"]
                                                }
                                            >
                                                <div
                                                    className={
                                                        styles["subtitle"]
                                                    }
                                                >
                                                    {doctor.first_name +
                                                        " " +
                                                        doctor.last_name}
                                                </div>
                                                <p>
                                                    Especialidad:{" "}
                                                    {doctor.specialty}
                                                </p>
                                                <p>E-mail: {doctor.email}</p>
                                                <p>
                                                    Matricula: {doctor.tuition}
                                                </p>
                                                <div
                                                    className={
                                                        styles[
                                                            "appointment-buttons-container"
                                                        ]
                                                    }
                                                >
                                                    <button
                                                        className={
                                                            styles[
                                                                "approve-button"
                                                            ]
                                                        }
                                                        onClick={() =>
                                                            handleApprovePhysician(
                                                                doctor
                                                            )
                                                        }
                                                    >
                                                        Aprobar
                                                    </button>

                                                    <button
                                                        className={
                                                            styles[
                                                                "delete-button"
                                                            ]
                                                        }
                                                        onClick={() =>
                                                            handleDenyPhysician(
                                                                doctor
                                                            )
                                                        }
                                                    >
                                                        Bloquear
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className={styles["subtitle"]}>
                                        No hay aprobaciones pendientes
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Profesionales en funciones
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando profesionales...");
                                    fetchPhysicians();
                                }}
                            />
                            <div className={styles["admin-section"]}>
                                {physicians.length > 0 ? (
                                    <div>
                                        {physicians.map((doctor) => (
                                            <div
                                                key={doctor.id}
                                                className={
                                                    styles["appointment"]
                                                }
                                            >
                                                <div
                                                    className={
                                                        styles["subtitle"]
                                                    }
                                                >
                                                    {doctor.first_name +
                                                        " " +
                                                        doctor.last_name}
                                                </div>
                                                <p>
                                                    Especialidad:{" "}
                                                    {doctor.specialty}
                                                </p>
                                                <p>E-mail: {doctor.email}</p>
                                                <p>
                                                    Matricula: {doctor.tuition}
                                                </p>
                                                <div
                                                    className={
                                                        styles[
                                                            "appointment-buttons-container"
                                                        ]
                                                    }
                                                >
                                                    <button
                                                        className={
                                                            styles[
                                                                "delete-button"
                                                            ]
                                                        }
                                                        onClick={() =>
                                                            handleDenyPhysician(
                                                                doctor
                                                            )
                                                        }
                                                    >
                                                        Bloquear
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className={styles["subtitle"]}>
                                        No hay profesionales en funciones
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Profesionales bloqueados / denegados
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando profesionales...");
                                    fetchBlockedPhysicians();
                                }}
                            />
                            <div className={styles["admin-section"]}>
                                {blockedPhysicians.length > 0 ? (
                                    // If there are pending doctor approvals, map through them and display each appointment
                                    <div>
                                        {blockedPhysicians.map((doctor) => (
                                            <div
                                                key={doctor.id}
                                                className={
                                                    styles["appointment"]
                                                }
                                            >
                                                <div
                                                    className={
                                                        styles["subtitle"]
                                                    }
                                                >
                                                    {doctor.first_name +
                                                        " " +
                                                        doctor.last_name}
                                                </div>
                                                <p>
                                                    Especialidad:{" "}
                                                    {doctor.specialty}
                                                </p>
                                                <p>E-mail: {doctor.email}</p>
                                                <p>
                                                    Matricula: {doctor.tuition}
                                                </p>
                                                <div
                                                    className={
                                                        styles[
                                                            "appointment-buttons-container"
                                                        ]
                                                    }
                                                >
                                                    <button
                                                        className={
                                                            styles[
                                                                "approve-button"
                                                            ]
                                                        }
                                                        onClick={() =>
                                                            handleUnblockPhysician(
                                                                doctor
                                                            )
                                                        }
                                                    >
                                                        Desbloquear
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    // If there are no pending doctor approvals, display the message
                                    <div className={styles["subtitle"]}>
                                        No hay profesionales bloqueados
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default Admin;
