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
import PhysicianCard from "../components/PhysicianCard";
import RatingsModal from "../components/RatingsModal";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [firstLoad, setFirstLoad] = useState(true);
    const [physicians, setPhysicians] = useState([]);
    const [pendingPhysicians, setPendingPhysicians] = useState([]);
    const [blockedPhysicians, setBlockedPhysicians] = useState([]);
    const [isRatingModalOpen, setIsRatingModalOpen] = useState(false);
    const [scores, setScores] = useState([]);

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
            !firstLoad
                ? toast.success("Profesionales por aprobar actualizados")
                : null;
        } catch (error) {
            console.error(error);
            !firstLoad
                ? toast.error("Error al actualizar los profesionales")
                : null;
        }
    };

    const fetchWorkingPhysicians = async () => {
        try {
            const response = await axios.get(
                `${apiURL}admin/physicians-working`,
                {
                    httpsAgent: agent,
                }
            );
            console.log(response.data.physicians_working);
            setPhysicians(response.data.physicians_working);
            !firstLoad
                ? toast.success("Profesionales en funciones actualizados")
                : null;
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
            !firstLoad
                ? toast.success("Profesionales bloquados actualizados")
                : null;
        } catch (error) {
            console.error(error);
            !firstLoad
                ? toast.error("Error al actualizar los profesionales")
                : null;
        }
    };

    const handleApprovePhysician = async (physician) => {
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
            fetchWorkingPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al aprobar profesional");
        }
    };

    const handleDenyPhysician = async (physician) => {
        try {
            toast.info("Bloquando medico...");
            console.log(physician.id);
            const response = await axios.post(
                `${apiURL}admin/deny-physician/${physician.id}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Medico bloqueado");
            setFirstLoad(true);
            fetchPendingPhysicians();
            fetchWorkingPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al denegar profesional");
        }
    };

    const handleUnblockPhysician = async (physician) => {
        try {
            toast.info("Desbloqueando medico...");
            console.log(physician.id);
            const response = await axios.post(
                `${apiURL}admin/unblock-physician/${physician.id}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Medico desbloqueado");
            setFirstLoad(true);
            fetchPendingPhysicians();
            fetchWorkingPhysicians();
            fetchBlockedPhysicians();
            setFirstLoad(false);
        } catch (error) {
            console.log(error);
            toast.error("Error al desbloquear profesional");
        }
    };

    const getAppointmentScores = async (id) => {
        try {
            const response = await axios.get(`${apiURL}users/score/${id}`, {
                httpsAgent: agent,
            });
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
            setScores([...reviews]);
        } catch (error) {
            toast.error("Error al obtener los puntajes");
            console.error(error);
        }
    };

    const handleOpenRatingModal = async (doctorId) => {
        await getAppointmentScores(doctorId);
        setIsRatingModalOpen(true);
    };

    const handleCloseRatingModal = () => {
        setScores([]);
        setIsRatingModalOpen(false);
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router, "admin").then(() => {
            fetchWorkingPhysicians();
            fetchBlockedPhysicians();
            fetchPendingPhysicians().then(() => setIsLoading(false));
            setFirstLoad(false);
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            {isRatingModalOpen && (
                <RatingsModal
                    isOpen={isRatingModalOpen}
                    handleCloseRatingModal={handleCloseRatingModal}
                    scores={scores}
                />
            )}

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
                                            <PhysicianCard
                                                doctor={doctor}
                                                handleOpenRatingModal={
                                                    handleOpenRatingModal
                                                }
                                                handleApprovePhysician={
                                                    handleApprovePhysician
                                                }
                                                handleDenyPhysician={
                                                    handleDenyPhysician
                                                }
                                                key={doctor.id}
                                            />
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
                                    fetchWorkingPhysicians();
                                }}
                            />
                            <div className={styles["admin-section"]}>
                                {physicians.length > 0 ? (
                                    <div>
                                        {physicians.map((doctor) => (
                                            <PhysicianCard
                                                doctor={doctor}
                                                handleOpenRatingModal={
                                                    handleOpenRatingModal
                                                }
                                                handleDenyPhysician={
                                                    handleDenyPhysician
                                                }
                                                key={doctor.id}
                                            />
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
                                    <div>
                                        {blockedPhysicians.map((doctor) => (
                                            <PhysicianCard
                                                doctor={doctor}
                                                handleOpenRatingModal={
                                                    handleOpenRatingModal
                                                }
                                                handleApprovePhysician={
                                                    handleUnblockPhysician
                                                }
                                                approveButtonText='Desbloquear'
                                                key={doctor.id}
                                            />
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
