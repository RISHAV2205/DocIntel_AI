import { useState } from "react";
import API from "../services/api";

function Register() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleRegister = async () => {

        try {

            const response = await API.post(
                "/users",
                {
                    email: email,
                    password: password
                }
            );

            console.log(response.data);

            alert("Registration Successful");

        } catch (error) {

            console.log(error.response.data);

            alert("Registration Failed");
        }
    };

    return (
        <div>

            <h1>Register</h1>

            <input
                type="email"
                placeholder="Enter Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
            />

            <br /><br />

            <input
                type="password"
                placeholder="Enter Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            <br /><br />

            <button onClick={handleRegister}>
                Register
            </button>

        </div>
    );
}

export default Register;