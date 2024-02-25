"use client";

import React, { useState, useEffect } from "react";
import Image from "next/image";
import styles from "../styles/styles.module.css";
import { useRouter } from "next/navigation";
import axios from "axios";
import https from "https";
import ConfirmationModal from "../components/ConfirmationModal";
import { Header, Footer, AdminTabBar } from "../components/header";
import { toast } from "react-toastify";
import { userCheck } from "../components/userCheck";
import ValueModal from "../components/ValueModal";
import InfoIcon from "@mui/icons-material/Info";
import IconButton from "@mui/material/IconButton";
import Tooltip from "@mui/material/Tooltip";

const Admin = () => {
    const [isLoading, setIsLoading] = useState(true);
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    const router = useRouter();
    const [firstLoad, setFirstLoad] = useState(true);
    const [specialties, setSpecialties] = useState([]);
    const [newSpecialty, setNewSpecialty] = useState("");
    const [showModal, setShowModal] = useState(false);
    const [selectedSpecialty, setSelectedSpecialty] = useState("");
    const [showValueModal, setShowValueModal] = useState(false);
    const [newValue, setNewValue] = useState(3000);
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

    const handleValueUpdate = (specialty) => {
        setSelectedSpecialty(specialty);
        setShowValueModal(true);
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

    const handleChangeValue = async () => {
        setShowValueModal(false);
        try {
            toast.info("Actualizando valor...");
            const response = await axios.put(
                `${apiURL}admin/specialties/value/${selectedSpecialty.name}`,
                { value: newValue }
            );
            console.log(response.data);
            toast.success("Valor actualizado exitosamente");
            fetchSpecialties();
        } catch (error) {
            console.error(error);
            toast.error("Error al actualizar el valor");
        }
    };

    useEffect(() => {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        userCheck(router, "admin").then(() => {
            fetchSpecialties().then(() => setIsLoading(false));
            setFirstLoad(false);
        });
    }, []);

    return (
        <div className={styles.dashboard}>
            <ValueModal
                isOpen={showValueModal}
                closeModal={() => setShowValueModal(false)}
                confirmAction={handleChangeValue}
                currentValue={selectedSpecialty.value}
                setNewValue={setNewValue}
                title={"Asignar un valor a la especialidad"}
                message={`¿Cual es el nuevo valor de la especialidad ${selectedSpecialty.name}?`}
                aclaration='Se le informara a todos los medicos de la especialidad del cambio'
            />

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

            <AdminTabBar highlight='Especialidades' />

            <Header role='admin' />
            {isLoading ? (
                <p>Cargando...</p>
            ) : (
                <>
                    <div className={styles["tab-content"]}>
                        <div className={styles.form}>
                            <div className={styles["title"]}>
                                Especialidades
                                <Tooltip
                                    title='Al crear una especialidad, esta se crea con un valor de $3000. Desde la lista podes editar este valor una vez creada la especialidad.'
                                    placement='right'
                                >
                                    <IconButton>
                                        <InfoIcon />
                                    </IconButton>
                                </Tooltip>
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
                                                        src='/money_icon.png'
                                                        alt='borrar'
                                                        className={styles.logo}
                                                        style={{
                                                            marginRight: "15px",
                                                        }}
                                                        width={25}
                                                        height={25}
                                                        onClick={() => {
                                                            handleValueUpdate(
                                                                specialty
                                                            );
                                                        }}
                                                    />
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
                    </div>
                    <Footer />
                </>
            )}
        </div>
    );
};

export default Admin;
