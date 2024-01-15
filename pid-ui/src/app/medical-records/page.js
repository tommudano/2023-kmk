"use client";

import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import axios from "axios";
import https from "https";
import { Footer, Header, PhysicianTabBar } from "../components/header";
import { toast } from "react-toastify";
import Image from "next/image";

const MedicalRecords = ({ searchParams }) => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const [urlSearchParams, setUrlSearchParams] = useState(null);
    const [patientId, setPatientId] = useState(
        searchParams.patientId || urlSearchParams.get("patientId")
    );
    const [record, setRecord] = useState({
        name: "",
        last_name: "",
        birth_date: "",
        gender: "",
        blood_type: "",
        id: "",
        observations: [],
    });
    const [analysis, setAnalysis] = useState([]);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    useEffect(() => {
        if (window)
            setUrlSearchParams(new URLSearchParams(window.location.search));
    }, []);

    const fetchData = async () => {
        try {
            const response = await axios.get(
                `${apiURL}records/get-record/${patientId}`,
                {
                    httpsAgent: agent,
                }
            );
            setRecord(response.data.record);
            console.log(response);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchMyAnalysis = async () => {
        try {
            const response = await axios.get(`${apiURL}analysis/${patientId}`);
            setAnalysis(response.data);
            console.log(response);
        } catch (error) {
            console.error(error);
        }
    };

    const handleDownload = (url) => {
        const link = document.createElement("a");
        link.download = url;

        link.href = url;

        link.click();
    };

    useEffect(() => {
        if (patientId) {
            axios.defaults.headers.common = {
                Authorization: `bearer ${localStorage.getItem("token")}`,
            };
            fetchData();
            fetchMyAnalysis().then(() => setIsLoading(false));
        }
    }, [patientId]);

    return (
        <div className={styles.dashboard}>
            <PhysicianTabBar />

            <Header role='physician' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Paciente: {record.name} {record.last_name}
                            </div>
                            <Image
                                src='/refresh_icon.png'
                                alt='Refrescar'
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    toast.info("Actualizando...");
                                    fetchData();
                                    fetchMyAnalysis();
                                }}
                            />
                            <div className={styles["subtitle"]}>
                                Fecha de nacimiento: {record.birth_date}
                            </div>
                            <div className={styles["subtitle"]}>
                                Genero: {record.gender}
                            </div>
                            <div className={styles["subtitle"]}>
                                Grupo sanguíneo: {record.blood_type}
                            </div>

                            <div className={styles["my-estudios-section"]}>
                                <div className={styles["title"]}>
                                    Estudios del paciente
                                </div>
                                <div className={styles["horizontal-scroll"]}>
                                    {analysis.length > 0 ? (
                                        analysis.map((uploaded_analysis) => {
                                            return (
                                                <a
                                                    className={
                                                        styles["estudio-card"]
                                                    }
                                                    key={uploaded_analysis.id}
                                                >
                                                    <div
                                                        onClick={() => {
                                                            handleDownload(
                                                                uploaded_analysis.url
                                                            );
                                                        }}
                                                    >
                                                        <div
                                                            className={
                                                                styles[
                                                                    "estudio-name"
                                                                ]
                                                            }
                                                        >
                                                            {uploaded_analysis.file_name.substring(
                                                                0,
                                                                12
                                                            ) + "..."}
                                                        </div>
                                                        <Image
                                                            src='/document.png'
                                                            alt=''
                                                            className={
                                                                styles[
                                                                    "document-icon"
                                                                ]
                                                            }
                                                            style={{
                                                                alignSelf:
                                                                    "center",
                                                                margin: "auto",
                                                            }}
                                                            width={100}
                                                            height={100}
                                                        />
                                                        <div
                                                            className={
                                                                styles[
                                                                    "estudio-date"
                                                                ]
                                                            }
                                                            style={{
                                                                alignSelf:
                                                                    "center",
                                                                margin: "auto",
                                                                display:
                                                                    "table",
                                                                padding:
                                                                    "5px 0",
                                                            }}
                                                        >
                                                            {new Date(
                                                                uploaded_analysis.uploaded_at *
                                                                    1000
                                                            ).toLocaleDateString(
                                                                "es-AR"
                                                            )}
                                                        </div>
                                                    </div>
                                                </a>
                                            );
                                        })
                                    ) : (
                                        <div
                                            style={{
                                                alignSelf: "center",
                                                margin: "auto",
                                                padding: "5px 0",
                                            }}
                                        >
                                            No hay analisis cargados
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className={styles["records-section"]}>
                                {record.observations.length > 0 ? (
                                    <>
                                        {record.observations.map(
                                            (observation, index) => {
                                                console.log(observation);
                                                return (
                                                    <div
                                                        className={
                                                            styles[
                                                                "record-card"
                                                            ]
                                                        }
                                                        key={index}
                                                    >
                                                        <div
                                                            className={
                                                                styles[
                                                                    "record-date"
                                                                ]
                                                            }
                                                        >
                                                            Observacion del{" "}
                                                            {new Date(
                                                                Number(
                                                                    observation.real_start_time
                                                                ) * 1000
                                                            ).toLocaleDateString(
                                                                "es-AR"
                                                            )}{" "}
                                                            - Médico:{" "}
                                                            {
                                                                observation.physician
                                                            }
                                                        </div>
                                                        <div
                                                            className={
                                                                styles[
                                                                    "record-observations"
                                                                ]
                                                            }
                                                        >
                                                            {
                                                                observation.observation
                                                            }
                                                        </div>
                                                    </div>
                                                );
                                            }
                                        )}
                                    </>
                                ) : (
                                    <div className={styles["subtitle"]}>
                                        No hay observaciones en esta historia
                                        clinica
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

export default MedicalRecords;
