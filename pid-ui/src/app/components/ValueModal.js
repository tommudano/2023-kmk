import React from "react";
import Modal from "react-modal";
import styles from "../styles/ConfirmationModal.module.css";

const ValueModal = ({
    isOpen,
    closeModal,
    confirmAction,
    message,
    currentValue,
    title,
    setNewValue,
    aclaration,
}) => {
    return (
        <Modal
            isOpen={isOpen}
            onRequestClose={closeModal}
            contentLabel='Valor'
            className={styles.modal}
            style={{ content: { height: "300px" } }}
            overlayClassName={styles.overlay}
            ariaHideApp={false}
        >
            <h2>{title}</h2>
            <p className={styles.message}>{message}</p>
            <p className={styles.aclaration}>({aclaration})</p>
            <input
                type='number'
                min={1}
                placeholder={`\$${currentValue}`}
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
