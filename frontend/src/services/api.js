// import axios from "axios";

// const API = axios.create({
//     baseURL: "http://127.0.0.1:8000"
// });

// export default API;


import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

API.interceptors.request.use((req) => {

    const token = localStorage.getItem("token");

    console.log("TOKEN:", token);

    if (token) {

        req.headers.Authorization =
            `Bearer ${token}`;

        console.log(req.headers);
    }

    return req;
});

export default API;