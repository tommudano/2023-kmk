import React, { useState, useEffect } from "react";
import styles from "../styles/styles.module.css";
import Modal from "react-modal";

const RatingsModal = ({ isOpen, handleCloseRatingModal, scores }) => {
    const ratingModalStyles = {
        content: {
            top: "50%",
            left: "50%",
            right: "auto",
            bottom: "auto",
            marginRight: "-50%",
            transform: "translate(-50%, -50%)",
            width: "auto",
        },
    };

    return (
        <Modal
            ariaHideApp={false}
            isOpen={isOpen}
            onRequestClose={handleCloseRatingModal}
            style={ratingModalStyles}
        >
            <div className={styles["reviews-container"]}>
                {scores.length > 0 ? (
                    <>
                        {scores.map((review) => (
                            <div key={review.id} className={styles["review"]}>
                                <div
                                    className={styles["review-cards-container"]}
                                >
                                    <div className={styles["review-card"]}>
                                        <div
                                            className={
                                                styles["review-card-title"]
                                            }
                                        >
                                            {review.type}
                                        </div>
                                        <div
                                            className={
                                                styles["review-card-content"]
                                            }
                                        >
                                            {review.rating}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </>
                ) : (
                    <label>No hay puntuaciones</label>
                )}
            </div>

            <button
                className={styles["standard-button"]}
                onClick={() => handleCloseRatingModal()}
            >
                Cerrar
            </button>
        </Modal>
    );
};

export default RatingsModal;
