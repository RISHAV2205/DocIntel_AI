// Import axios
import axios from "axios";


// ========================================
// CREATE AXIOS INSTANCE
// ========================================

// This creates a reusable axios object
// with backend base URL

const API = axios.create({

    baseURL: "http://127.0.0.1:8000"

});


// ========================================
// REQUEST INTERCEPTOR
// ========================================

// This automatically adds JWT token
// in every request header

API.interceptors.request.use(

    (req) => {

        // Get token from localStorage

        const token = localStorage.getItem("token");

        console.log("TOKEN:", token);

        // If token exists
        // add Authorization header

        if (token) {

            req.headers.Authorization =
                `Bearer ${token}`;
        }

        console.log(req.headers);

        return req;
    },

    // Handle request errors

    (error) => {

        return Promise.reject(error);
    }
);


// ========================================
// RESPONSE INTERCEPTOR (OPTIONAL)
// ========================================

// This helps handling expired token,
// unauthorized access, etc.

API.interceptors.response.use(

    // Successful response

    (response) => {

        return response;
    },

    // Error response

    (error) => {

        // If token expired or invalid

        if (error.response?.status === 401) {

            console.log("Unauthorized Access");

            // Remove invalid token

            localStorage.removeItem("token");

            // Redirect user to login page

            window.location.href = "/";
        }

        return Promise.reject(error);
    }
);


// Export API instance

export default API;