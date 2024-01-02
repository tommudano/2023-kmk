import React from "react";
import Modal from "react-modal";
import styles from "../styles/ConfirmationModal.module.css";

const ValueModal = ({
    isOpen,
    closeModal,
    confirmAction,
    message,
    currentValue,
    setNewValue,
}) => {
    return (
        <Modal
            isOpen={isOpen}
            onRequestClose={closeModal}
            contentLabel='Valor'
            className={styles.modal}
            style={{ content: { height: "250px" } }}
            overlayClassName={styles.overlay}
            ariaHideApp={false}
        >
            <h2>Asignar un valor a la especialidad</h2>
            <p className={styles.message}>{message}</p>
            <input
                type='number'
                min={1}
                placeholder={currentValue}
                onChange={(e) => setNewValue(e.target.value)}
            />
            <div className={styles["buttons-container"]}>
                <button
                    onClick={closeModal}
                    className={styles["cancel-button"]}
                >
                    Cancelar
                </button>
                <button
                    onClick={confirmAction}
                    className={styles["confirm-button"]}
                >
                    Confirmar
                </button>
            </div>
        </Modal>
    );
};

export default ValueModal;
