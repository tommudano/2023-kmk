"use client";

import React, { useState, useEffect } from "react";
import { Pie } from "react-chartjs-2";
import Chart from "chart.js/auto"; // NO BORRAR; Es necesario para que los graficos corran correctamente
import styles from "../styles/styles.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import { Header, Footer, AdminTabBar } from "../components/header";
import { userCheck } from "../components/userCheck";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [metrics, setMetrics] = useState({});

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

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
            fetchMetrics().then(() => setIsLoading(false));
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            <AdminTabBar highlight='Metricas' />

            <Header role='admin' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Metricas
                                <Tooltip
                                    title='Las puntuaciones muestran la opinion de los usuarios acerca de los medicos. La puntuacion mas baja es 0 (muy malo) y la mas alta es 5 (excelente). En caso de que el medico no haya sido puntuado en una categoria aun, se mostrara que dicha seccion no tiene reviews.'
                                    placement='right'
                                >
                                    <IconButton>
                                        <InfoIcon />
                                    </IconButton>
                                </Tooltip>
                            </div>
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
