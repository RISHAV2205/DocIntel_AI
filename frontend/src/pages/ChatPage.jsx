import { useState } from "react";
import API from "../services/api";

function ChatPage() {
    const [chatId, setChatId] = useState("");
    const [message, setMessage] = useState("");
    const [response, setResponse] = useState("");
    const [file, setFile] = useState(null);

    // CREATE CHAT
    const createChat = async () => {

        try {

            const response = await API.post(
                "/chat/create/",
                {
                    title: "New Chat"
                }
            );
            console.log("CHAT ID:", response.data.chat_id);
            console.log(response.data);

            setChatId(response.data.chat_id);

            alert("Chat Created");

        } catch (error) {

            console.log(error.response?.data);

            alert("Chat Creation Failed");
        }
    };

    // UPLOAD DOCUMENT
    const uploadDocument = async () => {

        if (!file) {
            alert("Select a file first");
            return;
        }

        const formData = new FormData();

        formData.append("file", file);

        try {

            const response = await API.post(
                "/documents/upload",
                formData,
                {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }
            );

            console.log(response.data);

            alert("Document Uploaded");

        } catch (error) {

            console.log(error.response?.data);

            alert("Upload Failed");
        }
    };

    // SEND MESSAGE
    const sendMessage = async () => {

        if (!chatId) {
            alert("Create chat first");
            return;
        }

        try {

            const response = await API.post(
            `/chat/${chatId}/message`,
            {
                query: message
            }
            );

            console.log(response.data);

            setResponse(response.data.response);

        } catch (error) {

            console.log(error.response?.data);

            alert("Message Failed");
        }
    };

    return (

        <div style={{ padding: "20px" }}>

            <h1>AI Document Chat</h1>

            <hr />

            {/* CREATE CHAT */}

            <button onClick={createChat}>
                Create Chat
            </button>

            <br /><br />

            <p>Current Chat ID: {chatId}</p>

            <hr />

            {/* UPLOAD DOCUMENT */}

            <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
            />

            <button onClick={uploadDocument}>
                Upload Document
            </button>

            <hr />

            {/* MESSAGE INPUT */}

            <textarea
                rows="5"
                cols="50"
                placeholder="Ask question..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
            />

            <br /><br />

            <button onClick={sendMessage}>
                Send
            </button>

            <hr />

            {/* AI RESPONSE */}

            <h3>AI Response:</h3>

            <p>{response}</p>

        </div>
    );
}

export default ChatPage;