import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import ChatPage from "./pages/ChatPage";
import Login from "./pages/Login";
import Register from "./pages/Register";

function ProtectedRoute({ children }) {
    return localStorage.getItem("token")
        ? children
        : <Navigate to="/login" replace />;
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Navigate to="/chat" replace />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route
                    path="/chat"
                    element={(
                        <ProtectedRoute>
                            <ChatPage />
                        </ProtectedRoute>
                    )}
                />
                <Route path="*" element={<Navigate to="/chat" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
