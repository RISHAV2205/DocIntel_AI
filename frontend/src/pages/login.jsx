import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import API from "../services/api";

function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const navigate = useNavigate();

    async function handleSubmit(event) {
        event.preventDefault();
        setError("");
        setIsSubmitting(true);

        try {
            const formData = new URLSearchParams({
                username: email,
                password,
            });
            const response = await API.post("/login", formData, {
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
            });
            localStorage.setItem("token", response.data.access_token);
            navigate("/chat");
        } catch (requestError) {
            setError(requestError.response?.data?.detail || "Login failed.");
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="auth-page">
            <form className="auth-card" onSubmit={handleSubmit}>
                <h1>Document Chat</h1>
                <p>Log in to chat with your documents.</p>
                {error && <p className="error-message">{error}</p>}
                <label htmlFor="login-email">Email</label>
                <input id="login-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
                <label htmlFor="login-password">Password</label>
                <input id="login-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
                <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Logging in..." : "Log in"}</button>
                <p>New here? <Link to="/register">Create an account</Link></p>
            </form>
        </main>
    );
}

export default Login;
