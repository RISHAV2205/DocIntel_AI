import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import API from "../services/api";

function Register() {
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
            await API.post("/users/", { email, password });
            navigate("/login", { state: { message: "Account created. Please log in." } });
        } catch (requestError) {
            setError(requestError.response?.data?.detail || "Registration failed.");
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <main className="auth-page">
            <form className="auth-card" onSubmit={handleSubmit}>
                <h1>Create account</h1>
                <p>Register to create chats and upload documents.</p>
                {error && <p className="error-message">{error}</p>}
                <label htmlFor="register-email">Email</label>
                <input id="register-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
                <label htmlFor="register-password">Password</label>
                <input id="register-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required minLength="6" />
                <button type="submit" disabled={isSubmitting}>{isSubmitting ? "Creating..." : "Register"}</button>
                <p>Already registered? <Link to="/login">Log in</Link></p>
            </form>
        </main>
    );
}

export default Register;
