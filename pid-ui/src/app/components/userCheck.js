import axios from "axios";
import https from "https";
import { toast } from "react-toastify";

const agent = new https.Agent({
    rejectUnauthorized: false,
});

const registerCheck = async (router) => {
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    try {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        const response = await axios.get(`${apiURL}users/role`, {
            httpsAgent: agent,
        });
        if (response.status == 200) {
            switch (response.data.roles[0]) {
                case "admin":
                    router.replace("/admin-specialties");
                    break;
                case "physician":
                    router.replace("/physician-agenda");
                    break;
                case "patient":
                    router.replace("/patient-dashboard");
                    break;
                default:
                    router.replace("/registro");
                    break;
            }
        } else {
            router.replace("/registro");
        }
    } catch (error) {
        router.replace("/registro");
    }
};

const loginCheck = async (router) => {
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    try {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        const response = await axios.get(`${apiURL}users/role`, {
            httpsAgent: agent,
        });
        if (response.status == 200) {
            console.log(response.data.roles);
            switch (response.data.roles[0]) {
                case "admin":
                    router.replace("/admin-specialties");
                    break;
                case "physician":
                    router.replace("/physician-agenda");
                    break;
                case "patient":
                    router.replace("/patient-dashboard");
                    break;

                default:
                    router.replace("/");
                    break;
            }
        } else {
            router.replace("/");
        }
    } catch (error) {
        console.error(error);
        if (error.response && error.response.data) {
            switch (error.response.data.detail) {
                case "User must be logged in":
                    router.replace("/");
                    break;
                case "Account has to be approved by admin":
                    toast.error(
                        <div>
                            Aprobacion pendiente <br /> Contacte al
                            administrador
                        </div>
                    );
                    break;
                case "Account is not approved":
                    toast.error(
                        <div>
                            Cuenta denegada <br /> Contacte al administrador
                        </div>
                    );
                    break;
            }
        } else router.replace("/");
    }
};

const redirect = async (router) => {
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    try {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        const response = await axios.get(`${apiURL}users/role`, {
            httpsAgent: agent,
        });
        if (response.status == 200) {
            switch (response.data.roles[0]) {
                case "admin":
                    router.replace("/admin-specialties");
                    break;
                case "physician":
                    router.replace("/physician-agenda");
                    break;
                case "patient":
                    router.replace("/patient-dashboard");
                    break;
                default:
                    router.replace("/");
                    break;
            }
        } else router.replace("/");
    } catch (error) {
        console.error(error);

        if (error.response && error.response.data) {
            switch (error.response.data.detail) {
                case "User must be logged in":
                    router.replace("/");
                    break;
            }
        }
    }
};

const userCheck = async (router, role) => {
    const apiURL = process.env.NEXT_PUBLIC_API_URL;
    try {
        axios.defaults.headers.common = {
            Authorization: `bearer ${localStorage.getItem("token")}`,
        };
        const response = await axios.get(`${apiURL}users/role`, {
            httpsAgent: agent,
        });

        if (response.status == 200) {
            if (response.data.roles[0] != role) {
                axios.defaults.headers.common = {
                    Authorization: `bearer `,
                };
                localStorage.clear();
                router.replace("/");
            }
        } else router.replace("/");
    } catch (error) {
        console.error(error);

        if (error.response && error.response.data) {
            switch (error.response.data.detail) {
                case "User must be logged in":
                    router.replace("/");
                    break;
            }
        } else router.replace("/");
    }
};

export { loginCheck, redirect, userCheck, registerCheck };
