import { useState } from "react";
import API from "../services/api";

function Login() {

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    const handleLogin = async () => {

        try {

            const formData = new URLSearchParams();

            formData.append("username", email);
            formData.append("password", password);

            console.log(formData.toString());

            const response = await API.post(
                "/login",
                formData.toString(),
                {
                    headers: {
                        "Content-Type":
                        "application/x-www-form-urlencoded"
                    }
                }
            );

            console.log(response.data);

            localStorage.setItem(
                "token",
                response.data.access_token
            );

            alert("Login Successful");

        } catch (error) {

    console.log("FULL ERROR:");
    console.log(error);

    console.log("RESPONSE DATA:");
    console.log(error.response.data);

    console.log("DETAIL:");
    console.log(error.response.data.detail);

    alert("Login Failed");
}
    };

    return (
        <div>

            <h1>Login</h1>

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

            <button onClick={handleLogin}>
                Login
            </button>

        </div>
    );
}

export default Login;