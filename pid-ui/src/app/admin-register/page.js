"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import { Pie } from "react-chartjs-2";
import Chart from "chart.js/auto"; // NO BORRAR; Es necesario para que los graficos corran correctamente
import styles from "../styles/styles.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import ConfirmationModal from "../components/ConfirmationModal";
import { Header, Footer, AdminTabBar } from "../components/header";
import { toast } from "react-toastify";
import { userCheck } from "../components/userCheck";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [firstLoad, setFirstLoad] = useState(true);
    const [specialties, setSpecialties] = useState([]);
    const [newSpecialty, setNewSpecialty] = useState("");
    const [physicians, setPhysicians] = useState([]);
    const [pendingPhysicians, setPendingPhysicians] = useState([]);
    const [blockedPhysicians, setBlockedPhysicians] = useState([]);
    const [metrics, setMetrics] = useState({});
    const [showModal, setShowModal] = useState(false);
    const [selectedSpecialty, setSelectedSpecialty] = useState("");
    const [disabledSpecialtyAddButton, setDisabledSpecialtyAddButton] =
        useState(false);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const fetchSpecialties = async () => {
        try {
            const response = await axios.get(`${apiURL}admin/specialties/`, {
                httpsAgent: agent,
            });
            console.log(response.data.specialties);
            response.data.specialties == undefined
                ? setSpecialties([])
                : setSpecialties(response.data.specialties);

            !firstLoad ? toast.success("Especialidades actualizadas") : null;
        } catch (error) {
            toast.error("Error al cargar especialidades");
            console.error(error);
        }
    };

    const handleAddSpecialty = async () => {
        setDisabledSpecialtyAddButton(true);
        try {
            toast.info("Agregando especialidad...");
            const response = await axios.post(
                `${apiURL}specialties/add/${newSpecialty}`,
                {
                    httpsAgent: agent,
                }
            );
            toast.success("Especialidad agregada");
            setNewSpecialty("");
            setFirstLoad(true);
            fetchSpecialties();
            setFirstLoad(false);
        } catch (error) {
            if (error.response.status === 422)
                toast.error("Error al agregar especialidad");
            else toast.error(error.response.data.detail);
        }
        setDisabledSpecialtyAddButton(false);
    };

    const handleDeleteClick = (specialty) => {
        setSelectedSpecialty(specialty);
        setShowModal(true);
    };

    const handleDeleteConfirmation = async () => {
        setShowModal(false);
        try {
            toast.info("Borrando especialidad...");
            const response = await axios.delete(
                `${apiURL}specialties/delete/${selectedSpecialty.name}`
            );
            console.log(response.data);
            toast.success("Especialidad eliminada exitosamente");
            fetchSpecialties();
        } catch (error) {
            console.error(error);
            toast.error("Error al borrar especialidad");
        }
    };

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

    const fetchMetrics = async () => {
        try {
            const response = await axios.get(`${apiURL}dashboard/admin`, {
                httpsAgent: agent,
            });
            response.data.dashboard_metrics == undefined
                ? setMetrics({})
                : setMetrics(response.data.dashboard_metrics);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router, "admin").then(() => {
            fetchSpecialties();
            fetchMetrics();
            fetchPhysicians();
            fetchBlockedPhysicians();
            fetchPendingPhysicians().then(() => setIsLoading(false));
            setFirstLoad(false);
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            <ConfirmationModal
                isOpen={showModal}
                closeModal={() => setShowModal(false)}
                confirmAction={handleDeleteConfirmation}
                message={`¿Estás seguro de que deseas eliminar la especialidad ${
                    selectedSpecialty.name
                } (hay ${selectedSpecialty.physicians_count} ${
                    selectedSpecialty.physicians_count === 1
                        ? "medico"
                        : "medicos"
                } bajo esta categoria)?`}
            />

            <AdminTabBar />

            <Header role='admin' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Especialidades
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Notificaciones'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info(
                                        "Actualizando especialidades..."
                                    );
                                    fetchSpecialties();
                                }}
                            />

                            <div className={styles["subtitle"]}>
                                Agregar Especialidad
                            </div>
                            <input
                                type='text'
                                id='specialty'
                                name='specialty'
                                placeholder='Especialidad'
                                value={newSpecialty}
                                onChange={(e) =>
                                    setNewSpecialty(e.target.value)
                                }
                            />
                            <button
                                className={`${styles["add-button"]} ${
                                    disabledSpecialtyAddButton
                                        ? styles["disabled-button"]
                                        : ""
                                }`}
                                onClick={handleAddSpecialty}
                                disabled={disabledSpecialtyAddButton}
                            >
                                Agregar
                            </button>
                            <div className={styles["admin-scrollable-section"]}>
                                {specialties.length > 0 ? (
                                    <>
                                        {specialties.map((specialty) => (
                                            <div
                                                key={specialty.name}
                                                className={
                                                    styles[
                                                        "specialty-container"
                                                    ]
                                                }
                                            >
                                                <p>
                                                    {specialty.name
                                                        .charAt(0)
                                                        .toUpperCase() +
                                                        specialty.name.slice(1)}
                                                </p>
                                                <div
                                                    className={
                                                        styles[
                                                            "appointment-buttons-container"
                                                        ]
                                                    }
                                                >
                                                    <Image
                                                        src='/trash_icon.png'
                                                        alt='borrar'
                                                        className={styles.logo}
                                                        width={25}
                                                        height={25}
                                                        onClick={() => {
                                                            handleDeleteClick(
                                                                specialty
                                                            );
                                                        }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </>
                                ) : (
                                    <div className={styles["subtitle"]}>
                                        No hay especialidades
                                    </div>
                                )}
                            </div>
                        </div>

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

                        <div className={styles.form}>
                            <div className={styles["title"]}>Metricas</div>
                            <div className={styles["admin-section"]}>
                                {metrics.all_appointments_by_specialty &&
                                Object.keys(
                                    metrics.all_appointments_by_specialty
                                ).length > 0 ? (
                                    <div>
                                        <div className={styles["subtitle"]}>
                                            Turnos por especialidad
                                        </div>
                                        <div
                                            style={{
                                                width: "100%",
                                                height: "400px",
                                                justifyContent: "center",
                                                alignContent: "space-around",
                                                justifyContent: "space-around",
                                                margin: "auto",
                                                padding: "1rem",
                                            }}
                                        >
                                            <Pie
                                                data={{
                                                    labels: Object.keys(
                                                        metrics.all_appointments_by_specialty
                                                    ),
                                                    datasets: [
                                                        {
                                                            label: "Cantidad de turnos",
                                                            data: Object.values(
                                                                metrics.all_appointments_by_specialty
                                                            ),
                                                            backgroundColor: [
                                                                "rgba(43, 59, 127, 0.3)",
                                                                "rgba(43, 59, 127, 0.5)",
                                                                "rgba(43, 59, 127, 0.7)",
                                                                "rgba(43, 59, 127, 0.9)",
                                                                "rgba(43, 59, 127, 1.1)",
                                                                "rgba(43, 59, 127, 1.3)",
                                                                "rgba(43, 59, 127, 1.5)",
                                                                "rgba(43, 59, 127, 1.7)",
                                                                "rgba(43, 59, 127, 1.9)",
                                                            ],
                                                        },
                                                    ],
                                                }}
                                                // height={30}
                                                // width={70}
                                                options={{
                                                    responsive: true,
                                                    maintainAspectRatio: false,
                                                    layout: {
                                                        padding: {
                                                            left: 150,
                                                            right: 150,
                                                        },
                                                    },
                                                    plugins: {
                                                        legend: {
                                                            position: "right",
                                                            labels: {
                                                                usePointStyle: true,
                                                                pointStyle:
                                                                    "circle",
                                                                padding: 20,
                                                            },
                                                        },
                                                    },
                                                }}
                                            />
                                        </div>
                                    </div>
                                ) : (
                                    <div className={styles["subtitle"]}>
                                        No hay datos suficientes para mostrar
                                        metricas
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
