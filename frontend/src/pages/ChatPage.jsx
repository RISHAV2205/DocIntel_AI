import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import API from "../services/api";

function getErrorMessage(error, fallback) {
    return error.response?.data?.detail || fallback;
}

function ChatPage() {
    const [chats, setChats] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [messages, setMessages] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [isSending, setIsSending] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const navigate = useNavigate();

    async function loadDocuments() {
        try {
            const response = await API.get("/documents/");
            setDocuments(response.data);
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not load documents."));
        }
    }

    async function openChat(chatId) {
        setError("");
        try {
            const response = await API.get(`/chat/${chatId}/messages`);
            setActiveChatId(chatId);
            setMessages(response.data);
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not load messages."));
        }
    }

    async function createChat() {
        setError("");
        try {
            const response = await API.post("/chat/create", { title: "New Chat" });
            const chat = { id: response.data.chat_id, title: response.data.title };
            setChats((currentChats) => [chat, ...currentChats]);
            setActiveChatId(chat.id);
            setMessages([]);
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not create chat."));
        }
    }

    async function deleteChat(chatId) {
        if (!window.confirm("Delete this chat and all its messages?")) return;

        try {
            await API.delete(`/chat/${chatId}`);
            setChats((currentChats) => currentChats.filter((chat) => chat.id !== chatId));
            if (activeChatId === chatId) {
                setActiveChatId(null);
                setMessages([]);
            }
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not delete chat."));
        }
    }

    async function uploadDocument(event) {
        event.preventDefault();
        const form = event.currentTarget;
        const formData = new FormData(form);
        const file = formData.get("file");

        if (!(file instanceof File) || file.size === 0) {
            setError("Choose a PDF, TXT, or DOCX file first.");
            return;
        }

        setError("");
        setIsUploading(true);
        try {
            await API.post("/documents/upload", formData);
            form.reset();
            await loadDocuments();
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not upload document."));
        } finally {
            setIsUploading(false);
        }
    }

    async function deleteDocument(documentId) {
        if (!window.confirm("Delete this document?")) return;

        try {
            await API.delete(`/documents/delete-docs/${documentId}`);
            setDocuments((currentDocuments) => currentDocuments.filter((document) => document.id !== documentId));
        } catch (requestError) {
            setError(getErrorMessage(requestError, "Could not delete document."));
        }
    }

    async function sendMessage(event) {
        event.preventDefault();
        const query = message.trim();
        if (!query || !activeChatId || isSending) return;

        const temporaryId = `temporary-${Date.now()}`;
        setError("");
        setMessage("");
        setIsSending(true);
        setMessages((currentMessages) => [...currentMessages, { id: temporaryId, role: "user", content: query }]);

        try {
            const response = await API.post(`/chat/${activeChatId}/message`, { query });
            setMessages((currentMessages) => [
                ...currentMessages,
                { id: `assistant-${Date.now()}`, role: "assistant", content: response.data.response },
            ]);
        } catch (requestError) {
            setMessages((currentMessages) => currentMessages.filter((item) => item.id !== temporaryId));
            setMessage(query);
            setError(getErrorMessage(requestError, "Could not send message."));
        } finally {
            setIsSending(false);
        }
    }

    function logout() {
        localStorage.removeItem("token");
        navigate("/login");
    }

    useEffect(() => {
        let isCurrent = true;

        async function loadInitialData() {
            try {
                const [chatsResponse, documentsResponse] = await Promise.all([
                    API.get("/chat/"),
                    API.get("/documents/"),
                ]);
                if (!isCurrent) return;

                setChats(chatsResponse.data);
                setDocuments(documentsResponse.data);
            } catch (requestError) {
                if (isCurrent) {
                    setError(getErrorMessage(requestError, "Could not load your data."));
                }
            }
        }

        void loadInitialData();
        return () => {
            isCurrent = false;
        };
    }, []);

    return (
        <main className="chat-layout">
            <aside className="sidebar">
                <div className="sidebar-heading">
                    <h1>DocIntel AI</h1>
                    <button className="secondary-button" onClick={logout}>Log out</button>
                </div>

                <button onClick={createChat}>+ New chat</button>
                <section>
                    <h2>Chats</h2>
                    {chats.length === 0 && <p className="empty-state">No chats yet.</p>}
                    {chats.map((chat) => (
                        <div className="list-item" key={chat.id}>
                            <button className={activeChatId === chat.id ? "chat-button active" : "chat-button"} onClick={() => openChat(chat.id)}>{chat.title}</button>
                            <button className="delete-button" aria-label={`Delete ${chat.title}`} onClick={() => deleteChat(chat.id)}>Delete</button>
                        </div>
                    ))}
                </section>

                <section>
                    <h2>Documents</h2>
                    <form className="upload-form" onSubmit={uploadDocument}>
                        <input name="file" type="file" accept=".pdf,.txt,.docx" required />
                        <button type="submit" disabled={isUploading}>{isUploading ? "Uploading..." : "Upload"}</button>
                    </form>
                    {documents.length === 0 && <p className="empty-state">No documents uploaded.</p>}
                    {documents.map((document) => (
                        <div className="list-item" key={document.id}>
                            <span>{document.filename} <small>({document.status})</small></span>
                            <button className="delete-button" onClick={() => deleteDocument(document.id)}>Delete</button>
                        </div>
                    ))}
                </section>
            </aside>

            <section className="conversation">
                <h2>{activeChatId ? "Chat" : "Create or select a chat"}</h2>
                {error && <p className="error-message">{error}</p>}
                <div className="messages">
                    {activeChatId && messages.length === 0 && <p className="empty-state">Ask a question about your uploaded documents.</p>}
                    {messages.map((item, index) => (
                        <article className={`message ${item.role}`} key={item.id || index}>
                            <strong>{item.role === "user" ? "You" : "Assistant"}</strong>
                            <p>{item.content}</p>
                        </article>
                    ))}
                </div>
                <form className="message-form" onSubmit={sendMessage}>
                    <textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder={activeChatId ? "Ask about your documents..." : "Create or select a chat first."} disabled={!activeChatId || isSending} />
                    <button type="submit" disabled={!activeChatId || !message.trim() || isSending}>{isSending ? "Sending..." : "Send"}</button>
                </form>
            </section>
        </main>
    );
}

export default ChatPage;
