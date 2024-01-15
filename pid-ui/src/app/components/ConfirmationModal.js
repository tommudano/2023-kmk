import React from "react";
import Modal from "react-modal";
import styles from "../styles/ConfirmationModal.module.css";

const ConfirmationModal = ({ isOpen, closeModal, confirmAction, message }) => {
    return (
        <Modal
            isOpen={isOpen}
            onRequestClose={closeModal}
            contentLabel='Confirmación'
            className={styles.modal}
            overlayClassName={styles.overlay}
            ariaHideApp={false}
        >
            <h2>Confirmación</h2>
            <p className={styles.message}>{message}</p>
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

export default ConfirmationModal;
