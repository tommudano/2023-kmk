"use client";

import React, { useState, useEffect, useRef } from "react";
import styles from "../styles/styles.module.css";
import axios from "axios";
import https from "https";
import { useRouter } from "next/navigation";
import { Footer, Header, TabBar } from "../components/header";
import Image from "next/image";
import { toast } from "react-toastify";
import { userCheck } from "../components/userCheck";
import "react-toastify/dist/ReactToastify.css";

const MyRecord = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [file, setFile] = useState([]); // File to be uploaded
    const [analysis, setAnalysis] = useState([]);
    const [record, setRecord] = useState({
        name: "",
        last_name: "",
        birth_date: "",
        gender: "",
        blood_type: "",
        id: "",
        observations: [],
    });
    const inputRef = useRef(null);

    const agent = new https.Agent({
        rejectUnauthorized: false,
    });

    const fetchData = async () => {
        try {
            const response = await axios.get(`${apiURL}records/get-my-record`, {
                httpsAgent: agent,
            });
            console.log(response);
            setRecord(response.data.record);
            console.log(response);
        } catch (error) {
            console.error(error);
        }
    };

    const fetchMyAnalysis = async () => {
        try {
            const response = await axios.get(`${apiURL}analysis`);
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

    const handleFileDelete = async (id) => {
        try {
            const response = await axios.delete(`${apiURL}analysis/${id}`);
            console.log(response);
            toast.success("Analisis eliminado con exito");
            fetchMyAnalysis();
        } catch (error) {
            console.error(error);
            toast.error("Error al eliminar analisis");
        }
    };

    const resetFileInput = () => {
        inputRef.current.value = null;
        setFile([]);
    };

    const onSubmit = async (e) => {
        // e.preventDefault();
        toast.info("Subiendo analisis");
        const formData = new FormData();
        Array.from(e).forEach((file_to_upload) =>
            formData.append("analysis", file_to_upload)
        );
        try {
            const response = await axios.post(`${apiURL}analysis`, formData);
            console.log(response);
            toast.success("Analisis subido con exito");
            fetchMyAnalysis();
            resetFileInput();
        } catch (error) {
            console.error(error);
            toast.error("Error al subir analisis");
        }
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router);
        fetchData();
        fetchMyAnalysis().then(() => setIsLoading(false));
    }, []);

    return (
        <div className={styles.dashboard}>
            <TabBar highlight="Ficha" />

            <Header role="patient" />

            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                {record.name} {record.last_name}
                            </div>
                            <Image
                                src="/refresh_icon.png"
                                alt="Refrescar"
                                className={styles["refresh-icon"]}
                                width={200}
                                height={200}
                                onClick={() => {
                                    fetchData();
                                    fetchMyAnalysis();
                                    toast.info("Datos actualizados");
                                }}
                            />
                            <div className={styles["subtitle"]}>
                                Nac.: {record.birth_date}
                            </div>
                            <div className={styles["subtitle"]}>
                                Genero: {record.gender}
                            </div>
                            <div className={styles["subtitle"]}>
                                Grupo sanguíneo: {record.blood_type}
                            </div>

                            <div className={styles["my-estudios-section"]}>
                                <div className={styles["title"]}>
                                    Mis Estudios
                                </div>

                                <div className={styles["horizontal-scroll"]}>
                                    {analysis.length > 0 ? (
                                        analysis.map((uploaded_analysis) => {
                                            return (
                                                <div
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
                                                            src="/document.png"
                                                            alt=""
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
                                                            onClick={() => {}}
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
                                                    <Image
                                                        src="/trash_icon.png"
                                                        alt=""
                                                        className={
                                                            styles[
                                                                "document-icon"
                                                            ]
                                                        }
                                                        style={{
                                                            alignSelf: "center",
                                                        }}
                                                        width={25}
                                                        height={25}
                                                        onClick={() => {
                                                            handleFileDelete(
                                                                uploaded_analysis.id
                                                            );
                                                        }}
                                                    />
                                                </div>
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

                                <form
                                    className={styles["file-upload-form"]}
                                    // onSubmit={onSubmit}
                                >
                                    <label
                                        htmlFor="files"
                                        className={styles["upload-button"]}
                                        style={{ color: "#fff" }}
                                    >
                                        Cargar analisis
                                    </label>

                                    <input
                                        id="files"
                                        type="file"
                                        name="file"
                                        accept=".pdf"
                                        multiple={true}
                                        onChange={(e) => {
                                            onSubmit(e.target.files);
                                            setFile(e.target.files);
                                        }}
                                        onClick={(event) => {
                                            event.target.value = null;
                                        }}
                                        ref={inputRef}
                                        style={{ display: "none" }}
                                    />
                                </form>
                            </div>
                        </div>

                        <div className={styles["records-section"]}>
                            {record.observations.length > 0 ? (
                                // If there are appointments, map through them and display each appointment
                                <>
                                    {record.observations.map(
                                        (observation, index) => {
                                            return (
                                                <div
                                                    className={
                                                        styles["record-card"]
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
                                                        {Date(
                                                            observation.appointment_date
                                                        ).toLocaleString(
                                                            "es-AR"
                                                        )}
                                                        - Médico:{" "}
                                                        {observation.physician}
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
                                // If there are no appointments, display the message
                                <div className={styles["subtitle"]}>
                                    No hay observaciones en esta historia
                                    clinica
                                </div>
                            )}
                        </div>
                    </div>

                    <Footer />
                </>
            )}
        </div>
    );
};
export default MyRecord;